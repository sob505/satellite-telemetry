"""
Satellite Telemetry RAG Pipeline
"""

import os
from typing import List, Dict
from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import math
from concurrent.futures import ProcessPoolExecutor, as_completed
import pandas as pd
from typing import Callable, Optional
import threading
import re
import traceback

load_dotenv()


def process_chunk(chunk, embeddings):
    """Generate embedding for a single chunk."""
    try:
        embedding = embeddings.encode(chunk)
        return {"chunk": chunk, "embedding": embedding.tolist()}
    except Exception as e:
        return {"error": f"Error processing chunk: {e}"}


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
        self.embeddings = SentenceTransformer("sentence-transformers/paraphrase-MiniLM-L3-v2")

        # Vector store path
        self.persist_directory = "data/chroma_db"
        os.makedirs(self.persist_directory, exist_ok=True)

        # Thread pool for background ingestion
        self.thread_pool = ThreadPoolExecutor(max_workers=2)

        # Initialize Chroma client
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        self.collection = self.client.get_or_create_collection(name="telemetry")

        self.output = f"Initialized RAG pipeline with model: {model_name}\n"

    def ingest_telemetry_data(self, file_path: str, source_name: str = None):
        """
        Ingest telemetry data from parquet, markdown, csv, txt, or json.
        """
        if source_name is None:
            source_name = os.path.basename(file_path)

        self.output += f"Ingesting telemetry data from: {file_path}\n"

        ext = os.path.splitext(file_path)[1].lower()

        chunks = []
        chunk_indices = []

        try:

            # =========================
            # PARQUET
            # =========================
            if ext == ".parquet":
                df = pd.read_parquet(file_path)

                # Dynamic chunk sizing
                file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                rows_per_chunk = max(500, int(file_size_mb * 2))

                for i in range(0, len(df), rows_per_chunk):
                    chunk_df = df.iloc[i:i + rows_per_chunk]
                    chunk_text = chunk_df.to_string()[:512]  # Limit to 512 chars

                    if chunk_text.strip():
                        chunks.append(chunk_text)
                        chunk_indices.append(i // rows_per_chunk)

            # =========================
            # TEXT FILES
            # =========================
            else:

                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                lines = content.splitlines()

                chunk_size = max(10, math.ceil(len(lines) / 100))

                for i in range(0, len(lines), chunk_size):

                    chunk_text = "\n".join(
                        lines[i:i + chunk_size]
                    ).strip()

                    if chunk_text:
                        chunks.append(chunk_text)
                        chunk_indices.append(i // chunk_size)

        except Exception as e:
            self.output += f"Error loading file: {e}\n"
            return

        # =========================
        # EMBEDDINGS
        # =========================

        results = []

        embeddings = self.embeddings.encode(
            chunks,
            batch_size=32,
            show_progress_bar=False,
            normalize_embeddings=True
        )

        results = [
            {"chunk": chunk, "embedding": emb.tolist()}
            for chunk, emb in zip(chunks, embeddings)
        ]

        # =========================
        # STORE IN CHROMA
        # =========================

        try:

            self.collection.add(
                ids=[
                    f"{source_name}_chunk_{i}"
                    for i in range(len(results))
                ],

                documents=[
                    res["chunk"]
                    for res in results
                ],

                embeddings=[
                    res["embedding"]
                    for res in results
                ],

                metadatas=[
                    {
                        "source": source_name,
                        "chunk_index": chunk_indices[i],
                        "file_path": str(file_path),
                        "format": ext.replace(".", "")
                    }
                    for i in range(len(results))
                ]
            )

            self.output += f"✓ Ingested {len(results)} chunks from {source_name}\n"

        except Exception as e:

            self.output += f"Error during batch write: {e}\n"

    def ingest_telemetry_data_async(
            self,
            file_path: str,
            source_name: str = None,
            progress_callback: Optional[Callable[[str], None]] = None
    ):
        """Ingest telemetry data asynchronously (non-blocking)."""
        def _worker():
            self.ingest_telemetry_data(file_path, source_name)
            if progress_callback:
                progress_callback("✓ Ingestion complete")

        self.thread_pool.submit(_worker)

    def query(
            self,
            question: str,
            top_k: int = 4,
            code_generation: bool = False,
            progress_callback: Optional[Callable[[str], None]] = None
    ) -> Dict:

        def log(msg: str):
            self.output += msg + "\n"
            if progress_callback:
                progress_callback(msg)

        log(f"Querying: {question}")

        # =========================
        # VECTOR SEARCH
        # =========================
        try:
            question_embedding = self.embeddings.encode(question)

            results = self.collection.query(
                query_embeddings=[question_embedding.tolist()],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )

        except Exception as e:
            log(f"Vector search error: {e}")
            return {"result": str(e), "source_documents": [], "code": None}

        if (
                not results
                or not results.get("documents")
                or not results["documents"][0]
        ):
            documents = results["documents"][0]
            metadatas = results["metadatas"][0]

        # =========================
        # BUILD CONTEXT
        # =========================
        context = ""
        source_docs = []

        for i, doc in enumerate(documents):
            metadata = metadatas[i] if i < len(metadatas) else {} or {}

            source_file = metadata.get("source", "Unknown")
            chunk_index = metadata.get("chunk_index", "N/A")

            context += f"[Source: {source_file}]\n{doc}\n\n"

            source_docs.append({
                "content": doc,
                "source": source_file,
                "chunk_index": chunk_index
            })

        log(f"Retrieved {len(source_docs)} chunks.")

        # =========================
        # ROUTING
        # =========================
        if code_generation:
            log("Routing → CODE generation")
            answer, code = self._query_ollama_for_code(
                question,
                context,
                progress_callback=progress_callback
            )
        else:
            log("Routing → TEXT QA")
            answer = self._query_ollama(question, context)
            code = None

        log("Query complete.")

        return {
            "result": answer,
            "source_documents": source_docs,
            "code": code
        }

    def _query_ollama(self, question: str, context: str) -> str:
        """Simple QA model call (no retry logic, no parsing)."""
        with open("prompts/query_prompt.txt", "r") as f:
            prompt_template = f.read()

        prompt = prompt_template.format(context=context, question=question)
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=300
            )

            if response.status_code != 200:
                return f"Error: {response.status_code}"
            return response.json().get("response", "No response")
        except Exception as e:
            return f"Error querying model: {e}"

    def _query_ollama_for_code(
            self,
            question: str,
            context: str,
            progress_callback: Optional[Callable[[str], None]] = None
    ) -> tuple:

        def log(msg: str):
            self.output += msg + "\n"
            if progress_callback:
                progress_callback(msg)

        MAX_RETRIES = 2

        try:
            with open("prompts/coding_prompt.txt", "r") as f:
                base_prompt = f.read()
        except FileNotFoundError:
            return "Missing coding prompt", None

        prompt = base_prompt.format(context=context, question=question)

        for attempt in range(MAX_RETRIES + 1):

            log(f"Generating code (attempt {attempt + 1})")

            try:
                response = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.2
                        }
                    },
                    timeout=300
                )

                if response.status_code != 200:
                    continue

                raw = response.json().get("response", "")

                explanation, code = self._parse_code_response(raw)

                if not code:
                    log("No code extracted, retrying...")
                    continue

                # Syntax check
                try:
                    compile(code, "<string>", "exec")
                    log("Code validation passed.")
                    return explanation, code

                except Exception:
                    error_msg = traceback.format_exc()
                    log("Syntax error detected:")
                    log(error_msg)
                    log("Retrying with error feedback...")

                    prompt = f"""
You previously generated invalid Python code.

ERROR:
{error_msg}

BROKEN CODE:
{code}

Rewrite the code so it is syntactically correct.

You MUST follow this format exactly:

EXPLANATION:
<brief explanation>

CODE:
```python
<valid python code only>

RULES:

Return valid Python only
Keep code short
No comments
No markdown outside CODE block
Ensure code compiles successfully
"""
            except Exception as e:
                log(f"LLM error: {e}")

        return "Failed to generate valid code", None

    def _parse_code_response(self, response: str) -> tuple:
        """
        Parse STRICT format:
        EXPLANATION:
        ...
        CODE:
        ...
        """

        explanation = ""
        code = ""

        # =========================
        # Extract EXPLANATION
        if "EXPLANATION:" in response and "CODE:" in response:
            explanation = (
                response.split("EXPLANATION:")[1]
                .split("CODE:")[0]
                .strip()
            )

            code = response.split("CODE:")[1].strip()

        # =========================
        # Fallback: no structure
        else:
            explanation = response.strip()

        # =========================
        # Cleanup safety
        code = code.replace("```python", "")
        code = code.replace("```", "")
        code = code.replace("\u00a0", " ").strip()

        return explanation, code

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

    def list_sources(self) -> List[str]:
        """List all source files currently ingested."""
        try:
            results = self.collection.get(include=["metadatas"])
            sources = set()
            for metadata_list in results.get('metadatas', []):
                if isinstance(metadata_list, dict):
                    sources.add(metadata_list.get('source', 'Unknown'))
            return sorted(list(sources))
        except Exception as e:
            self.output += f"Error listing sources: {e}\n"
            return []

    def shutdown(self):
        """Shut down thread pool."""
        self.thread_pool.shutdown(wait=True)