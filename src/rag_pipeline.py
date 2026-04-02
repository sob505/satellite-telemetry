"""
Satellite Telemetry RAG Pipeline (No LangChain, No NumPy)
Simplified version for Windows 32-bit compatibility
"""

import os
from typing import List, Dict
from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer
import requests

load_dotenv()

class SimpleRAG:
    def __init__(self, model_name: str = "mistral"):
        """
        Initialize the RAG pipeline.
        
        Args:
            model_name: Name of the local Ollama model to use
        """
        self.model_name = model_name
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        # Initialize embeddings
        self.embeddings = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Vector store path
        self.persist_directory = "data/chroma_db"
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize Chroma client
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        self.collection = self.client.get_or_create_collection(name="telemetry")
        
    def ingest_telemetry_data(self, file_path: str):
        """Ingest satellite telemetry data from a file."""
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Simple chunking by lines
        lines = content.split('\n')
        chunks = []
        chunk_size = 10
        
        for i in range(0, len(lines), chunk_size):
            chunk = '\n'.join(lines[i:i+chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        # Embed and store chunks
        for i, chunk in enumerate(chunks):
            try:
                embedding = self.embeddings.encode(chunk)
                self.collection.add(
                    ids=[f"chunk_{i}"],
                    documents=[chunk],
                    embeddings=[embedding.tolist()]
                )
            except Exception as e:
                print(f"Error processing chunk {i}: {e}")
        
        print(f"✓ Ingested {len(chunks)} chunks from {file_path}")
    
    def query(self, question: str, top_k: int = 4) -> Dict:
        """Query the RAG pipeline."""
        # Embed the question
        question_embedding = self.embeddings.encode(question)
        
        # Search in vector store
        try:
            results = self.collection.query(
                query_embeddings=[question_embedding.tolist()],
                n_results=top_k
            )
        except Exception as e:
            return {
                "result": f"Error querying vector store: {e}",
                "source_documents": []
            }
        
        # Build context from retrieved documents
        context = ""
        source_docs = []
        
        if results and results['documents'] and len(results['documents']) > 0:
            for doc in results['documents'][0]:
                context += doc + "\n"
                source_docs.append({"content": doc})
        
        if not context:
            return {
                "result": "No relevant telemetry data found. Please ingest data first with: python cli.py ingest data/sample_telemetry.csv",
                "source_documents": []
            }
        
        # Query Ollama for answer
        answer = self._query_ollama(question, context)
        
        return {
            "result": answer,
            "source_documents": source_docs
        }
    
    def _query_ollama(self, question: str, context: str) -> str:
        """Query Ollama for an answer based on context."""
        prompt = f"""Based on the following satellite telemetry data, answer the question.

Context:
{context}

Question: {question}

Answer:"""
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=180
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "No response from model")
            else:
                return f"Error from Ollama: {response.status_code}"
        except requests.ConnectionError:
            return f"Cannot connect to Ollama at {self.ollama_url}. Is it running? (ollama serve)"
        except Exception as e:
            return f"Error querying Ollama: {e}"
    
    def batch_query(self, questions: List[str]) -> List[dict]:
        """Process multiple queries."""
        results = []
        for question in questions:
            result = self.query(question)
            results.append({
                "question": question,
                "answer": result["result"],
                "sources": result["source_documents"]
            })
        return results
