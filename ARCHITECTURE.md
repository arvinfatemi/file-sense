# Architecture Flow - AI File Concierge

This document explains the complete architecture and data flow of the AI File Concierge system using pure Google ADK (Runner + InMemorySessionService, no Vertex AI dependency).

## Visual Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER                                     │
│                    (Terminal/Browser)                            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│  Custom CLI              │  │  Google ADK CLI          │
│  main.py                 │  │  adk run / adk web       │
│  python main.py          │  │                          │
│  interactive             │  │  Provides:               │
│                          │  │  • Web UI                │
│  Commands:               │  │  • Terminal chat         │
│  • index                 │  │  • Built-in logging      │
│  • stats                 │  │  • Debug tools           │
│  • reindex               │  │                          │
│  • <natural query>       │  │                          │
└───────────┬──────────────┘  └────────────┬─────────────┘
            │                              │
            │        Both route to         │
            └──────────────┬───────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Google ADK Agent (src/file_concierge/agent.py)                 │
│                                                                  │
│  from google.adk.agents import Agent                            │
│  from google.adk.runners import Runner                          │
│  from google.adk.sessions import InMemorySessionService         │
│                                                                  │
│  root_agent = Agent(                                            │
│      name="file_concierge",                                     │
│      model="gemini-2.0-flash-exp",                             │
│      tools=[9 tool functions]                                   │
│  )                                                              │
│                                                                  │
│  runner = Runner(                                               │
│      agent=root_agent,                                          │
│      session_service=InMemorySessionService()                   │
│  )                                                              │
│                                                                  │
│  Responsibilities:                                              │
│  • Understand user intent                                       │
│  • Select appropriate tools                                     │
│  • Execute tools with parameters                                │
│  • Synthesize responses                                         │
│  • Handle multi-turn conversations                              │
│  • Manage session state (via InMemorySessionService)            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Tool Functions (src/file_concierge/tools.py)                   │
│                                                                  │
│  9 callable Python functions:                                   │
│                                                                  │
│  1. search_files(query, tags, top_k)                           │
│     → Semantic search using vector embeddings                   │
│                                                                  │
│  2. suggest_tags(file_path)                                     │
│     → AI-powered tag suggestions                                │
│                                                                  │
│  3. apply_tags(file_path, tags)                                │
│     → Apply tags to files                                       │
│                                                                  │
│  4. get_file_tags(file_path)                                    │
│     → Retrieve file's tags                                      │
│                                                                  │
│  5. create_collection(name, description)                        │
│     → Create new file collection                                │
│                                                                  │
│  6. add_to_collection(collection_name, file_paths)             │
│     → Add files to collection                                   │
│                                                                  │
│  7. get_collection_files(collection_name)                       │
│     → List collection contents                                  │
│                                                                  │
│  8. list_files(directory, pattern)                              │
│     → Browse sandbox files                                      │
│                                                                  │
│  9. read_file(file_path)                                        │
│     → Read file contents                                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
┌──────────────────┐ ┌──────────────┐ ┌────────────────┐
│  VectorStore     │ │  LongTerm    │ │  FileProcessor │
│  (ChromaDB)      │ │  Memory      │ │                │
│                  │ │  (SQLite)    │ │  Extracts:     │
│  Stores:         │ │              │ │  • Metadata    │
│  • Embeddings    │ │  Tables:     │ │  • Text        │
│  • File content  │ │  • metadata  │ │  • Categories  │
│  • Metadata      │ │  • tags      │ │                │
│                  │ │  • file_tags │ │  Handles:      │
│  Operations:     │ │  • collections│ │  • .txt, .md   │
│  • add_document  │ │  • coll_files│ │  • .py, .java  │
│  • search        │ │              │ │  • .pdf, .docx │
│  • update        │ │  Operations: │ │  • etc.        │
│  • delete        │ │  • store     │ │                │
│                  │ │  • retrieve  │ │                │
│                  │ │  • tag       │ │                │
│                  │ │  • collect   │ │                │
└──────────────────┘ └──────────────┘ └────────────────┘
          │                 │                 │
          └─────────────────┼─────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Sandbox Filesystem                                              │
