# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is an Ollama fine-tuning tool that processes markdown files to create custom-trained language models. The application uses Python with asyncio for efficient processing and provides a CLI interface for model training and testing.

## Project Structure

```
src/
├── __init__.py          # Package init
├── config.py           # Configuration management with pydantic
├── file_processor.py   # Markdown processing and chunking
├── ollama_client.py    # Ollama API integration
└── main.py            # CLI interface with click

import/
├── landing/           # Place markdown files here for processing
└── done/             # Processed files are moved here

.env.example           # Environment configuration template
requirements.txt       # Python dependencies
pyproject.toml        # Project metadata and dependencies
```

## Development Commands

### Setup
```bash
pip install -r requirements.txt
cp .env.example .env  # Configure as needed
```

### Core Workflow
```bash
# Process markdown files from import/landing/
python -m src.main process

# Train model on processed data
python -m src.main train

# Interactive chat with fine-tuned model
python -m src.main chat

# List available models
python -m src.main models

# Show status and configuration
python -m src.main status
```

## Architecture Notes

- **Async Processing**: Uses aiofiles and asyncio for efficient file handling
- **Rich UI**: CLI uses rich library for progress bars and formatted output
- **Chunking Strategy**: Splits markdown content by paragraphs respecting context length limits
- **Training Format**: Converts markdown to instruction-response pairs for Ollama modelfile format
- **File Management**: Automatically moves processed files from landing to done directory

## Configuration

Key settings in `.env`:
- `OLLAMA_HOST`: Ollama server endpoint
- `OLLAMA_BASE_MODEL`: Source model to fine-tune (e.g., llama3.1:8b)
- `OLLAMA_CUSTOM_MODEL_NAME`: Name for the fine-tuned model
- `MAX_CONTEXT_LENGTH`: Maximum chunk size for training data