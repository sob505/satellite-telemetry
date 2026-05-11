# satellite-telemetry
This project implements a Retrieval-Augmented Generation (RAG) system for satellite telemetry data using an Ollama model. 
It includes a command-line interface and a GUI for interactive querying, as well as scripts for preprocessing data from
the ESA Anomaly Detection Dataset, Mission 1. 

Disclaimer: The writing of this document, as well as the frameworks of several scripts and comments in the codebase, was assisted by 
generative AI.

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

## Project Structure

```
satellite-telemetry-rag/
├── gui.py                      # Start here to run GUI interface
├── requirements.txt            # Python dependencies
├── data/
│   ├── parquet/                # Parquet files (created by convert_to_parquet.py)
│   ├── chroma_db/              # Vector database (created on first run)
│   └── channels.csv            # Sample satellite telemetry data from ESA Dataset
│   └── scikit_corpus.json      # Sample text data from scikit-learn (created by get_scikitlearn.py)
│   └── summary.md              # Markdown summary of data (created by make_markdown.py)
│   └── telecommands.csv        # Sample satellite telemetry data from ESA Dataset
├── prompts/
│   └── coding_prompt.txt       # Prompt template for coding tasks
│   └── modelfile               # File to customize model behavior
│   └── query_prompt.txt        # Prompt template for querying model
├── src/
│   └── clear_rag.py            # Utility to clear RAG database
│   └── cli.py                  # Command-line interface
│   └── convert_to_parquet.py   # Utility to convert CSV to Parquet
│   └── get_scikitlearn.py      # Utility to fetch scikit-learn dataset
│   └── make_markdown.py        # Utility to create Markdown files for RAG
│   └── rag_pipeline.py         # Main RAG pipeline implementation
│   └── verify.py               # Utility to verify RAG results
└── README.md                   # Full documentation
```

## Step 4: Run the GUI
Make sure you have Ollama running (`ollama serve`) and the model pulled (`ollama pull phi`), then start the GUI:

```bash
python gui.py
```

Type in a folder to ingest the data. Example: data/parquet

Once ingested, click on the "LLM Interaction" tab at the top. Use the left text entry to input queries. Press "Generate Code"
to prompt the LLM to generate Python code. Press "Ask Question" to prompt the LLM to answer your question directly. Press
"Retry" if you would like to reuse your previous query and have the LLM re-generate the code or answer.

The conversational history will be logged in the left section, and the generated code that passes a synatx check will be 
logged in the right section.

## Troubleshooting

**"Cannot connect to Ollama"**
- Make sure `ollama serve` is running
- Check it's on port 11434: `curl http://localhost:11434/api/tags`

**"Port 11434 already in use"**
- Ollama is already running (that's good!)
- Just skip the `ollama serve` step

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
