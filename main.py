"""
main.py
CLI interface for the Question Generation System
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Import configuration
try:
    from config import INPUT_FILE_PATH
except ImportError:
    INPUT_FILE_PATH = None

# Import the modules
try:
    from document_processor import DocumentProcessor
    from text_chunker import TextChunker
    from question_generator import QuestionGenerator
except ImportError:
    print("Error: Unable to import modules. Make sure all files are in the same directory.")
    sys.exit(1)


def format_output(questions: dict, document_name: str) -> str:
    """
    Format questions as plain text output
    
    Args:
        questions: Dictionary with factual and conceptual questions
        document_name: Name of the source document
        
    Returns:
        Formatted string output
    """
    output = []
    output.append("-" * 70)
    output.append("GENERATED QUESTIONS")
    output.append("-" * 70)
    output.append(f"Source Document: {document_name}")
    output.append("-" * 70)
    
    # Factual Questions (limited to 7)
    output.append("\nFACTUAL QUESTIONS")
    output.append("-" * 70)
    for i, question in enumerate(questions['factual'][:7], 1):
        output.append(f"{i}. {question}")
    
    # Conceptual Questions (limited to 3)
    output.append("\nCONCEPTUAL QUESTIONS")
    output.append("-" * 70)
    for i, question in enumerate(questions['conceptual'][:3], 1):
        output.append(f"{i}. {question}")
    
    return "\n".join(output)


def save_output(output_text: str, output_file: str = None):
    """
    Save output to file
    
    Args:
        output_text: Formatted output text
        output_file: Path to output file (optional)
    """
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_text)
            print(f"\nOutput saved to: {output_file}")
        except Exception as e:
            print(f"\nWarning: Could not save to file: {e}")


def main():
    """Main CLI function"""
    
    # Header
    print("\n" + "-" * 70)
    print("QUESTION GENERATION SYSTEM")
    print("-" * 70)
    print("Automatic Question Generation from Documents using Groq AI")
    print("-" * 70 + "\n")
    
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Generate questions from PDF or text documents using Groq LLM',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py
  python main.py --input document.pdf
  python main.py --input document.txt --output questions.txt
  python main.py -i doc.pdf -o output.txt

Requirements:
  - Set GROQ_API_KEY environment variable
  - Install dependencies: pip install -r requirements.txt
  - Configure INPUT_FILE_PATH in config.py (optional)
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        help='Path to input document (PDF or TXT). If not provided, uses config.py',
        metavar='FILE'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Path to output file (optional, displays to console if not provided)',
        metavar='FILE'
    )
    
    parser.add_argument(
        '--max-tokens',
        type=int,
        default=3000,
        help='Maximum tokens per chunk (default: 3000)',
        metavar='N'
    )
    
    args = parser.parse_args()
    
    # Determine input file path
    if args.input:
        input_file = args.input
    elif INPUT_FILE_PATH:
        input_file = INPUT_FILE_PATH
    else:
        print("Error: No input file specified.")
        print("Either:")
        print("  1. Use --input flag: python main.py --input document.pdf")
        print("  2. Set INPUT_FILE_PATH in config.py")
        sys.exit(1)
    
    # Validate input file
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)
    
    if input_path.suffix.lower() not in ['.pdf', '.txt']:
        print(f"Error: Unsupported file format. Use .pdf or .txt files.")
        sys.exit(1)
    
    # Check API key
    if not os.getenv('GROQ_API_KEY'):
        print("Error: GROQ_API_KEY environment variable not set.")
        print("\nTo set it:")
        print("set GROQ_API_KEY=your-api-key")
        print("\nGet your free API key from: https://console.groq.com/keys")
        sys.exit(1)
    
    try:
        # Process Document (silent processing)
        processor = DocumentProcessor(str(input_path))
        document_text = processor.process()
        
        # Chunk if necessary (silent processing)
        chunker = TextChunker(max_tokens=args.max_tokens)
        chunks = chunker.chunk_text(document_text)
        
        # Generate Questions (silent processing)
        generator = QuestionGenerator()
        
        if len(chunks) == 1:
            questions = generator.generate_from_text(document_text)
        else:
            questions = generator.generate_from_chunks(chunks)
        
        # Format and Output
        output_text = format_output(questions, input_path.name)
        
        # Display to console
        print("\n" + output_text)
        
        # Save to file if specified
        if args.output:
            save_output(output_text, args.output)
        
        print("\n\nProcess completed successfully\n")
        
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()