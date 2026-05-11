# 🚀 Quick Start Guide

## Step 0: Verify Python and pip Installation

Before installing dependencies, make sure you have Python and pip:

```bash
python --version
pip --version
```

Both should show version numbers. If you see "command not found" or "not recognized", see the **[Troubleshooting](#troubleshooting-python-and-pip)** section below.

---

## Step 1: Create Virtual Environment

A virtual environment isolates your project dependencies from your system Python.

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

✅ You should see `(venv)` appear in your terminal prompt.

---

## Step 2: Install Dependencies

With venv activated, install all required packages:

```bash
pip install -r requirements.txt
```

This installs all dependencies with pre-built wheels - no compilation, works on 32-bit and 64-bit Windows.

## Step 3: Set Up Ollama

1. **Download and install Ollama** from https://ollama.ai/download

2. **Start Ollama server** (in a separate terminal/command prompt):
   ```bash
   ollama serve
   ```

3. **Pull a model** (in yet another terminal, while Ollama is running):
   ```bash
   ollama pull phi
   ```

   (This downloads ~4GB, takes 5-10 minutes. You only do this once.)

## Step 4: Test It Works

Make sure you still have the venv activated (you should see `(venv)` in your prompt).

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
rag = SimpleRAG(model_name="phi")

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

---

## Troubleshooting: Python and pip

### **Python is not installed**

**Windows:**
1. Download Python from https://www.python.org/downloads/
2. Run the installer
3. ⚠️ **IMPORTANT**: Check "Add Python to PATH" during installation
4. Restart your terminal and try again

**Mac:**
```bash
# Install with Homebrew
brew install python3
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### **Python is installed but pip is not**

**Windows:**
```bash
# Download get-pip.py
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

# Run it
python get-pip.py
```

**Mac/Linux:**
```bash
python3 -m ensurepip --upgrade
```

### **Python works but can't create venv**

**Windows:**
```bash
# Some Python installations don't include venv by default
# Try using pip to install it
pip install virtualenv

# Then create venv with virtualenv instead
virtualenv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
sudo apt install python3-venv
# or
brew install python3-venv
```

### **"venv\Scripts\activate" doesn't work on Mac/Linux**

Make sure you're using the correct activation command for your OS:

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### **"pip install" says "Access denied" or "Permission denied"**

Don't use `sudo` with pip! Instead, ensure venv is activated:

```bash
# Check venv is active (should show (venv) in prompt)
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Now install
pip install -r requirements.txt
```

### **"ModuleNotFoundError" when running cli.py**

Your virtual environment isn't activated. Run:

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

---

## Deactivating venv

When you're done, deactivate the virtual environment:

```bash
deactivate
```

The `(venv)` prompt indicator disappears. To use the project again, just activate it again.

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
