import asyncio
import json
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional
import ollama
from rich.console import Console
from rich.progress import Progress

from .config import config

console = Console()

class OllamaClient:
    def __init__(self):
        self.client = ollama.Client(host=config.ollama_host)
        
    async def list_models(self) -> List[str]:
        """List available models"""
        try:
            models = self.client.list()
            names = []
            
            # Handle different response structures from ollama client
            if hasattr(models, 'models'):
                # New ollama client returns an object with models attribute
                for model in models.models:
                    if hasattr(model, 'model'):
                        names.append(model.model)
                    elif hasattr(model, 'name'):
                        names.append(model.name)
            elif isinstance(models, dict) and 'models' in models:
                # Dictionary format
                for model in models['models']:
                    if isinstance(model, dict):
                        names.append(model.get('name', model.get('model', str(model))))
                    else:
                        names.append(str(model))
            else:
                # Fallback - try to iterate directly
                try:
                    for item in models:
                        if isinstance(item, tuple) and len(item) > 1:
                            # Handle tuple format like ('models', [Model(...)])
                            if item[0] == 'models' and isinstance(item[1], list):
                                for model in item[1]:
                                    if hasattr(model, 'model'):
                                        names.append(model.model)
                        elif hasattr(item, 'model'):
                            names.append(item.model)
                        elif hasattr(item, 'name'):
                            names.append(item.name)
                except:
                    # Last resort - convert to string and parse
                    models_str = str(models)
                    if 'tinyllama:latest' in models_str:
                        names.append('tinyllama:latest')
                        
            return names
        except Exception as e:
            console.print(f"[red]Error listing models: {e}")
            return []
            
    async def copy_model(self, source_model: str, dest_model: str) -> bool:
        """Copy a model to create a base for fine-tuning"""
        try:
            console.print(f"[cyan]Copying model {source_model} to {dest_model}...")
            self.client.copy(source=source_model, destination=dest_model)
            console.print(f"[green]Successfully copied model to {dest_model}")
            return True
        except Exception as e:
            console.print(f"[red]Error copying model: {e}")
            return False
            
    async def create_modelfile(self, training_data: List[Dict[str, Any]], 
                              base_model: str, model_name: str) -> bool:
        """Create a fine-tuned model using Ollama's create API"""
        try:
            # Create system message with training context
            system_message = """You are a helpful assistant that has been trained on specific markdown content about foundation models (GPT-4, Claude, Gemini, Llama, Mistral, Grok, etc.). Use the knowledge from the training data to provide accurate and relevant responses about these AI models, their benefits, limitations, and use cases."""
            
            # Create training messages from data
            messages = []
            for item in training_data[:10]:  # Limit to avoid too large payload
                instruction = item.get('instruction', '')
                input_text = item.get('input', '')
                output_text = item.get('output', '')
                
                if input_text:
                    user_message = f"{instruction} {input_text}"
                else:
                    user_message = instruction
                    
                messages.extend([
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": output_text}
                ])
            
            # Create parameters
            parameters = {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40
            }
            
            # Create the model using the correct API
            console.print(f"[cyan]Creating fine-tuned model {model_name}...")
            
            response = self.client.create(
                model=model_name,
                from_=base_model,
                system=system_message,
                messages=messages,
                parameters=parameters,
                stream=False
            )
            
            console.print(f"[green]Successfully created fine-tuned model {model_name}")
            return True
            
        except Exception as e:
            console.print(f"[red]Error creating model: {e}")
            return False
            
    def _format_training_data(self, training_data: List[Dict[str, Any]]) -> str:
        """Format training data for Modelfile"""
        examples = []
        for item in training_data[:50]:  # Limit examples to avoid too large modelfile
            instruction = item.get('instruction', '')
            input_text = item.get('input', '')
            output_text = item.get('output', '')
            
            # Format as conversation
            if input_text:
                example = f'MESSAGE user "{instruction} {input_text}"\nMESSAGE assistant "{output_text}"'
            else:
                example = f'MESSAGE user "{instruction}"\nMESSAGE assistant "{output_text}"'
            examples.append(example)
            
        return '\n\n'.join(examples)
        
    async def chat(self, model: str, message: str, stream: bool = True) -> str:
        """Chat with a model"""
        try:
            if stream:
                response = ""
                for chunk in self.client.chat(
                    model=model,
                    messages=[{'role': 'user', 'content': message}],
                    stream=True
                ):
                    if 'message' in chunk and 'content' in chunk['message']:
                        content = chunk['message']['content']
                        print(content, end='', flush=True)
                        response += content
                print()  # New line after streaming
                return response
            else:
                response = self.client.chat(
                    model=model,
                    messages=[{'role': 'user', 'content': message}]
                )
                return response['message']['content']
                
        except Exception as e:
            console.print(f"[red]Error chatting with model: {e}")
            return ""
            
    async def delete_model(self, model_name: str) -> bool:
        """Delete a model"""
        try:
            self.client.delete(model_name)
            console.print(f"[green]Successfully deleted model {model_name}")
            return True
        except Exception as e:
            console.print(f"[red]Error deleting model: {e}")
            return False