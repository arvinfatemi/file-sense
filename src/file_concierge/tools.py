"""Tool functions for the File Concierge agent using Google ADK.

These functions are directly callable by the ADK agent.
"""

from typing import List, Optional
from pathlib import Path
import sys
from src.memory.long_term import LongTermMemory
from src.indexing.vector_store import VectorStore
from src.indexing.file_processor import FileProcessor
from config import config

# Validate sandbox directory exists before initializing tools
if not config.SANDBOX_DIR.exists():
    print(f"ERROR: Sandbox directory not found!", file=sys.stderr)
    print(f"Expected: {config.SANDBOX_DIR}", file=sys.stderr)
    print(f"Current working directory: {Path.cwd()}", file=sys.stderr)
    raise RuntimeError(
        f"Sandbox directory not found at: {config.SANDBOX_DIR}\n"
        f"Please ensure the project structure is intact."
    )

# Log paths for debugging
print(f"[DEBUG] Tools initialized with paths:", file=sys.stderr)
print(f"  PROJECT_ROOT: {config.PROJECT_ROOT}", file=sys.stderr)
print(f"  SANDBOX_DIR: {config.SANDBOX_DIR}", file=sys.stderr)
print(f"  DATA_DIR: {config.DATA_DIR}", file=sys.stderr)
print(f"  Current working directory: {Path.cwd()}", file=sys.stderr)

# Initialize shared resources
_memory = LongTermMemory()
_vector_store = VectorStore()
_file_processor = FileProcessor()


