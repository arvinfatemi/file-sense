"""Configuration management for AI File Concierge."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""

    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent
    SANDBOX_DIR = PROJECT_ROOT / "sandbox"
    DATA_DIR = PROJECT_ROOT / "data"

    # API Configuration
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")

    # Vector Database Configuration
    CHROMA_PERSIST_DIR = DATA_DIR / "chroma"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"

    # Memory Configuration
    MEMORY_DB_PATH = DATA_DIR / "memory.db"
    METADATA_STORE = DATA_DIR / "metadata.json"

    # File Processing Configuration
    MAX_FILE_SIZE_MB = 10
    TEXT_SAMPLE_SIZE = 1000  # Characters for shallow sampling
    DEEP_PROCESS_THRESHOLD = 5  # Number of files for deep processing

    # Search Configuration
    TOP_K_RESULTS = 10
    SIMILARITY_THRESHOLD = 0.3

    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist."""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
        cls.SANDBOX_DIR.mkdir(exist_ok=True)

        # Create sandbox subdirectories
        (cls.SANDBOX_DIR / "documents").mkdir(exist_ok=True)
        (cls.SANDBOX_DIR / "code").mkdir(exist_ok=True)
        (cls.SANDBOX_DIR / "notes").mkdir(exist_ok=True)
        (cls.SANDBOX_DIR / "images").mkdir(exist_ok=True)
        (cls.SANDBOX_DIR / "misc").mkdir(exist_ok=True)

config = Config()
