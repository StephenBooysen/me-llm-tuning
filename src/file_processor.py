import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any
import aiofiles
from rich.console import Console
from rich.progress import Progress, TaskID

from .config import config

console = Console()

class MarkdownProcessor:
    def __init__(self):
        self.training_data: List[Dict[str, Any]] = []
        
    async def process_files(self) -> List[Dict[str, Any]]:
        """Process all markdown files in the landing directory"""
        landing_path = config.import_landing
        done_path = config.import_done
        
        if not landing_path.exists():
            console.print(f"[red]Landing directory does not exist: {landing_path}")
            return []
            
        md_files = list(landing_path.glob("*.md"))
        if not md_files:
            console.print("[yellow]No markdown files found in landing directory")
            return []
            
        console.print(f"[green]Found {len(md_files)} markdown files to process")
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Processing files...", total=len(md_files))
            
            for md_file in md_files:
                try:
                    content = await self._read_file(md_file)
                    training_examples = self._convert_to_training_data(content, md_file.name)
                    self.training_data.extend(training_examples)
                    
                    # Move processed file to done directory
                    await self._move_file(md_file, done_path)
                    progress.advance(task)
                    
                except Exception as e:
                    console.print(f"[red]Error processing {md_file.name}: {e}")
                    
        console.print(f"[green]Processed {len(md_files)} files, created {len(self.training_data)} training examples")
        return self.training_data
        
    async def _read_file(self, file_path: Path) -> str:
        """Read markdown file content"""
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            return await f.read()
            
    def _convert_to_training_data(self, content: str, filename: str) -> List[Dict[str, Any]]:
        """Convert markdown content to training data format"""
        # Split content into chunks for better training
        chunks = self._chunk_content(content)
        training_examples = []
        
        for i, chunk in enumerate(chunks):
            # Create instruction-response pairs from chunks
            training_examples.append({
                "instruction": f"Based on the content from {filename}, provide relevant information about the following:",
                "input": chunk[:200] + "..." if len(chunk) > 200 else chunk,
                "output": chunk,
                "source": filename,
                "chunk_id": i
            })
            
        return training_examples
        
    def _chunk_content(self, content: str, max_length: int = None) -> List[str]:
        """Chunk content into smaller pieces for training"""
        if max_length is None:
            max_length = config.max_context_length
            
        # Simple chunking by paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) + 2 <= max_length:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"
                
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks
        
    async def _move_file(self, source: Path, dest_dir: Path):
        """Move processed file to done directory"""
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / source.name
        
        # Handle duplicate names
        counter = 1
        while dest_path.exists():
            name_parts = source.stem, counter, source.suffix
            dest_path = dest_dir / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
            counter += 1
            
        source.rename(dest_path)
        
    async def save_training_data(self, output_path: Path):
        """Save training data to JSON file"""
        async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(self.training_data, indent=2, ensure_ascii=False))