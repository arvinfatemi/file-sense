"""Tools for file operations."""

from pathlib import Path
from typing import Dict, Any, List
from config import config
from src.indexing.file_processor import FileProcessor


class FileTools:
    """File operation tools for agents."""

    def __init__(self):
        self.processor = FileProcessor()
        self.sandbox_dir = config.SANDBOX_DIR

    def read_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read a file's contents.

        Args:
            file_path: Path to the file (relative to sandbox)

        Returns:
            Dictionary with file content and metadata
        """
        full_path = self.sandbox_dir / file_path

        if not full_path.exists():
            return {"error": f"File not found: {file_path}"}

        try:
            metadata = self.processor.process_file(full_path, deep=True)
            return {
                "success": True,
                "file_path": file_path,
                "content": metadata.get("text_content") or metadata.get("text_sample"),
                "metadata": metadata
            }
        except Exception as e:
            return {"error": str(e)}

    def list_files(self, directory: str = "", pattern: str = "*") -> Dict[str, Any]:
        """
        List files in a directory.

        Args:
            directory: Directory path (relative to sandbox)
            pattern: Glob pattern for filtering

        Returns:
            Dictionary with list of files
        """
        search_dir = self.sandbox_dir / directory

        if not search_dir.exists():
            return {"error": f"Directory not found: {directory}"}

        try:
            files = []
            for file_path in search_dir.glob(pattern):
                if file_path.is_file():
                    relative_path = file_path.relative_to(self.sandbox_dir)
                    files.append({
                        "path": str(relative_path),
                        "name": file_path.name,
                        "size": file_path.stat().st_size,
                        "type": self.processor.get_file_category(file_path)
                    })

            return {
                "success": True,
                "directory": directory,
                "files": files,
                "count": len(files)
            }
        except Exception as e:
            return {"error": str(e)}

    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Get metadata for a file without reading full content.

        Args:
            file_path: Path to the file (relative to sandbox)

        Returns:
            Dictionary with file metadata
        """
        full_path = self.sandbox_dir / file_path

        if not full_path.exists():
            return {"error": f"File not found: {file_path}"}

        try:
            metadata = self.processor.process_file(full_path, deep=False)
            return {
                "success": True,
                "file_path": file_path,
                "metadata": metadata
            }
        except Exception as e:
            return {"error": str(e)}

    def get_all_files(self, recursive: bool = True) -> List[Path]:
        """Get all files in the sandbox directory."""
        pattern = "**/*" if recursive else "*"
        return [f for f in self.sandbox_dir.glob(pattern) if f.is_file()]
