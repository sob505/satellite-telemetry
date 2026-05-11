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
MODEL = "satellite-telemetry2"


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
    ingested_files = []

    for file in folder_path.iterdir():
        if file.is_file() and file.suffix in ['.csv', '.json', '.txt', '.parquet', '.md']:
            try:
                source_name = file.name  # Use just filename as source
                yield f"Ingesting: {source_name}\n"
                rag.ingest_telemetry_data_async(str(file), source_name=source_name)
                yield f"✓ Successfully ingested: {source_name}\n"
                ingested_files.append(source_name)
            except Exception as e:
                yield f"Error ingesting {file.name}: {e}\n"

    if ingested_files:
        yield f"\n✓ Ingested sources:\n"
        for fname in ingested_files:
            yield f"  - {fname}\n"


def query_command(question: str, model: str, progress_callback=None):
    """Handle single query and return structured result."""
    print(f"Initializing RAG pipeline with model: {model}")
    rag = SimpleRAG(model_name=model)

    print(f"Processing query: {question}")
    result = rag.query(question, code_generation=False, progress_callback=progress_callback)

    # Console output
    print("\n" + "=" * 80)
    print("ANSWER:")
    print("=" * 80)
    print(result['result'])

    if result.get('source_documents'):
        print("\n" + "=" * 80)
        print("SOURCES:")
        print("=" * 80)
        for doc in result['source_documents']:
            source = doc.get('source', 'Unknown')
            print(f"  - {source}")

    # Return the full structured result for the GUI
    return result


def codegen_command(task: str, model: str, save_file: str = None, progress_callback=None):
    """Handle code generation and return structured result."""
    rag = SimpleRAG(model_name=model)
    print("RAG Model done\n")
    result = rag.query(task, code_generation=True, progress_callback=progress_callback)
    print("Got results\n")
    if result is None:
        print("No response received from the model. Please check your query and try again.")

    # Console output
    output = "=" * 80 + "\nEXPLANATION:\n" + "=" * 80 + "\n"
    output += result['result'] + "\n"

    if result.get('code'):
        output += "\n" + "=" * 80 + "\nGENERATED CODE:\n" + "=" * 80 + "\n"
        output += result['code'] + "\n"

        # Default to saving the code if no file is specified
        if not save_file:
            save_file = "../output.py"

        with open(save_file, 'w') as f:
            f.write(result['code'])
        output += f"\n✓ Code saved to: {save_file}"
    else:
        output += "\nNo code was generated."

    if result.get('source_documents'):
        output += "\n" + "=" * 80 + "\nSOURCES:\n" + "=" * 80 + "\n"
        for doc in result['source_documents']:
            source = doc.get('source', 'Unknown')
            output += f"  - {source}\n"

    print(output)

    # Return full structured result for the GUI
    return result

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
