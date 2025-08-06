# Ollama Fine-Tuning Tool

A Python CLI tool for fine-tuning Ollama models using markdown files as training data.

## Features

- Process markdown files into training data
- Fine-tune Ollama models with custom content
- Interactive CLI chat interface for testing
- Automatic file management (landing → done)

## Setup

1. Run the setup script to create virtual environment and install dependencies:
```bash
./setup.sh
```

2. Activate the virtual environment:
```bash
source venv/bin/activate
```

3. Edit configuration:
```bash
# Edit .env with your settings
nano .env
```

4. Ensure Ollama is running:
```bash
ollama serve
```

## Usage

1. **Add markdown files** to `/import/landing/` directory

2. **Process files** into training data:
```bash
python -m src.main process
```

3. **Train the model**:
```bash
python -m src.main train
```

4. **Chat with your fine-tuned model**:
```bash
python -m src.main chat
```

## Commands

- `process` - Process markdown files from landing directory
- `train` - Create fine-tuned model from processed data
- `chat` - Interactive chat with fine-tuned model  
- `models` - List available models
- `status` - Show configuration and status
- `delete-model MODEL` - Delete a model

## Configuration

Edit `.env` file to customize:
- `OLLAMA_HOST` - Ollama server URL
- `OLLAMA_BASE_MODEL` - Base model to fine-tune
- `OLLAMA_CUSTOM_MODEL_NAME` - Name for your fine-tuned model
