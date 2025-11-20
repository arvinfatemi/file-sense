"""Short-term memory for session context and conversation history."""

from typing import List, Dict, Any
from datetime import datetime


class ShortTermMemory:
    """Manages short-term memory for active session context."""

    def __init__(self):
        self.conversation_history: List[Dict[str, Any]] = []
        self.current_task: Dict[str, Any] = {}
        self.session_start = datetime.now()
        self.context_vars: Dict[str, Any] = {}

    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add a message to conversation history."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.conversation_history.append(message)

    def set_current_task(self, task_description: str, task_type: str = "general"):
        """Set the current task being worked on."""
        self.current_task = {
            "description": task_description,
            "type": task_type,
            "started_at": datetime.now().isoformat()
        }

    def clear_current_task(self):
        """Clear the current task."""
        self.current_task = {}

    def get_conversation_history(self, last_n: int = None) -> List[Dict[str, Any]]:
        """Get conversation history, optionally limited to last N messages."""
        if last_n:
            return self.conversation_history[-last_n:]
        return self.conversation_history

    def set_context_var(self, key: str, value: Any):
        """Set a context variable."""
        self.context_vars[key] = value

    def get_context_var(self, key: str, default: Any = None) -> Any:
        """Get a context variable."""
        return self.context_vars.get(key, default)

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []

    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the current session."""
        return {
            "session_start": self.session_start.isoformat(),
            "message_count": len(self.conversation_history),
            "current_task": self.current_task,
            "context_vars": self.context_vars
        }
