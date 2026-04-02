#!/usr/bin/env python
"""
Command-line interface for Satellite Telemetry RAG
"""

import argparse
import sys
from pathlib import Path
from src.rag_pipeline import SimpleRAG
# from src.telemetry_loader import TelemetryProcessor


def main():
    parser = argparse.ArgumentParser(
        description="Satellite Telemetry RAG System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest telemetry data
  python cli.py ingest data/telemetry.csv
  
  # Query the RAG system
  python cli.py query "What was the satellite altitude?"
  
  # Interactive mode
  python cli.py interactive
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Ingest command
    ingest_parser = subparsers.add_parser('ingest', help='Ingest telemetry data')
    ingest_parser.add_argument('filepath', type=str, help='Path to telemetry file')
    ingest_parser.add_argument('--model', type=str, default='mistral',
                              help='LLM model to use (default: mistral)')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Query the RAG system')
    query_parser.add_argument('question', type=str, help='Question to ask')
    query_parser.add_argument('--model', type=str, default='mistral',
                             help='LLM model to use (default: mistral)')
    
    # Interactive command
    interactive_parser = subparsers.add_parser('interactive', help='Interactive mode')
    interactive_parser.add_argument('--model', type=str, default='mistral',
                                   help='LLM model to use (default: mistral)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'ingest':
            ingest_command(args.filepath, args.model)
        elif args.command == 'query':
            query_command(args.question, args.model)
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
    
    print(f"Initializing RAG pipeline with model: {model}")
    rag = SimpleRAG(model_name=model)
    
    print(f"Ingesting telemetry data from: {filepath}")
    rag.ingest_telemetry_data(str(filepath))
    
    print("✓ Data ingestion complete")


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


def interactive_command(model: str):
    """Handle interactive mode."""
    print(f"Initializing RAG pipeline with model: {model}")
    print("Type 'exit' to quit, 'ingest <filepath>' to add data\n")
    
    rag = SimpleRAG(model_name=model)
    
    while True:
        try:
            user_input = input("Query> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == 'exit':
                print("Goodbye!")
                break
            
            if user_input.startswith('ingest '):
                filepath = user_input[7:].strip()
                print(f"Ingesting: {filepath}")
                rag.ingest_telemetry_data(filepath)
                print("✓ Ingestion complete")
                continue
            
            print("\nProcessing query...\n")
            result = rag.query(user_input)
            
            print(f"Answer: {result['result']}\n")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == '__main__':
    main()
