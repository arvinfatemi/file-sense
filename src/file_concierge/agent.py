"""AI File Concierge agent using Google ADK.

This module defines the main agent for semantic file organization and search.
"""

import asyncio
from google.adk.agents import Agent
from vertexai.agent_engines import AdkApp
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

# Lazy initialization of AdkApp
_app = None

def _get_app():
    """Lazy initialization of AdkApp to avoid premature authentication."""
    global _app
    if _app is None:
        _app = AdkApp(agent=root_agent)
    return _app


def query_agent(message: str, user_id: str = "default_user") -> str:
    """
    Query the ADK agent with a message and return the response.

    Args:
        message: User's message/query
        user_id: User identifier for session management

    Returns:
        Agent's response as a string
    """
    async def _async_query():
        response_parts = []
        try:
            app = _get_app()  # Get or initialize AdkApp
            async for event in app.async_stream_query(
                user_id=user_id,
                message=message
            ):
                # Extract content from streaming events
                if isinstance(event, dict):
                    # Check for different event types
                    if 'content' in event:
                        content = event['content']
                        if isinstance(content, str):
                            response_parts.append(content)
                        elif hasattr(content, 'text'):
                            response_parts.append(content.text)
                    elif 'text' in event:
                        response_parts.append(event['text'])

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
