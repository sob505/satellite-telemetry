#!/usr/bin/env python
"""
Command-line interface for Satellite Telemetry RAG with Code Generation
"""

import argparse
import sys
from pathlib import Path
from src.rag_pipeline import SimpleRAG
import subprocess

# from src.telemetry_loader import TelemetryProcessor
MODEL = "phi"


def main():
    parser = argparse.ArgumentParser(
        description="Satellite Telemetry RAG System with Code Generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest telemetry data
  python cli.py ingest data/telemetry.csv
  
  # Query the RAG system (natural language)
  python cli.py query "What was the satellite altitude?"
  
  # Generate code
  python cli.py codegen "Generate Python code that determines maximum altitude"
  
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Ingest command
    ingest_parser = subparsers.add_parser('ingest', help='Ingest telemetry data')
    ingest_parser.add_argument('filepath', type=str, help='Path to telemetry file')
    ingest_parser.add_argument('--model', type=str, default=MODEL,
                               help=f'LLM model to use (default: {MODEL})')

    # Query command
    query_parser = subparsers.add_parser('query', help='Query the RAG system')
    query_parser.add_argument('question', type=str, help='Question to ask')
    query_parser.add_argument('--model', type=str, default=MODEL,
                              help=f'LLM model to use (default: {MODEL})')

    # Code generation command
    codegen_parser = subparsers.add_parser('codegen', help='Generate code')
    codegen_parser.add_argument('task', type=str, help='Task description for code generation')
    codegen_parser.add_argument('--model', type=str, default=MODEL,
                                help=f'LLM model to use (default: {MODEL})')
    codegen_parser.add_argument('--save', type=str, help='Save generated code to file')

    # Check command
    check_parser = subparsers.add_parser('check', help='Check Python syntax')
    check_parser.add_argument('filepath', type=str, help='Path to Python file')
    check_parser.add_argument('--model', type=str, default=MODEL,
                              help=f'LLM model to use (default: {MODEL})')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == 'ingest':
            ingest_command(args.filepath, args.model)
        elif args.command == 'query':
            query_command(args.question, args.model)
        elif args.command == 'codegen':
            codegen_command(args.task, args.model, args.save)
        elif args.command == 'check':
            check_command(args.filepath, args.model)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def ingest_command(folder_path: str, model: str):
    """Handle data ingestion for all files in a folder."""
    folder_path = Path(folder_path)

    if not folder_path.exists() or not folder_path.is_dir():
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    rag = SimpleRAG(model_name=model)
    for file in folder_path.iterdir():
        if file.is_file():  # Ensure it's a file
            try:
                yield f"Ingesting: {file}\n"
                rag.ingest_telemetry_data(str(file))
                yield f"✓ Successfully ingested: {file}\n"
            except Exception as e:
                yield f"Error ingesting {file}: {e}\n"

    yield "✓ Data ingestion complete for all files in the folder\n"


def query_command(question: str, model: str):
    """Handle single query."""
    print(f"Initializing RAG pipeline with model: {model}")
    rag = SimpleRAG(model_name=model)

    print(f"Processing query: {question}")
    result = rag.query(question)

    print("\n" + "=" * 80)
    print("ANSWER:")
    print("=" * 80)
    print(result['result'])

    if result.get('source_documents'):
        print("\n" + "=" * 80)
        print("SOURCE DOCUMENTS:")
        print("=" * 80)
        for i, doc in enumerate(result['source_documents'], 1):
            content = doc.get('content', doc)
            print(f"\n[{i}] Content preview: {str(content)[:200]}...")

    return result['result']


def codegen_command(task: str, model: str, save_file: str = None):
    """Handle code generation."""
    rag = SimpleRAG(model_name=model)

    result = rag.query(task, code_generation=True)
    explanation = result['result']
    code = result['code']
    output = "=" * 80 + "\n" + "EXPLANATION:" + "\n" + "=" * 80 + "\n" + result['result'] + "\n"

    if result.get('code'):
        output += "\n" + "=" * 80 + "GENERATED CODE:" + "\n" + "=" * 80 + "\n" + result['code'] + "\n"

        # Default to saving the code if no file is specified
        if not save_file:
            save_file = "output.py"

        with open(save_file, 'w') as f:
            f.write(result['code'])
        output += f"\n✓ Code saved to: {save_file}"
    else:
        output += "\nNo code was generated. The LLM may not have recognized the code format."

    sources = None
    if result.get('source_documents'):
        output += "\n" + "=" * 80 + "\n" + "SOURCE DOCUMENTS:" + "\n" + "=" * 80 + "\n"
        sources = result['source_documents']
        for i, doc in enumerate(result['source_documents'], 1):
            content = doc.get('content', doc)
            output += f"\n[{i}] Content preview: {str(content)[:20]}..."

    return explanation, code, sources


def check_command(file_path: str, model: str):
    """Check Python syntax using ollama."""
    try:
        with open(file_path, 'r') as file:
            code = file.read()

        # Call ollama with the code as input
        result = subprocess.run(
            ["ollama", "run", model],
            input=code,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if result.returncode == 0:
            print("Syntax check passed!")
            print(result.stdout)
        else:
            print("Syntax check failed!")
            print(result.stderr)

    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    main()