│  (sandbox/)                                                      │
│                                                                  │
│  ├── documents/                                                  │
│  │   ├── resume.txt                                             │
│  │   ├── cover_letter.txt                                       │
│  │   └── research_paper_notes.md                                │
│  ├── code/                                                       │
│  │   ├── ml_experiment.py                                       │
│  │   └── data_processing.py                                     │
│  ├── notes/                                                      │
│  │   ├── meeting_notes.txt                                      │
│  │   └── project_ideas.txt                                      │
│  └── misc/                                                       │
│      └── todo.txt                                                │
└─────────────────────────────────────────────────────────────────┘
```

## Detailed Flow: Example Query

### Scenario: User asks "Find documents about machine learning"

```
1. USER INPUT
   └─> "Find documents about machine learning"

2. CLI/ADK receives input
   └─> Routes to root_agent.query()

3. GOOGLE ADK AGENT (Gemini 2.0 Flash)
   ├─> Understands intent: semantic search needed
   ├─> Selects tool: search_files
   └─> Generates parameters:
       {
         "query": "machine learning",
         "tags": null,
         "top_k": 10
       }

4. TOOL EXECUTION: search_files()
   ├─> Receives parameters from agent
   ├─> Generates embedding for "machine learning"
   ├─> Queries VectorStore (ChromaDB)
   │   └─> Performs cosine similarity search
   │       └─> Returns top matches with scores
   ├─> Enriches results with tags from LongTermMemory
   └─> Returns:
       {
         "status": "success",
         "results": [
           {
             "file_path": "code/ml_experiment.py",
             "similarity": 0.87,
             "tags": ["python", "bayesian", "statistics"],
             "content": "Bayesian A/B testing..."
           },
           {
             "file_path": "notes/project_ideas.txt",
             "similarity": 0.72,
             "tags": ["ideas", "personal"],
             "content": "AI File Organizer - Use LLMs..."
           }
         ],
         "count": 2
       }

5. AGENT SYNTHESIS
   ├─> Receives tool results
   ├─> Formats response naturally
   └─> Returns to user:
       "I found 2 files about machine learning:

        1. code/ml_experiment.py (87% match)
           - Bayesian A/B testing implementation
           - Tags: python, bayesian, statistics

        2. notes/project_ideas.txt (72% match)
           - Project ideas including ML file organizer
           - Tags: ideas, personal"

6. OUTPUT TO USER
   └─> Displays in CLI or ADK web interface
```

## Key Concepts

### 1. **Google ADK Agent**

The agent is the "brain" of the system:

```python
# src/file_concierge/agent.py
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

root_agent = Agent(
    name="file_concierge",
    model="gemini-2.0-flash-exp",
    description="Intelligent file organization assistant",
    instruction="You are an AI File Concierge that helps...",
    tools=ALL_TOOLS
)

# Pure ADK setup (no Vertex AI)
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name="file_concierge",
    session_service=session_service
)

# Query execution
async for event in runner.run_async(
    user_id="user_1",
    session_id="session_1",
    new_message=types.Content(role='user', parts=[types.Part(text=query)])
):
    # Process events
```

**What Pure ADK provides:**
- Tool schema inference from function signatures
- Function calling (selecting which tool to use)
- Parameter extraction from natural language
- Error handling and retries
- Session management via InMemorySessionService
- Event streaming for real-time responses
- No Vertex AI/GCP dependencies

### 2. **Tool Functions**

Simple Python functions that do the actual work:

```python
# src/file_concierge/tools.py
def search_files(query: str, tags: Optional[List[str]] = None, top_k: int = 10) -> dict:
    """Search for files using natural language queries and/or tags."""
    results = _vector_store.search(query, top_k=top_k)
    # Process and return results
    return {"status": "success", "results": results}
