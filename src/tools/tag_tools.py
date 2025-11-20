"""Tools for tagging operations."""

from typing import Dict, Any, List
import google.generativeai as genai
from src.memory.long_term import LongTermMemory
from config import config


class TagTools:
    """Tagging tools for agents."""

    def __init__(self, memory: LongTermMemory = None):
        self.memory = memory or LongTermMemory()

        # Configure Gemini for tag suggestions
        if config.GOOGLE_API_KEY:
            genai.configure(api_key=config.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel(config.GEMINI_MODEL)
        else:
            self.model = None

    def suggest_tags(self, file_path: str, content: str, existing_tags: List[str] = None) -> Dict[str, Any]:
        """
        Suggest tags for a file using LLM.

        Args:
            file_path: Path to the file
            content: File content
            existing_tags: Optional list of existing tags in the system

        Returns:
            Dictionary with suggested tags
        """
        if not self.model:
            return {"error": "Google API key not configured"}

        try:
            prompt = f"""Analyze the following file content and suggest 3-5 relevant tags.
Tags should be:
- Concise (1-2 words)
- Descriptive of the content or purpose
- Lowercase with hyphens (e.g., "machine-learning", "python", "personal")

File: {file_path}

Content:
{content[:1000]}...

"""
            if existing_tags:
                prompt += f"\nExisting tags in the system: {', '.join(existing_tags[:20])}\n"
                prompt += "Prefer using existing tags when appropriate, but suggest new ones if needed.\n"

            prompt += "\nProvide ONLY the tags as a comma-separated list, nothing else."

            response = self.model.generate_content(prompt)
            suggested_tags = [tag.strip().lower() for tag in response.text.split(",")]

            return {
                "success": True,
                "file_path": file_path,
                "suggested_tags": suggested_tags
            }
        except Exception as e:
            return {"error": str(e)}

    def apply_tag(self, file_path: str, tag: str) -> Dict[str, Any]:
        """
        Apply a tag to a file.

        Args:
            file_path: Path to the file
            tag: Tag to apply

        Returns:
            Dictionary with operation result
        """
        try:
            self.memory.tag_file(file_path, tag.lower())
            return {
                "success": True,
                "file_path": file_path,
                "tag": tag.lower(),
                "message": f"Tag '{tag}' applied to {file_path}"
            }
        except Exception as e:
            return {"error": str(e)}

    def apply_tags(self, file_path: str, tags: List[str]) -> Dict[str, Any]:
        """
        Apply multiple tags to a file.

        Args:
            file_path: Path to the file
            tags: List of tags to apply

        Returns:
            Dictionary with operation result
        """
        try:
            for tag in tags:
                self.memory.tag_file(file_path, tag.lower())

            return {
                "success": True,
                "file_path": file_path,
                "tags": [t.lower() for t in tags],
                "message": f"Applied {len(tags)} tags to {file_path}"
            }
        except Exception as e:
            return {"error": str(e)}

    def get_file_tags(self, file_path: str) -> Dict[str, Any]:
        """
        Get all tags for a file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with file tags
        """
        try:
            tags = self.memory.get_file_tags(file_path)
            return {
                "success": True,
                "file_path": file_path,
                "tags": tags,
                "count": len(tags)
            }
        except Exception as e:
            return {"error": str(e)}

    def get_all_tags(self) -> Dict[str, Any]:
        """
        Get all tags in the system.

        Returns:
            Dictionary with all tags
        """
        try:
            tags = self.memory.get_all_tags()
            return {
                "success": True,
                "tags": tags,
                "count": len(tags)
            }
        except Exception as e:
            return {"error": str(e)}

    def get_files_by_tag(self, tag: str) -> Dict[str, Any]:
        """
        Get all files with a specific tag.

        Args:
            tag: Tag name

        Returns:
            Dictionary with matching files
        """
        try:
            files = self.memory.get_files_by_tag(tag.lower())
            return {
                "success": True,
                "tag": tag.lower(),
                "files": files,
                "count": len(files)
            }
        except Exception as e:
            return {"error": str(e)}
