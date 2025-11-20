"""Tools for semantic search operations."""

from typing import Dict, Any, List
from src.indexing.vector_store import VectorStore
from src.memory.long_term import LongTermMemory
from config import config


class SearchTools:
    """Search tools for agents."""

    def __init__(self, vector_store: VectorStore = None, memory: LongTermMemory = None):
        self.vector_store = vector_store or VectorStore()
        self.memory = memory or LongTermMemory()

    def semantic_search(self, query: str, top_k: int = None) -> Dict[str, Any]:
        """
        Perform semantic search over indexed files.

        Args:
            query: Natural language search query
            top_k: Number of results to return

        Returns:
            Dictionary with search results
        """
        top_k = top_k or config.TOP_K_RESULTS

        try:
            results = self.vector_store.search(query, top_k=top_k)

            # Enrich results with tags from long-term memory
            enriched_results = []
            for result in results:
                file_path = result["file_path"]
                tags = self.memory.get_file_tags(file_path)
                result["tags"] = tags
                enriched_results.append(result)

            return {
                "success": True,
                "query": query,
                "results": enriched_results,
                "count": len(enriched_results)
            }
        except Exception as e:
            return {"error": str(e)}

    def search_by_tags(self, tags: List[str]) -> Dict[str, Any]:
        """
        Search for files by tags.

        Args:
            tags: List of tag names

        Returns:
            Dictionary with matching files
        """
        try:
            # Get files for each tag
            files_by_tag = {}
            for tag in tags:
                files = self.memory.get_files_by_tag(tag)
                files_by_tag[tag] = files

            # Find intersection (files with all tags)
            if files_by_tag:
                all_files = set(files_by_tag[tags[0]])
                for tag in tags[1:]:
                    all_files &= set(files_by_tag[tag])
                matching_files = list(all_files)
            else:
                matching_files = []

            # Get metadata for matching files
            results = []
            for file_path in matching_files:
                metadata = self.memory.get_file_metadata(file_path)
                if metadata:
                    metadata["tags"] = self.memory.get_file_tags(file_path)
                    results.append(metadata)

            return {
                "success": True,
                "tags": tags,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            return {"error": str(e)}

    def combined_search(self, query: str = None, tags: List[str] = None, top_k: int = None) -> Dict[str, Any]:
        """
        Perform combined semantic and tag-based search.

        Args:
            query: Optional semantic search query
            tags: Optional list of tags
            top_k: Number of results to return

        Returns:
            Dictionary with combined search results
        """
        results = []

        try:
            # Perform semantic search if query provided
            if query:
                semantic_results = self.semantic_search(query, top_k)
                if semantic_results.get("success"):
                    results.extend(semantic_results["results"])

            # Perform tag search if tags provided
            if tags:
                tag_results = self.search_by_tags(tags)
                if tag_results.get("success"):
                    # Merge with semantic results
                    tag_file_paths = {r["file_path"] for r in tag_results["results"]}

                    # Boost semantic results that also have matching tags
                    for result in results:
                        if result["file_path"] in tag_file_paths:
                            result["tag_match"] = True
                            if "similarity" in result:
                                result["similarity"] += 0.2  # Boost score

                    # Add tag-only results
                    semantic_paths = {r["file_path"] for r in results}
                    for tag_result in tag_results["results"]:
                        if tag_result["file_path"] not in semantic_paths:
                            tag_result["similarity"] = 0.5
                            tag_result["tag_match"] = True
                            results.append(tag_result)

            # Sort by similarity
            results.sort(key=lambda x: x.get("similarity", 0), reverse=True)

            if top_k:
                results = results[:top_k]

            return {
                "success": True,
                "query": query,
                "tags": tags,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            return {"error": str(e)}
