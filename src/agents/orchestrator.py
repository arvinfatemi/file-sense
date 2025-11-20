"""Orchestrator agent for coordinating file concierge operations."""

import google.generativeai as genai
from typing import Dict, Any, List
from src.memory.short_term import ShortTermMemory
from src.memory.long_term import LongTermMemory
from src.tools.file_tools import FileTools
from src.tools.search_tools import SearchTools
from src.tools.tag_tools import TagTools
from src.tools.collection_tools import CollectionTools
from src.indexing.vector_store import VectorStore
from config import config


class OrchestratorAgent:
    """Main orchestrator agent that coordinates file operations."""

    def __init__(self):
        # Initialize memory systems
        self.short_term_memory = ShortTermMemory()
        self.long_term_memory = LongTermMemory()
        self.vector_store = VectorStore()

        # Initialize tools
        self.file_tools = FileTools()
        self.search_tools = SearchTools(self.vector_store, self.long_term_memory)
        self.tag_tools = TagTools(self.long_term_memory)
        self.collection_tools = CollectionTools(self.long_term_memory)

        # Configure Gemini
        if config.GOOGLE_API_KEY:
            genai.configure(api_key=config.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel(
                config.GEMINI_MODEL,
                tools=[
                    self._create_tool_declarations()
                ]
            )
        else:
            self.model = None

    def _create_tool_declarations(self) -> List[Dict[str, Any]]:
        """Create tool declarations for Gemini function calling."""
        return [
            {
                "name": "search_files",
                "description": "Search for files using natural language queries and/or tags",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Natural language search query"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of tags to filter by"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of results to return (default 10)"
                        }
                    }
                }
            },
            {
                "name": "suggest_tags",
                "description": "Suggest tags for a file based on its content",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file"
                        }
                    },
                    "required": ["file_path"]
                }
            },
            {
                "name": "apply_tags",
                "description": "Apply one or more tags to a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of tags to apply"
                        }
                    },
                    "required": ["file_path", "tags"]
                }
            },
            {
                "name": "create_collection",
                "description": "Create a new collection of files",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Collection name"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional description"
                        }
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "add_to_collection",
                "description": "Add files to an existing collection",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "collection_name": {
                            "type": "string",
                            "description": "Name of the collection"
                        },
                        "file_paths": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of file paths to add"
                        }
                    },
                    "required": ["collection_name", "file_paths"]
                }
            },
            {
                "name": "read_file",
                "description": "Read the full content of a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file"
                        }
                    },
                    "required": ["file_path"]
                }
            },
            {
                "name": "list_files",
                "description": "List files in a directory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "Directory path (relative to sandbox)"
                        },
                        "pattern": {
                            "type": "string",
                            "description": "Glob pattern for filtering (default: *)"
                        }
                    }
                }
            }
        ]

    def _execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool based on its name and arguments."""
        if tool_name == "search_files":
            query = tool_args.get("query")
            tags = tool_args.get("tags")
            top_k = tool_args.get("top_k")
            return self.search_tools.combined_search(query, tags, top_k)

        elif tool_name == "suggest_tags":
            file_path = tool_args["file_path"]
            # Read file content first
            file_content = self.file_tools.read_file(file_path)
            if not file_content.get("success"):
                return file_content
            existing_tags = self.tag_tools.get_all_tags().get("tags", [])
            return self.tag_tools.suggest_tags(
                file_path,
                file_content.get("content", ""),
                existing_tags
            )

        elif tool_name == "apply_tags":
            return self.tag_tools.apply_tags(
                tool_args["file_path"],
                tool_args["tags"]
            )

        elif tool_name == "create_collection":
            return self.collection_tools.create_collection(
                tool_args["name"],
                tool_args.get("description", "")
            )

        elif tool_name == "add_to_collection":
            return self.collection_tools.add_multiple_to_collection(
                tool_args["collection_name"],
                tool_args["file_paths"]
            )

        elif tool_name == "read_file":
            return self.file_tools.read_file(tool_args["file_path"])

        elif tool_name == "list_files":
            return self.file_tools.list_files(
                tool_args.get("directory", ""),
                tool_args.get("pattern", "*")
            )

        else:
            return {"error": f"Unknown tool: {tool_name}"}

    def process_query(self, user_query: str) -> str:
        """
        Process a user query using the orchestrator agent.

        Args:
            user_query: User's natural language query

        Returns:
            Response from the agent
        """
        if not self.model:
            return "Error: Google API key not configured. Please set GOOGLE_API_KEY in .env file."

        # Add to conversation history
        self.short_term_memory.add_message("user", user_query)

        try:
            # Create conversation context
            conversation = [
                {
                    "role": "user",
                    "parts": [self._create_system_prompt() + "\n\nUser query: " + user_query]
                }
            ]

            # Start chat with function calling
            chat = self.model.start_chat(history=[])
            response = chat.send_message(conversation[0]["parts"][0])

            # Handle function calls
            while response.candidates[0].content.parts[0].function_call:
                function_call = response.candidates[0].content.parts[0].function_call
                tool_name = function_call.name
                tool_args = dict(function_call.args)

                # Execute the tool
                tool_result = self._execute_tool(tool_name, tool_args)

                # Send result back to model
                response = chat.send_message(
                    genai.protos.Content(
                        parts=[genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=tool_name,
                                response={"result": tool_result}
                            )
                        )]
                    )
                )

            # Get final text response
            final_response = response.text

            # Add to conversation history
            self.short_term_memory.add_message("assistant", final_response)

            return final_response

        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            self.short_term_memory.add_message("system", error_msg)
            return error_msg

    def _create_system_prompt(self) -> str:
        """Create the system prompt for the orchestrator."""
        return """You are an AI File Concierge assistant helping users organize and search their files.

You have access to tools for:
- Semantic search over file contents
- Tag suggestion and management
- Collection creation and management
- File reading and listing

When users ask you to:
1. Search for files: Use search_files with appropriate query and/or tags
2. Organize files: Suggest and apply tags, create collections
3. Find specific information: Read files and search semantically

Be helpful, concise, and proactive in suggesting organization strategies.
Always present search results in a clear, organized manner.
When creating collections or applying tags, explain your reasoning."""
