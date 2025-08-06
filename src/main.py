import asyncio
import sys
from pathlib import Path
import click
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table

from .config import config
from .file_processor import MarkdownProcessor
from .ollama_client import OllamaClient

console = Console()

@click.group()
def cli():
    """Ollama Fine-tuning Tool - Train models on markdown files"""
    pass

@cli.command()
async def process():
    """Process markdown files from the landing directory"""
    processor = MarkdownProcessor()
    training_data = await processor.process_files()
    
    if training_data:
        # Save training data
        output_path = config.project_root / "training_data.json"
        await processor.save_training_data(output_path)
        console.print(f"[green]Training data saved to {output_path}")
    else:
        console.print("[yellow]No training data generated")

@cli.command()
@click.option('--base-model', default=None, help='Base model to copy from')
@click.option('--model-name', default=None, help='Name for the fine-tuned model')
async def train(base_model, model_name):
    """Train a model on processed markdown files"""
    if not base_model:
        base_model = config.base_model
    if not model_name:
        model_name = config.custom_model_name
        
    client = OllamaClient()
    
    # Check if base model exists
    models = await client.list_models()
    if base_model not in models:
        console.print(f"[red]Base model {base_model} not found. Available models:")
        for model in models:
            console.print(f"  - {model}")
        return
        
    # Load training data
    training_data_path = config.project_root / "training_data.json"
    if not training_data_path.exists():
        console.print(f"[red]No training data found. Run 'process' command first.")
        return
        
    import json
    with open(training_data_path, 'r') as f:
        training_data = json.load(f)
        
    console.print(f"[cyan]Training data loaded: {len(training_data)} examples")
    
    # Confirm training
    if not Confirm.ask(f"Create fine-tuned model '{model_name}' from '{base_model}'?"):
        return
        
    # Create the fine-tuned model
    success = await client.create_modelfile(training_data, base_model, model_name)
    if success:
        console.print(f"[green]Successfully created fine-tuned model: {model_name}")
    else:
        console.print(f"[red]Failed to create fine-tuned model")

@cli.command()
@click.option('--model', default=None, help='Model to chat with')
async def chat(model):
    """Interactive chat with a fine-tuned model"""
    if not model:
        model = config.custom_model_name
        
    client = OllamaClient()
    
    # Check if model exists
    models = await client.list_models()
    if model not in models:
        console.print(f"[red]Model {model} not found. Available models:")
        for m in models:
            console.print(f"  - {m}")
        return
        
    console.print(f"[green]Starting chat with {model}")
    console.print("[dim]Type 'quit', 'exit', or press Ctrl+C to stop[/dim]")
    console.print()
    
    try:
        while True:
            # Get user input
            user_input = Prompt.ask("[bold blue]You", default="")
            
            if user_input.lower() in ['quit', 'exit', '']:
                break
                
            # Get model response
            console.print("[bold green]Assistant:[/bold green] ", end="")
            response = await client.chat(model, user_input, stream=True)
            console.print()
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Chat ended.")

@cli.command()
async def models():
    """List available models"""
    client = OllamaClient()
    models = await client.list_models()
    
    if models:
        table = Table(title="Available Models")
        table.add_column("Model Name", style="cyan")
        
        for model in models:
            table.add_row(model)
            
        console.print(table)
    else:
        console.print("[yellow]No models found")

@cli.command()
@click.argument('model_name')
async def delete_model(model_name):
    """Delete a model"""
    client = OllamaClient()
    
    if Confirm.ask(f"Delete model '{model_name}'?"):
        success = await client.delete_model(model_name)
        if not success:
            sys.exit(1)

@cli.command()
async def status():
    """Show current status and configuration"""
    table = Table(title="Configuration Status")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Ollama Host", config.ollama_host)
    table.add_row("Base Model", config.base_model) 
    table.add_row("Custom Model Name", config.custom_model_name)
    table.add_row("Import Landing", str(config.import_landing))
    table.add_row("Import Done", str(config.import_done))
    
    console.print(table)
    
    # Check directories
    console.print(f"\n[bold]Directory Status:[/bold]")
    console.print(f"Landing exists: {config.import_landing.exists()}")
    console.print(f"Done exists: {config.import_done.exists()}")
    
    # Count files
    if config.import_landing.exists():
        md_files = list(config.import_landing.glob("*.md"))
        console.print(f"Markdown files in landing: {len(md_files)}")
        
    training_data_path = config.project_root / "training_data.json"
    console.print(f"Training data exists: {training_data_path.exists()}")

def main():
    """Convert sync CLI to async"""
    import inspect
    
    def async_command(f):
        if inspect.iscoroutinefunction(f):
            def wrapper(*args, **kwargs):
                return asyncio.run(f(*args, **kwargs))
            return wrapper
        return f
    
    # Convert async commands to sync for click
    for name, obj in cli.commands.items():
        if hasattr(obj, 'callback') and inspect.iscoroutinefunction(obj.callback):
            obj.callback = async_command(obj.callback)
    
    cli()

if __name__ == "__main__":
    main()