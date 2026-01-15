# Question Generation System

Automatically generate meaningful and relevant questions from academic documents using Large Language Models (LLMs).

### Important Notes:

- PLEASE MAKE SURE TO:
  a.Install requirements/dependencies (Run 'pip install groq pypdf python-dotenv' on terminal)
  b.Get GROQ API (https://console.groq.com/)
  c.Create your own .env file and set up the API KEY
  d.Configure the document path in 'config.py' in the 'INPUT_FILE_PATH' variable (INPUT_FILE_PATH = r"C:\Users\YourName\Documents\research_paper.pdf")
  e.Run main.py

- The `.env` file is git-ignored (won't be uploaded to GitHub)

- The `config.py` file shows example path format

- Never commit your API keys or personal file paths

- Replace example paths with your own

## Features

- **Document Support**: PDF and TXT files (optimized for academic papers)
- **Smart Processing**: Automatic text extraction, cleaning, and chunking
- **Academic Paper Support**: Handles IEEE format, two-column layout, removes headers/footers/references
- **LLM-Powered**: Uses Groq API with Llama 3.3 (FREE and FAST)
- **Question Types**:
  - 5-10 Factual questions (who, what, when, where)
  - 3-5 Conceptual questions (why, how, explain)
- **Plain Text Output**: Easy-to-read formatted output

## Project Structure

question-generator/
├── document_processor.py   # Document extraction & cleaning (academic paper support)
├── text_chunker.py         # Smart text chunking
├── question_generator.py   # Groq LLM interaction
├── main.py                 # CLI interface
├── config.py              # Local file path configuration
├── requirements.txt       # Python dependencies
├── .env                   # API keys (create this, git-ignored)
├── .gitignore            # Git ignore file
└── README.md             # This file

## How It Works

### Pipeline Overview

Input Document -> Text Extraction -> Cleaning -> Chunking (if needed) 
                                                     |
Questions Output <- Format & Display <- LLM Processing <- Context Preparation


## Configuration

### Token Limits

Default: 3000 tokens per chunk (~750 words)

Adjust with `--max-tokens` flag:
```
python main.py --input doc.pdf --max-tokens 2000
```

### Academic Paper Support

The system is optimized for IEEE format and similar academic papers:
- Handles two-column layouts
- Removes author information and affiliations
- Removes headers, footers, page numbers
- Removes references section
- Removes copyright text
- Extracts only main content sections

## License

MIT License - feel free to use for educational or commercial purposes
