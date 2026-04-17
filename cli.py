#!/usr/bin/env python
"""
Command-line interface for Satellite Telemetry RAG with Code Generation
"""

import argparse
import sys
from pathlib import Path
from src.rag_pipeline import SimpleRAG
# from src.telemetry_loader import TelemetryProcessor


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
  
  # Interactive mode
  python cli.py interactive
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Ingest command
    ingest_parser = subparsers.add_parser('ingest', help='Ingest telemetry data')
    ingest_parser.add_argument('filepath', type=str, help='Path to telemetry file')
    ingest_parser.add_argument('--model', type=str, default='llama2',
                               help='LLM model to use (default: llama2)')

    # Query command
    query_parser = subparsers.add_parser('query', help='Query the RAG system')
    query_parser.add_argument('question', type=str, help='Question to ask')
    query_parser.add_argument('--model', type=str, default='llama2',
                              help='LLM model to use (default: llama2)')

    # Code generation command
    codegen_parser = subparsers.add_parser('codegen', help='Generate code')
    codegen_parser.add_argument('task', type=str, help='Task description for code generation')
    codegen_parser.add_argument('--model', type=str, default='llama2',
                                help='LLM model to use (default: llama2)')
    codegen_parser.add_argument('--save', type=str, help='Save generated code to file')

    # Interactive command
    interactive_parser = subparsers.add_parser('interactive', help='Interactive mode')
    interactive_parser.add_argument('--model', type=str, default='llama2',
                                    help='LLM model to use (default: llama2)')

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
        elif args.command == 'interactive':
            interactive_command(args.model)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def ingest_command(filepath: str, model: str):
    """Handle data ingestion."""
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    rag = SimpleRAG(model_name=model)
    rag.ingest_telemetry_data(str(filepath))
    output = rag.output

    output += "✓ Data ingestion complete\n"
    return output


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

    if result.get('source_documents'):
        output += "\n" + "=" * 80 + "\n" + "SOURCE DOCUMENTS:" + "\n" + "=" * 80 + "\n"
        for i, doc in enumerate(result['source_documents'], 1):
            content = doc.get('content', doc)
            output += f"\n[{i}] Content preview: {str(content)[:20]}..."

    return output

def interactive_command(model: str):
    """Handle interactive mode."""
    print(f"Initializing RAG pipeline with model: {model}")
    print("Commands:")
    print("  query <question>     - Ask a question")
    print("  codegen <task>       - Generate code")
    print("  ingest <filepath>    - Ingest data")
    print("  exit                 - Quit\n")

    rag = SimpleRAG(model_name=model)

    while True:
        try:
            user_input = input(">> ").strip()

            if not user_input:
                continue

            if user_input.lower() == 'exit':
                print("Goodbye!")
                break

            if user_input.startswith('ingest '):
                filepath = user_input[7:].strip()
                print(f"Ingesting: {filepath}")
                rag.ingest_telemetry_data(filepath)
                print("✓ Ingestion complete\n")
                continue

            if user_input.startswith('codegen '):
                task = user_input[8:].strip()
                print(f"\nGenerating code...\n")
                result = rag.query(task, code_generation=True)
                print(f"Explanation: {result['result']}\n")
                if result.get('code'):
                    print("Code:\n")
                    print(result['code'])
                print()
                continue

            if user_input.startswith('query '):
                question = user_input[6:].strip()
                print(f"\nProcessing query...\n")
                result = rag.query(question)
                print(f"Answer: {result['result']}\n")
                continue

            # Default to query if no command specified
            print(f"\nProcessing query...\n")
            result = rag.query(user_input)
            print(f"Answer: {result['result']}\n")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == '__main__':
    main()