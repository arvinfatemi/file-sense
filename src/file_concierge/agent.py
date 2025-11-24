"""AI File Concierge agent using Google ADK.

This module defines the main agent for semantic file organization and search.
Uses pure Google ADK (Runner + InMemorySessionService) without Vertex AI dependency.
"""

# CRITICAL: Load environment variables BEFORE any google imports
# This ensures GOOGLE_API_KEY is available when google-genai initializes
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root (3 levels up from this file)
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'
load_dotenv(env_path)

# Verify API key is loaded
if not os.getenv('GOOGLE_API_KEY'):
    raise ValueError(
        f"GOOGLE_API_KEY not found in environment variables!\n"
        f"Expected .env file at: {env_path}\n"
        f"Please create .env file with your API key."
    )

# Now safe to import google-adk components
import asyncio
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from src.file_concierge.tools import ALL_TOOLS

# Define the root agent using Google ADK
root_agent = Agent(
    name="file_concierge",
    model="gemini-2.0-flash-exp",
    description=(
        "An intelligent file organization assistant that helps users search, tag, "
        "and organize files using natural language. Supports semantic search, "
        "AI-powered tagging, and virtual collections."
    ),
    instruction=(
        "You are an AI File Concierge, a helpful assistant for organizing and searching files. "
        "\n\n"
        "Your capabilities include:\n"
        "1. **Semantic Search**: Search files using natural language queries, understanding context and meaning\n"
        "2. **Smart Tagging**: Suggest and apply relevant tags to files for better organization\n"
        "3. **Collections**: Create virtual collections to group related files\n"
        "4. **File Operations**: List, read, and browse files in the sandbox\n"
        "\n"
        "When helping users:\n"
        "- Always be proactive in suggesting organization strategies\n"
        "- Explain your reasoning when creating tags or collections\n"
        "- Present search results clearly with relevant metadata\n"
        "- Use semantic search when users ask for files by topic or content\n"
        "- Suggest creating collections when multiple related files are found\n"
        "- Apply tags thoughtfully based on file content and context\n"
        "\n"
        "Communication style:\n"
        "- Be concise but informative\n"
        "- Use bullet points for multiple results\n"
        "- Always confirm actions taken (e.g., 'I've applied 3 tags to your file')\n"
        "- Ask clarifying questions when user intent is unclear\n"
        "\n"
        "Example interactions:\n"
        "- User: 'Find my Python files' → Use list_files or search_files\n"
        "- User: 'Find documents about machine learning' → Use search_files with semantic query\n"
        "- User: 'Tag this file' → Use suggest_tags first, then apply_tags with user confirmation\n"
        "- User: 'Create a collection for job stuff' → Search for job-related files, then create_collection\n"
    ),
    tools=ALL_TOOLS,
)

# Lazy initialization of Runner and SessionService
_runner = None
_session_service = None


def _get_runner():
    """Lazy initialization of Runner and SessionService to avoid premature setup."""
    global _runner, _session_service
    if _runner is None:
        _session_service = InMemorySessionService()
        _runner = Runner(
            agent=root_agent,
            app_name="file_concierge",
            session_service=_session_service
        )
    return _runner, _session_service


def query_agent(message: str, user_id: str = "default_user", session_id: str = "default_session") -> str:
    """
    Query the ADK agent with a message and return the response.

    Uses pure Google ADK (Runner + InMemorySessionService) without Vertex AI dependency.

    Args:
        message: User's message/query
        user_id: User identifier for session management
        session_id: Session identifier (defaults to "default_session")

    Returns:
        Agent's response as a string
    """
    async def _async_query():
        runner, session_service = _get_runner()

        # Create or get session (session methods are async)
        try:
            session = await session_service.get_session(
                app_name="file_concierge",
                user_id=user_id,
                session_id=session_id
            )
            if session is None:
                # Session doesn't exist, create it
                session = await session_service.create_session(
                    app_name="file_concierge",
                    user_id=user_id,
                    session_id=session_id
                )
        except Exception:
            # Session doesn't exist or error occurred, create it
            session = await session_service.create_session(
                app_name="file_concierge",
                user_id=user_id,
                session_id=session_id
            )

        # Create content from user message
        content = types.Content(role='user', parts=[types.Part(text=message)])

        # Run agent and collect response
        response_parts = []
        try:
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=content
            ):
                # Extract text from events
                if hasattr(event, 'content') and event.content:
                    if hasattr(event.content, 'parts'):
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                response_parts.append(part.text)

                # Check if this is the final response
                if hasattr(event, 'is_final_response') and event.is_final_response():
                    break

            # Join all response parts
            full_response = ''.join(response_parts).strip()
            return full_response if full_response else "No response generated."

        except Exception as e:
            return f"Error querying agent: {str(e)}"

    # Run async function in event loop
    try:
        return asyncio.run(_async_query())
    except RuntimeError:
        # Event loop already running (in async context)
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(_async_query())
