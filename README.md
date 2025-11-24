# AI File Concierge (AFC)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**An intelligent agentic system for semantic file organization and search**

AI File Concierge is a capstone project for the [Kaggle 5-Day GenAI Agents Intensive](https://www.kaggle.com/learn-guide/5-day-agents) that demonstrates how agent-based reasoning, tools, and memory enable smarter file organization through natural language interaction.

## Features

✨ **Natural Language Search** - Find files using semantic queries instead of exact filenames
🏷️ **Smart Tagging** - AI-powered tag suggestions for automatic file organization
📁 **Virtual Collections** - Create dynamic file collections based on search results or tags
🤖 **Agentic Architecture** - Multi-agent system using Google ADK and Gemini
💾 **Persistent Memory** - Short-term (session) and long-term (database) memory systems
🔍 **Vector Search** - Semantic search powered by sentence transformers and ChromaDB

## Quick Start

### Prerequisites

- Python 3.10 or higher (required for Google ADK)
- Google API key for Gemini ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/arvinfatemi/file-sense.git
cd file-sense
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
# Ensure GOOGLE_GENAI_USE_VERTEXAI=FALSE for API key usage
```

5. **Index the sandbox files**
```bash
python main.py index
```

6. **Start the interactive CLI**

#### Option A: Custom CLI

```bash
python main.py interactive
```

#### Option B: Google ADK Web UI

```bash
adk web src/file_concierge
```

#### Option C: Google ADK Terminal

```bash
adk run src/file_concierge
```

## Usage Examples

### Interactive Mode

```bash
$ python main.py interactive

You: Find my Python files

Agent: I found 2 Python files in your sandbox:
1. code/ml_experiment.py - Bayesian A/B testing implementation
2. code/data_processing.py - ETL utilities with pandas

You: Create a collection for all machine learning related files

Agent: I've created a collection called "Machine Learning" with 1 file:
- code/ml_experiment.py

You: Suggest tags for documents/resume.txt

Agent: I suggest the following tags for documents/resume.txt:
- career
- resume
- software-engineering
- job-search

Would you like me to apply these tags?
```

### Command-Line Interface

```bash
# Index all files
python main.py index

# Search files
python main.py search "machine learning notes"

# View statistics
python main.py stats
```

### Example Queries

- `"Find my Bayesian A/B testing notes"`
- `"Show everything related to job applications"`
- `"Search for documents about transformers and attention"`
- `"Create a collection for all Python code files"`
- `"What files do I have about machine learning?"`

## Project Structure

```
file-sense/
├── src/
│   ├── agents/           # Agent architecture
│   │   ├── orchestrator.py    # Main orchestrator agent
│   │   └── file_concierge.py  # System coordinator
│   ├── tools/            # Agent tools
│   │   ├── file_tools.py       # File operations
│   │   ├── search_tools.py     # Semantic search
│   │   ├── tag_tools.py        # Tagging operations
│   │   └── collection_tools.py # Collection management
│   ├── memory/           # Memory systems
│   │   ├── short_term.py       # Session memory
│   │   └── long_term.py        # Persistent storage
│   ├── indexing/         # File processing
│   │   ├── file_processor.py   # Metadata extraction
│   │   └── vector_store.py     # Vector embeddings
│   └── ui/               # User interface
│       └── cli.py              # Command-line interface
├── sandbox/              # Sandboxed file directory
│   ├── documents/        # Sample documents
│   ├── code/            # Sample code files
│   ├── notes/           # Sample notes
│   └── misc/            # Miscellaneous files
├── config/              # Configuration
├── evaluation/          # Evaluation scripts
├── tests/              # Unit tests
├── main.py             # Entry point
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Architecture

### Agentic System Overview

The system implements an **agentic architecture** using Google's Agent Development Kit (ADK), where an intelligent agent coordinates multiple specialized tools to accomplish user requests.

```
┌─────────────────────────────────────────────────────────────┐
│                          USER                                │
│                "Find my machine learning files"              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  GOOGLE ADK AGENT                            │
│                 (Gemini 2.0 Flash)                          │
│                                                              │
│  • Understands natural language intent                      │
│  • Reasons about which tools to use                         │
│  • Executes tools with appropriate parameters               │
│  • Synthesizes coherent responses                           │
│                                                              │
│  Agent Definition:                                          │
│    Agent(                                                   │
│      name="file_concierge",                                │
│      model="gemini-2.0-flash-exp",                         │
│      tools=[9 specialized functions]                       │
│    )                                                        │
└────────────────────────┬────────────────────────────────────┘
                         │
            ┌────────────┴────────────┐
            │    Tool Selection       │
            │  & Execution Engine     │
            └────────────┬────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Search Tools │  │  Tag Tools   │  │ Collection   │
│              │  │              │  │   Tools      │
│ • search_    │  │ • suggest_   │  │ • create_    │
│   files      │  │   tags       │  │   collection │
│ • list_      │  │ • apply_tags │  │ • add_to_    │
│   files      │  │ • get_file_  │  │   collection │
│ • read_file  │  │   tags       │  │ • get_       │
│              │  │              │  │   collection_│
│              │  │              │  │   files      │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
        ▼                                 ▼
┌──────────────────┐            ┌──────────────────┐
│  Vector Store    │            │  Long-term       │
│  (ChromaDB)      │            │  Memory          │
│                  │            │  (SQLite)        │
│  • Embeddings    │            │                  │
│  • Semantic      │            │  Tables:         │
│    search        │            │  • file_metadata │
│  • Similarity    │            │  • tags          │
│    scoring       │            │  • file_tags     │
│                  │            │  • collections   │
│  Model:          │            │  • coll_files    │
│  SentenceXfrmr   │            │                  │
└──────────────────┘            └──────────────────┘
        │                                 │
        └────────────────┬────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    SANDBOX FILESYSTEM                        │
│                                                              │
│  sandbox/                                                    │
│  ├── documents/  (resumes, papers, letters)                │
│  ├── code/       (Python ML & data scripts)                │
│  ├── notes/      (meeting notes, ideas)                    │
│  └── misc/       (todos, etc.)                             │
└─────────────────────────────────────────────────────────────┘
```

### Agentic Workflow Example

Here's how the system processes: **"Find my machine learning files"**

```
1. USER INPUT
   └─> "Find my machine learning files"

2. AGENT REASONING (Gemini 2.0 Flash via ADK)
   ├─> Analyzes intent: User wants semantic file search
   ├─> Selects tool: search_files()
   └─> Determines parameters:
       {
         "query": "machine learning",
         "tags": null,
         "top_k": 10
       }

3. TOOL EXECUTION
   ├─> search_files() is invoked
   ├─> Generates embedding for "machine learning"
   ├─> Queries ChromaDB vector store
   ├─> Retrieves similar documents by cosine similarity
   ├─> Enriches with tags from SQLite
   └─> Returns results with metadata

4. AGENT SYNTHESIS
   ├─> Receives structured tool output
   ├─> Formats into natural language
   └─> Generates user-friendly response:

       "I found 2 files about machine learning:

        1. code/ml_experiment.py (87% match)
           - Bayesian A/B testing implementation
           - Tags: python, bayesian, statistics

        2. notes/project_ideas.txt (72% match)
           - AI File Organizer project idea
           - Tags: ideas, personal"

5. USER RECEIVES RESPONSE
   └─> Displayed in CLI or ADK web interface
```

### Tool Categories

The agent has access to **9 specialized tools** organized by function:

#### 1. Search & Discovery Tools

- **`search_files(query, tags, top_k)`** - Semantic search using vector embeddings
- **`list_files(directory, pattern)`** - Browse sandbox directory structure
- **`read_file(file_path)`** - Read full file contents

#### 2. Tagging Tools

- **`suggest_tags(file_path)`** - AI-powered tag recommendations
- **`apply_tags(file_path, tags)`** - Apply tags to files
- **`get_file_tags(file_path)`** - Retrieve file's current tags

#### 3. Collection Tools

- **`create_collection(name, description)`** - Create new file collections
- **`add_to_collection(collection_name, file_paths)`** - Add files to collections
- **`get_collection_files(collection_name)`** - List collection contents

### Memory Systems

The system employs two complementary memory systems:

#### Conversation Memory (Managed by ADK)

- Automatically maintained by Google ADK
- Tracks conversation history and context
- Enables multi-turn interactions
- No manual management required

#### Persistent Memory (Long-term Storage)

##### Vector Store (ChromaDB)

- Stores file content embeddings (384-dimensional vectors)
- Enables semantic similarity search
- Fast nearest-neighbor lookup
- Supports metadata filtering

##### Relational Database (SQLite)

- File metadata and indexing information
- Tag definitions and file-tag associations
- Collection definitions and memberships
- Queryable with SQL for complex operations

### Key Design Principles

1. **Declarative Agent Definition** - Agent behavior defined through configuration, not code
2. **Pure Function Tools** - Tools are simple, testable Python functions
3. **Automatic Schema Inference** - ADK infers tool schemas from type hints
4. **Separation of Concerns** - Clear boundaries between agent logic, tools, and storage
5. **Extensibility** - Easy to add new tools by writing functions

## Evaluation

Run the evaluation suite to test system performance:

```bash
python evaluation/test_scenarios.py
```

The evaluation tests:
- **Search Accuracy** (Hit@K metrics)
- **Tag Quality** (Relevance scoring)
- **Workflow Scenarios** (End-to-end operations)

See [evaluation/README.md](evaluation/README.md) for details.

<!-- ## Capstone Requirements

This project fulfills all capstone requirements:

✅ **Agentic Architecture** - Orchestrator agent with tool-based workflow
✅ **Tools** - 7+ specialized tools for file operations
✅ **Memory** - Short-term (session) and long-term (database) storage
✅ **Evaluation** - Automated test scenarios with metrics
✅ **Production Thinking** - See [PRODUCTION_SCALING.md](PRODUCTION_SCALING.md)
✅ **Public Repository** - Clean code, documentation, and examples -->

<!-- ## Production Scaling

For a detailed discussion of how to scale this prototype to production, see [PRODUCTION_SCALING.md](PRODUCTION_SCALING.md), which covers:

- Real filesystem integration via MCP
- Distributed vector databases (Pinecone, Weaviate)
- Cloud storage integration (Google Drive, Dropbox, etc.)
- Multimodal support (OCR, audio transcription, video)
- Security and privacy considerations
- Cost optimization strategies -->

## Technology Stack

- **Agent Framework**: [Google ADK (Agent Development Kit)](https://google.github.io/adk-docs/)
- **LLM**: Gemini 2.0 Flash Experimental
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Vector Store**: ChromaDB
- **Database**: SQLite
- **CLI**: Rich, Click
- **Language**: Python 3.10+

## Architecture with Google ADK

The system uses Google's Agent Development Kit (ADK) for agent orchestration:

### Agent Structure

```python
# src/file_concierge/agent.py
from google.adk.agents import Agent
from src.file_concierge.tools import ALL_TOOLS

root_agent = Agent(
    name="file_concierge",
    model="gemini-2.0-flash-exp",
    description="Intelligent file organization assistant",
    instruction="You are an AI File Concierge...",
    tools=ALL_TOOLS  # 9 specialized tools
)
```

### Tool Functions

Tools are simple Python functions that the agent can invoke:

```python
def search_files(query: str, tags: Optional[List[str]] = None, top_k: int = 10) -> dict:
    """Search for files using natural language queries and/or tags."""
    # Implementation...
```

ADK automatically:

- Infers tool schemas from function signatures
- Handles tool execution and error handling
- Manages conversation context
- Provides built-in logging and debugging

<!-- ## Limitations

This is a **prototype** with the following limitations:

- Operates only on a sandboxed directory (not real filesystem)
- Single-user, local-only (no multi-user support)
- No authentication or authorization
- Limited file type support (text files primarily)
- No cloud storage integration
- SQLite database (not production-scale)

See [PRODUCTION_SCALING.md](PRODUCTION_SCALING.md) for how to address these. -->

## Contributing

This is a capstone project, but suggestions and feedback are welcome! Please open an issue to discuss proposed changes.

## License

MIT License - see [LICENSE](LICENSE) for details.

<!-- ## Acknowledgments

- [Kaggle 5-Day GenAI Agents Intensive](https://www.kaggle.com/learn-guide/5-day-agents) for project inspiration
- [Google ADK](https://google.github.io/adk-docs/) for the agent framework
- Course instructors and community for guidance -->

## References

- [Capstone Project Details](https://www.kaggle.com/competitions/agents-intensive-capstone-project)
- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [Project Brief](STARTER.md)

---

**Built with ❤️ for the Kaggle GenAI Agents Intensive**