```

**Key characteristics:**
- Pure Python functions (no special decorators needed)
- Type hints for ADK schema inference
- Docstrings for tool descriptions
- Return structured dictionaries
- Handle errors gracefully

### 3. **Memory Systems**

Two types of memory:

**Short-term (Not currently used in ADK version):**
- Handled automatically by ADK
- Conversation history
- Session context

**Long-term (SQLite):**
- File metadata
- Tags and their associations
- Collections
- Persistent across sessions

### 4. **Vector Search**

ChromaDB stores embeddings for semantic search:

```python
# When indexing:
embedding = sentence_transformer.encode(file_content)
chromadb.add(file_path, embedding, metadata)

# When searching:
query_embedding = sentence_transformer.encode(user_query)
results = chromadb.search(query_embedding, top_k=10)
```

## Module Dependencies

```
main.py
  └─> src/ui/cli.py
        ├─> src/file_concierge/agent.py (Google ADK Agent)
        │     └─> src/file_concierge/tools.py
        │           ├─> src/indexing/vector_store.py
        │           │     └─> chromadb
        │           ├─> src/memory/long_term.py
        │           │     └─> sqlite3
        │           └─> src/indexing/file_processor.py
        │                 └─> file reading utilities
        └─> src/file_concierge/indexer.py
              ├─> src/indexing/file_processor.py
              ├─> src/indexing/vector_store.py
              └─> src/memory/long_term.py
```

## Import Flow

```python
# Entry point
from src.ui.cli import cli

# CLI imports
from src.file_concierge.agent import query_agent  # Pure ADK query function
from src.file_concierge.indexer import FileIndexer

# Agent imports (pure ADK)
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from src.file_concierge.tools import ALL_TOOLS

# Tools import
from src.memory.long_term import LongTermMemory
from src.indexing.vector_store import VectorStore
from src.indexing.file_processor import FileProcessor
from config import config
```

## Data Persistence

### Files Created During Operation

```
project-root/
├── data/
│   ├── chroma/              ← ChromaDB vector database
│   │   ├── index/
│   │   └── metadata/
│   └── memory.db            ← SQLite database
│       ├── file_metadata
│       ├── tags
│       ├── file_tags
│       ├── collections
│       └── collection_files
```

### SQLite Schema

```sql
file_metadata
├── id (PK)
├── file_path (unique)
├── file_name
├── file_type
├── file_size
├── created_at
├── modified_at
├── indexed_at
├── text_sample
└── embedding_id

tags
├── id (PK)
├── tag_name (unique)
└── created_at

file_tags
├── id (PK)
├── file_path (FK)
├── tag_id (FK)
└── applied_at

collections
├── id (PK)
├── collection_name (unique)
├── description
├── created_at
└── updated_at

collection_files
├── id (PK)
├── collection_id (FK)
├── file_path
└── added_at
```

## Benefits of Pure ADK Architecture

### Before (Manual Implementation)
- ❌ Manual tool schema definition (~100 lines)
- ❌ Custom function calling loop
- ❌ Manual tool dispatching logic
- ❌ Custom error handling
- ❌ Manual conversation management

### After (Pure Google ADK)
- ✅ Automatic schema inference
- ✅ Built-in function calling
- ✅ Automatic tool dispatching
- ✅ Robust error handling
- ✅ Session management via InMemorySessionService
- ✅ Event streaming for real-time responses
- ✅ Built-in logging and debugging
- ✅ Web UI out of the box (`adk web`)
- ✅ No Vertex AI/GCP dependencies
- ✅ Works with just GOOGLE_API_KEY

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| File indexing | ~1-2s per file | Includes embedding generation |
| Semantic search | <100ms | Vector similarity search |
| Tool execution | 10-50ms | Direct function calls |
| Agent query (simple) | ~2-3s | LLM call + tool execution |
| Agent query (complex) | ~5-10s | Multiple tool calls |

## Scalability Considerations

See [PRODUCTION_SCALING.md](PRODUCTION_SCALING.md) for detailed discussion of:
- Distributed vector databases
- Cloud deployment
- Multi-user support
- Real filesystem integration
- Production optimizations
