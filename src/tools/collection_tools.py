"""Tools for collection management."""

from typing import Dict, Any, List
from src.memory.long_term import LongTermMemory


class CollectionTools:
    """Collection management tools for agents."""

    def __init__(self, memory: LongTermMemory = None):
        self.memory = memory or LongTermMemory()

    def create_collection(self, name: str, description: str = "") -> Dict[str, Any]:
        """
        Create a new collection.

        Args:
            name: Collection name
            description: Optional description

        Returns:
            Dictionary with operation result
        """
        try:
            collection_id = self.memory.create_collection(name, description)
            return {
                "success": True,
                "collection_name": name,
                "collection_id": collection_id,
                "description": description,
                "message": f"Collection '{name}' created"
            }
        except Exception as e:
            return {"error": str(e)}

    def add_to_collection(self, collection_name: str, file_path: str) -> Dict[str, Any]:
        """
        Add a file to a collection.

        Args:
            collection_name: Name of the collection
            file_path: Path to the file

        Returns:
            Dictionary with operation result
        """
        try:
            self.memory.add_file_to_collection(collection_name, file_path)
            return {
                "success": True,
                "collection_name": collection_name,
                "file_path": file_path,
                "message": f"Added {file_path} to collection '{collection_name}'"
            }
        except Exception as e:
            return {"error": str(e)}

    def add_multiple_to_collection(self, collection_name: str, file_paths: List[str]) -> Dict[str, Any]:
        """
        Add multiple files to a collection.

        Args:
            collection_name: Name of the collection
            file_paths: List of file paths

        Returns:
            Dictionary with operation result
        """
        try:
            for file_path in file_paths:
                self.memory.add_file_to_collection(collection_name, file_path)

            return {
                "success": True,
                "collection_name": collection_name,
                "files_added": len(file_paths),
                "message": f"Added {len(file_paths)} files to collection '{collection_name}'"
            }
        except Exception as e:
            return {"error": str(e)}

    def get_collection(self, collection_name: str) -> Dict[str, Any]:
        """
        Get all files in a collection.

        Args:
            collection_name: Name of the collection

        Returns:
            Dictionary with collection files
        """
        try:
            files = self.memory.get_collection_files(collection_name)
            return {
                "success": True,
                "collection_name": collection_name,
                "files": files,
                "count": len(files)
            }
        except Exception as e:
            return {"error": str(e)}

    def list_collections(self) -> Dict[str, Any]:
        """
        List all collections.

        Returns:
            Dictionary with all collections
        """
        try:
            collections = self.memory.get_all_collections()
            return {
                "success": True,
                "collections": collections,
                "count": len(collections)
            }
        except Exception as e:
            return {"error": str(e)}

    def create_from_search(self, collection_name: str, search_results: List[Dict[str, Any]],
                          description: str = "") -> Dict[str, Any]:
        """
        Create a collection from search results.

        Args:
            collection_name: Name for the new collection
            search_results: List of search result dictionaries
            description: Optional description

        Returns:
            Dictionary with operation result
        """
        try:
            # Create collection
            collection_id = self.memory.create_collection(collection_name, description)

            # Add files from search results
            file_paths = [result["file_path"] for result in search_results if "file_path" in result]
            for file_path in file_paths:
                self.memory.add_file_to_collection(collection_name, file_path)

            return {
                "success": True,
                "collection_name": collection_name,
                "collection_id": collection_id,
                "files_added": len(file_paths),
                "message": f"Created collection '{collection_name}' with {len(file_paths)} files"
            }
        except Exception as e:
            return {"error": str(e)}