def search_files(query: str, tags: Optional[List[str]] = None, top_k: int = 10) -> dict:
    """
    Search for files using natural language queries and/or tags.

    Args:
        query: Natural language search query describing what files to find
        tags: Optional list of tags to filter results by
        top_k: Maximum number of results to return (default: 10)

    Returns:
        Dictionary containing search results with file paths, similarity scores, and metadata
    """
    try:
        # Perform semantic search
        results = _vector_store.search(query, top_k=top_k)

        # Enrich with tags
        for result in results:
            file_path = result["file_path"]
            result["tags"] = _memory.get_file_tags(file_path)

        # Filter by tags if provided
        if tags:
            filtered_results = []
            for result in results:
                if any(tag in result["tags"] for tag in tags):
                    filtered_results.append(result)
            results = filtered_results

        return {
            "status": "success",
            "query": query,
            "tags_filter": tags,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def suggest_tags(file_path: str) -> dict:
    """
    Suggest relevant tags for a file based on its content using AI.

    Args:
        file_path: Path to the file relative to sandbox directory

    Returns:
        Dictionary containing suggested tags
    """
    try:
        # Read file content
        full_path = config.SANDBOX_DIR / file_path
        if not full_path.exists():
            return {"status": "error", "error_message": f"File not found: {file_path}"}

        metadata = _file_processor.process_file(full_path, deep=False)
        content = metadata.get("text_sample", "")

        if not content:
            return {"status": "error", "error_message": "No text content to analyze"}

        # Get existing tags for context
        existing_tags = _memory.get_all_tags()

        # For now, suggest tags based on file type and content keywords
        # In a real implementation, this would use an LLM
        suggested = []

        # Add category-based tags
        category = _file_processor.get_file_category(full_path)
        suggested.append(category)

        # Add extension-based tag
        ext = full_path.suffix.lower().replace(".", "")
        if ext:
            suggested.append(ext)

        # Simple keyword extraction
        keywords = ["python", "machine", "learning", "data", "code", "document",
                    "note", "job", "work", "project", "research"]
        content_lower = content.lower()
        for keyword in keywords:
            if keyword in content_lower:
                suggested.append(keyword)

        # Remove duplicates and limit
        suggested = list(set(suggested))[:5]

        return {
            "status": "success",
            "file_path": file_path,
            "suggested_tags": suggested
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def apply_tags(file_path: str, tags: List[str]) -> dict:
    """
    Apply one or more tags to a file.

    Args:
        file_path: Path to the file relative to sandbox directory
        tags: List of tag names to apply

    Returns:
        Dictionary indicating success or failure
    """
    try:
        for tag in tags:
            _memory.tag_file(file_path, tag.lower())

        return {
            "status": "success",
            "file_path": file_path,
            "tags_applied": [t.lower() for t in tags],
            "message": f"Applied {len(tags)} tag(s) to {file_path}"
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def get_file_tags(file_path: str) -> dict:
    """
    Get all tags currently applied to a file.

    Args:
        file_path: Path to the file relative to sandbox directory

    Returns:
        Dictionary containing the file's tags
    """
    try:
        tags = _memory.get_file_tags(file_path)
        return {
            "status": "success",
            "file_path": file_path,
            "tags": tags,
            "count": len(tags)
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def create_collection(name: str, description: str = "") -> dict:
    """
    Create a new collection to organize files.

    Args:
        name: Name for the collection
        description: Optional description of the collection's purpose

    Returns:
        Dictionary with collection creation status
    """
    try:
        collection_id = _memory.create_collection(name, description)
        return {
            "status": "success",
            "collection_name": name,
            "collection_id": collection_id,
            "description": description,
            "message": f"Created collection '{name}'"
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def add_to_collection(collection_name: str, file_paths: List[str]) -> dict:
    """
    Add one or more files to an existing collection.

    Args:
        collection_name: Name of the collection
        file_paths: List of file paths to add to the collection

    Returns:
        Dictionary with operation status
    """
    try:
        for file_path in file_paths:
            _memory.add_file_to_collection(collection_name, file_path)

        return {
            "status": "success",
            "collection_name": collection_name,
            "files_added": len(file_paths),
            "message": f"Added {len(file_paths)} file(s) to collection '{collection_name}'"
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def get_collection_files(collection_name: str) -> dict:
    """
    Get all files in a collection.

    Args:
        collection_name: Name of the collection

    Returns:
        Dictionary containing the collection's files
    """
    try:
        files = _memory.get_collection_files(collection_name)
        return {
            "status": "success",
            "collection_name": collection_name,
            "files": files,
            "count": len(files)
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def list_files(directory: str = "", pattern: str = "*") -> dict:
    """
    List files in a directory within the sandbox.

    Args:
        directory: Directory path relative to sandbox (empty for root)
        pattern: Glob pattern for filtering (default: *)

    Returns:
        Dictionary containing list of files with metadata
    """
    try:
        search_dir = config.SANDBOX_DIR / directory
        print(f"[DEBUG] list_files() called with directory='{directory}', pattern='{pattern}'", file=sys.stderr)
        print(f"[DEBUG] Resolved search_dir: {search_dir}", file=sys.stderr)
        print(f"[DEBUG] search_dir.exists(): {search_dir.exists()}", file=sys.stderr)

        if not search_dir.exists():
            return {"status": "error", "error_message": f"Directory not found: {directory} (resolved to: {search_dir})"}

        files = []
        # Use rglob for recursive search if pattern doesn't start with **/
        # This allows patterns like "*.py" to search subdirectories
        if pattern.startswith("**/"):
            glob_method = search_dir.glob
        else:
            # For simple patterns, search recursively using rglob
            glob_method = search_dir.rglob

        for file_path in glob_method(pattern):
            if file_path.is_file():
                relative_path = file_path.relative_to(config.SANDBOX_DIR)
                files.append({
                    "path": str(relative_path),
                    "name": file_path.name,
                    "size": file_path.stat().st_size,
                    "type": _file_processor.get_file_category(file_path)
                })

        return {
            "status": "success",
            "directory": directory,
            "pattern": pattern,
            "files": files,
            "count": len(files)
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def read_file(file_path: str) -> dict:
    """
    Read the full content of a file.

    Args:
        file_path: Path to the file relative to sandbox directory

    Returns:
        Dictionary containing file content and metadata
    """
    try:
        full_path = config.SANDBOX_DIR / file_path
        print(f"[DEBUG] read_file() called with file_path='{file_path}'", file=sys.stderr)
        print(f"[DEBUG] Resolved full_path: {full_path}", file=sys.stderr)
        print(f"[DEBUG] full_path.exists(): {full_path.exists()}", file=sys.stderr)

        if not full_path.exists():
            return {"status": "error", "error_message": f"File not found: {file_path} (resolved to: {full_path})"}

        metadata = _file_processor.process_file(full_path, deep=True)
        content = metadata.get("text_content") or metadata.get("text_sample", "")

        return {
            "status": "success",
            "file_path": file_path,
            "content": content,
            "metadata": {
                "file_name": metadata["file_name"],
                "file_type": metadata["file_type"],
                "file_size": metadata["file_size"]
            }
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


# Tool list for easy export
ALL_TOOLS = [
    search_files,
    suggest_tags,
    apply_tags,
    get_file_tags,
    create_collection,
    add_to_collection,
    get_collection_files,
    list_files,
    read_file
]
