"""File indexing functionality for the File Concierge."""

from pathlib import Path
from rich.console import Console
from rich.progress import Progress
from src.indexing.file_processor import FileProcessor
from src.indexing.vector_store import VectorStore
from src.memory.long_term import LongTermMemory
from config import config


class FileIndexer:
    """Handles indexing of files in the sandbox directory."""

    def __init__(self):
        self.console = Console()
        self.file_processor = FileProcessor()
        self.vector_store = VectorStore()
        self.memory = LongTermMemory()
        config.ensure_directories()

    def index_all_files(self, force_reindex: bool = False):
        """
        Index all files in the sandbox directory.

        Args:
            force_reindex: If True, reindex all files even if already indexed
        """
        self.console.print("[bold cyan]Indexing files in sandbox...[/bold cyan]")

        all_files = self._get_all_files()

        with Progress() as progress:
            task = progress.add_task("[green]Processing files...", total=len(all_files))

            for file_path in all_files:
                relative_path = str(file_path.relative_to(config.SANDBOX_DIR))

                # Check if already indexed
                if not force_reindex:
                    existing = self.memory.get_file_metadata(relative_path)
                    if existing:
                        progress.advance(task)
                        continue

                try:
                    # Process file
                    metadata = self.file_processor.process_file(file_path, deep=False)

                    # Store metadata
                    self.memory.store_file_metadata(relative_path, metadata)

                    # Add to vector store if text content available
                    text_content = metadata.get("text_sample") or metadata.get("text_content")
                    if text_content and text_content.strip():
                        self.vector_store.add_document(
                            relative_path,
                            text_content,
                            {
                                "file_name": metadata["file_name"],
                                "file_type": metadata["file_type"],
                                "category": self.file_processor.get_file_category(file_path)
                            }
                        )

                except Exception as e:
                    self.console.print(f"[red]Error processing {relative_path}: {str(e)}[/red]")

                progress.advance(task)

        indexed_count = len(self.memory.get_all_files())
        vector_count = self.vector_store.count_documents()

        self.console.print(f"[bold green]Indexing complete![/bold green]")
        self.console.print(f"  • Files indexed: {indexed_count}")
        self.console.print(f"  • Files in vector store: {vector_count}")

    def _get_all_files(self):
        """Get all files in the sandbox directory."""
        pattern = "**/*"
        return [f for f in config.SANDBOX_DIR.glob(pattern) if f.is_file()]

    def get_stats(self) -> dict:
        """Get statistics about the indexed files."""
        files = self.memory.get_all_files()
        tags = self.memory.get_all_tags()
        collections = self.memory.get_all_collections()

        return {
            "total_files": len(files),
            "total_tags": len(tags),
            "total_collections": len(collections),
            "vector_store_size": self.vector_store.count_documents()
        }

    def display_stats(self):
        """Display statistics about the system."""
        stats = self.get_stats()

        self.console.print("\n[bold cyan]File Concierge Statistics[/bold cyan]")
        self.console.print(f"  • Total files indexed: {stats['total_files']}")
        self.console.print(f"  • Files in vector store: {stats['vector_store_size']}")
        self.console.print(f"  • Total tags: {stats['total_tags']}")
        self.console.print(f"  • Total collections: {stats['total_collections']}")
