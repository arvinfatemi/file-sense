"""File processing and metadata extraction."""

import os
import mimetypes
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class FileProcessor:
    """Processes files and extracts metadata."""

    def __init__(self, max_sample_size: int = 1000):
        self.max_sample_size = max_sample_size
        mimetypes.init()

    def process_file(self, file_path: Path, deep: bool = False) -> Dict[str, Any]:
        """
        Process a file and extract metadata.

        Args:
            file_path: Path to the file
            deep: Whether to perform deep processing

        Returns:
            Dictionary containing file metadata
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        stat = file_path.stat()
        mime_type, _ = mimetypes.guess_type(str(file_path))

        metadata = {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "file_type": mime_type or "unknown",
            "file_size": stat.st_size,
            "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        }

        # Extract text content if applicable
        if self._is_text_file(file_path, mime_type):
            try:
                if deep:
                    metadata["text_content"] = self._read_full_text(file_path)
                else:
                    metadata["text_sample"] = self._read_text_sample(file_path)
            except Exception as e:
                metadata["text_content"] = None
                metadata["text_sample"] = None
                metadata["error"] = str(e)

        return metadata

    def _is_text_file(self, file_path: Path, mime_type: Optional[str]) -> bool:
        """Check if a file is a text file."""
        if mime_type and mime_type.startswith("text/"):
            return True

        # Check common text file extensions
        text_extensions = {
            ".txt", ".md", ".py", ".js", ".java", ".cpp", ".c", ".h",
            ".json", ".xml", ".yaml", ".yml", ".csv", ".log", ".rst",
            ".html", ".css", ".sh", ".bash", ".sql", ".r", ".rb"
        }
        return file_path.suffix.lower() in text_extensions

    def _read_text_sample(self, file_path: Path) -> str:
        """Read a sample of text from a file."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(self.max_sample_size)
        except Exception:
            return ""

    def _read_full_text(self, file_path: Path) -> str:
        """Read full text content from a file."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception:
            return ""

    def extract_text_from_pdf(self, file_path: Path) -> str:
        """Extract text from a PDF file."""
        try:
            import PyPDF2
            text = []
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text.append(page.extract_text())
            return "\n".join(text)
        except Exception as e:
            return f"Error extracting PDF text: {str(e)}"

    def extract_text_from_docx(self, file_path: Path) -> str:
        """Extract text from a DOCX file."""
        try:
            import docx
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            return f"Error extracting DOCX text: {str(e)}"

    def get_file_category(self, file_path: Path) -> str:
        """Categorize file based on extension."""
        suffix = file_path.suffix.lower()

        categories = {
            "document": {".pdf", ".doc", ".docx", ".txt", ".md", ".rtf", ".odt"},
            "code": {".py", ".js", ".java", ".cpp", ".c", ".h", ".go", ".rb", ".php"},
            "data": {".csv", ".json", ".xml", ".yaml", ".yml", ".sql"},
            "image": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"},
            "spreadsheet": {".xls", ".xlsx", ".ods"},
            "presentation": {".ppt", ".pptx", ".odp"},
            "archive": {".zip", ".tar", ".gz", ".rar", ".7z"},
        }

        for category, extensions in categories.items():
            if suffix in extensions:
                return category

        return "misc"
