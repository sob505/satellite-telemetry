"""
Scikit-learn → Telemetry RAG Corpus Builder (JSONL export)

This script:
1. Fetches anomaly detection docs from scikit-learn
2. Cleans HTML into raw text
3. Chunks documents into RAG-friendly segments
4. Adds lightweight metadata + telemetry tags
5. Saves everything as JSONL for downstream embedding/ingestion
"""

import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from typing import List, Dict


# =========================================================
# SOURCE DOCUMENTS
# =========================================================

SCIKIT_DOCS = {
    "outlier_overview": "https://scikit-learn.org/stable/modules/outlier_detection.html",
    "isolation_forest": "https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html",
    "lof": "https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.LocalOutlierFactor.html",
    "one_class_svm": "https://scikit-learn.org/stable/modules/generated/sklearn.svm.OneClassSVM.html",
    "comparison": "https://scikit-learn.org/stable/modules/outlier_detection.html#comparison-of-anomaly-detection-methods",
}


# =========================================================
# FETCH + CLEAN
# =========================================================

def fetch_html(url: str) -> str:
    """Download raw HTML from a URL."""
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.text


def clean_html(html: str) -> str:
    """Remove boilerplate and extract readable text."""
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    return soup.get_text(separator="\n")


# =========================================================
# CHUNKING
# =========================================================

def chunk_text(text: str, max_chars: int = 2000) -> List[str]:
    """
    Split cleaned text into manageable RAG chunks.
    """
    chunks = []
    buffer = ""

    for line in text.split("\n"):
        if len(buffer) + len(line) > max_chars:
            if buffer.strip():
                chunks.append(buffer.strip())
            buffer = line
        else:
            buffer += "\n" + line

    if buffer.strip():
        chunks.append(buffer.strip())

    return chunks


# =========================================================
# TELEMETRY TAGGING
# =========================================================

def infer_tags(source: str) -> List[str]:
    """Assign telemetry-relevant semantic tags."""
    source = source.lower()

    if "isolation" in source:
        return ["anomaly_detection", "isolation_forest", "unsupervised"]

    if "local" in source or "lof" in source:
        return ["anomaly_detection", "density_based"]

    if "svm" in source:
        return ["anomaly_detection", "boundary_method"]

    if "outlier" in source:
        return ["anomaly_detection", "overview"]

    return ["ml_reference"]


# =========================================================
# CORE PIPELINE
# =========================================================

def build_rag_docs() -> List[Dict]:
    """
    Convert scikit-learn docs into structured RAG records.
    """
    docs = []

    for name, url in SCIKIT_DOCS.items():
        print(f"Processing: {name}")

        try:
            html = fetch_html(url)
            text = clean_html(html)
            chunks = chunk_text(text)

            for i, chunk in enumerate(chunks):

                if len(chunk.strip()) < 100:
                    continue

                docs.append({
                    "id": f"{name}_{i}",
                    "text": chunk,
                    "source": name,
                    "url": url,
                    "chunk_index": i,
                    "tags": infer_tags(name),
                })

        except Exception as e:
            print(f"Failed {name}: {e}")

    return docs


# =========================================================
# SAVE AS JSONL
# =========================================================

def save_jsonl(docs: List[Dict], output_path: str):
    """
    Save RAG corpus in JSONL format (recommended for vector pipelines).
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        for doc in docs:
            f.write(json.dumps(doc) + "\n")

    print(f"Saved {len(docs)} documents → {output_path}")


# =========================================================
# MAIN ENTRY
# =========================================================

def main():
    print("Building scikit-learn telemetry RAG corpus...")

    docs = build_rag_docs()

    print(f"Generated {len(docs)} RAG chunks")

    save_jsonl(
        docs,
        "data/scikit_corpus.jsonl"
    )

    print("Done.")


if __name__ == "__main__":
    main()