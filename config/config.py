"""Configuration management for AI File Concierge."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""

    # Project paths - use .resolve() for absolute paths
    PROJECT_ROOT = Path(__file__).parent.parent.resolve()
    SANDBOX_DIR = (PROJECT_ROOT / "sandbox").resolve()
    DATA_DIR = (PROJECT_ROOT / "data").resolve()

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

    @classmethod
    def validate_paths(cls):
        """Validate that critical paths exist and are accessible."""
        import sys

        if not cls.PROJECT_ROOT.exists():
            print(f"ERROR: Project root not found at: {cls.PROJECT_ROOT}", file=sys.stderr)
            print(f"Current working directory: {Path.cwd()}", file=sys.stderr)
            raise RuntimeError(f"Project root directory not found: {cls.PROJECT_ROOT}")

        if not cls.SANDBOX_DIR.exists():
            print(f"WARNING: Sandbox directory not found at: {cls.SANDBOX_DIR}", file=sys.stderr)
            print(f"Creating sandbox directory...", file=sys.stderr)
            cls.ensure_directories()

        if not cls.DATA_DIR.exists():
            print(f"WARNING: Data directory not found at: {cls.DATA_DIR}", file=sys.stderr)
            print(f"Creating data directory...", file=sys.stderr)
            cls.ensure_directories()

config = Config()
# Validate paths on module import
config.validate_paths()
