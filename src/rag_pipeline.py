"""
Satellite Telemetry RAG Pipeline (No LangChain, No NumPy)
Enhanced with Code Generation Support
"""

import os
import json
import re
from typing import List, Dict
from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer
import requests

load_dotenv()

class SimpleRAG:
    def __init__(self, model_name: str = "phi"):
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

        self.output = f"Initialized RAG pipeline with model: {model_name}\n"

    def ingest_telemetry_data(self, file_path: str):
        """Ingest satellite telemetry data from a file."""
        self.output += f"Ingesting telemetry data from: {file_path}\n"
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
                self.output += f"Error processing chunk {i}: {e}\n"

        self.output += f"✓ Ingested {len(chunks)} chunks from {file_path}\n"

    def query(self, question: str, top_k: int = 4, code_generation: bool = False) -> Dict:
        """
        Query the RAG pipeline.

        Args:
            question: The query question
            top_k: Number of top results to retrieve
            code_generation: If True, request code as output instead of natural language

        Returns:
            Dictionary with 'result' and 'source_documents'
        """
        self.output += f"Generating code for task: {question}\n"
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
                "source_documents": [],
                "code": None
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
                "source_documents": [],
                "code": None
            }

        # Query Ollama for answer
        if code_generation:
            answer, code = self._query_ollama_for_code(question, context)
        else:
            answer = self._query_ollama(question, context)
            code = None

        return {
            "result": answer,
            "source_documents": source_docs,
            "code": code
        }

    def _query_ollama(self, question: str, context: str) -> str:
        """Query Ollama for a natural language answer based on context."""
        # Load the prompt from text file
        with open('query_prompt.txt','r') as file:
            prompt_template = file.read()

        prompt = prompt_template.format(context=context, question=question)
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=300
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

    def _query_ollama_for_code(self, question: str, context: str) -> tuple:
        """
        Query Ollama for code generation based on context.

        Returns:
            Tuple of (explanation, code_string)
        """

        # Load the prompt from text file
        with open('coding_prompt.txt','r') as file:
            prompt_template = file.read()
        # Format prompt with context and question
        prompt = prompt_template.format(context=context, question=question)

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=300
            )

            if response.status_code == 200:
                data = response.json()
                full_response = data.get("response", "No response from model")

                # Parse the response to extract explanation and code
                explanation, code = self._parse_code_response(full_response)
                return explanation, code
            else:
                return f"Error from Ollama: {response.status_code}", None
        except requests.ConnectionError:
            return f"Cannot connect to Ollama at {self.ollama_url}. Is it running? (ollama serve)", None
        except Exception as e:
            return f"Error querying Ollama: {e}", None

    def _parse_code_response(self, response: str) -> tuple:
        """
        Parse the code generation response to extract explanation and code.

        Args:
            response: The full response from the LLM

        Returns:
            Tuple of (explanation, code_string)
        """
        explanation = ""
        code = ""

        # Try to extract explanation
        if "EXPLANATION:" in response:
            exp_start = response.find("EXPLANATION:") + len("EXPLANATION:")
            exp_end = response.find("CODE:") if "CODE:" in response else len(response)
            explanation = response[exp_start:exp_end].strip()

        # Try to extract code from markdown code block
        if "```python" in response:
            code_start = response.find("```python") + len("```python")
            code_end = response.find("```", code_start)
            if code_end != -1:
                code = response[code_start:code_end].strip()
            else:
                code = response[code_start:].strip()
        elif "CODE:" in response:
            code_start = response.find("CODE:") + len("CODE:")
            code = code_start.strip()

        return explanation, code

    def batch_query(self, questions: List[str], code_generation: bool = False) -> List[dict]:
        """Process multiple queries."""
        results = []
        for question in questions:
            result = self.query(question, code_generation=code_generation)
            results.append({
                "question": question,
                "answer": result["result"],
                "code": result.get("code"),
                "sources": result["source_documents"]
            })
        return results

    def list_ingested_documents(self) -> List[str]:
        """
        List all documents currently ingested in the vector store.

        Returns:
            A list of document contents.
        """
        try:
            # Retrieve all documents from the collection
            results = self.collection.get()
            return results.get('documents', [])
        except Exception as e:
            self.output += f"Error retrieving documents: {e}\n"
            return []

    def clear_ingested_documents(self) -> None:
        """
        Clear all documents currently ingested in the vector store.
        """
        try:
            # Retrieve all document IDs
            all_ids = self.collection.get().get('ids', [])
            if all_ids:
                # Delete documents by their IDs
                self.collection.delete(ids=all_ids)
                self.output += "✓ All ingested documents have been cleared.\n"
            else:
                self.output += "No documents to clear.\n"
        except Exception as e:
            self.output += f"Error clearing documents: {e}\n"