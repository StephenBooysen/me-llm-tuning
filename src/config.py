import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Config(BaseModel):
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    base_model: str = os.getenv("OLLAMA_BASE_MODEL", "llama3.1:8b") 
    custom_model_name: str = os.getenv("OLLAMA_CUSTOM_MODEL_NAME", "custom-tuned-model")
    batch_size: int = int(os.getenv("BATCH_SIZE", "10"))
    max_context_length: int = int(os.getenv("MAX_CONTEXT_LENGTH", "2048"))
    
    # Paths
    project_root: Path = Path(__file__).parent.parent
    import_landing: Path = project_root / "import" / "landing"
    import_done: Path = project_root / "import" / "done"
    
config = Config()