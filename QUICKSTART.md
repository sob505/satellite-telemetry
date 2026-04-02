# 🚀 Quick Start Guide

## Installation (One Command)

```bash
pip install -r requirements.txt
```

This installs all dependencies with pre-built wheels - no compilation, works on 32-bit and 64-bit Windows.

## Setup

1. **Make sure Ollama is running:**
   ```bash
   ollama serve
   ```
   (In a separate terminal/command prompt)

2. **Pull a model** (in another terminal):
   ```bash
   ollama pull mistral
   ```

## Test It Works

```bash
# Ingest sample data
python cli.py ingest data/sample_telemetry.csv

# Ask a question
python cli.py query "What was the maximum altitude?"

# Or interactive mode
python cli.py interactive
```

## Commands

```bash
# Ingest data
python cli.py ingest data/sample_telemetry.csv

# Ask single question
python cli.py query "Your question here"

# Interactive Q&A
python cli.py interactive
```

## Project Structure

```
satellite-telemetry-rag/
├── cli.py                      # Command-line interface
├── requirements.txt            # Python dependencies
├── src/
│   └── rag_pipeline.py        # Core RAG system
├── data/
│   ├── sample_telemetry.csv   # Sample data to get started
│   └── chroma_db/             # Vector database (created on first run)
└── README.md                  # Full documentation
```

## Python Usage

```python
from src.rag_pipeline import SimpleRAG

# Initialize
rag = SimpleRAG(model_name="mistral")

# Ingest data
rag.ingest_telemetry_data("data/sample_telemetry.csv")

# Query
result = rag.query("What was happening with the satellite?")
print(result['result'])

# Batch query
questions = ["Q1?", "Q2?", "Q3?"]
results = rag.batch_query(questions)
for r in results:
    print(f"{r['question']}: {r['answer']}")
```

## Troubleshooting

**"Cannot connect to Ollama"**
- Make sure `ollama serve` is running
- Check it's on port 11434: `curl http://localhost:11434/api/tags`

**"Port 11434 already in use"**
- Ollama is already running (that's good!)
- Just skip the `ollama serve` step

**"No data found" when querying**
- Ingest data first: `python cli.py ingest data/sample_telemetry.csv`

## Features

✅ Works on Windows 32-bit and 64-bit
✅ No build tools needed
✅ Local LLM (Mistral, Llama2, etc.)
✅ Fast vector search with Chroma
✅ Semantic embeddings with Sentence Transformers
✅ Simple Python API + CLI

## Next Steps

1. Add your own satellite telemetry data (CSV format)
2. Customize questions for your use case
3. Experiment with different Ollama models
4. Integrate into your workflow

Happy analyzing! 🛰️
