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

- Python 3.8 or higher
- Google API key for Gemini ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/file-sense.git
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
```

5. **Index the sandbox files**
```bash
python main.py index
```

6. **Start the interactive CLI**
```bash
python main.py interactive
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

### Agentic System

The system uses a multi-agent architecture with the **Orchestrator Agent** coordinating multiple specialized tools:

```
User Query → Orchestrator Agent → Tools (File, Search, Tag, Collection)
                ↓
          Short-term Memory (Conversation context)
                ↓
          Long-term Memory (SQLite + ChromaDB)
                ↓
          Sandbox Filesystem
```

### Tools

1. **File Tools** - Read, list, and extract metadata from files
2. **Search Tools** - Semantic search using vector embeddings
3. **Tag Tools** - AI-powered tag suggestion and management
4. **Collection Tools** - Create and manage file collections

### Memory

- **Short-term Memory**: Tracks conversation history and current session context
- **Long-term Memory**: Persists file metadata, tags, collections, and embeddings in SQLite and ChromaDB

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

- **Agent Framework**: Google ADK with Gemini
- **LLM**: Gemini 2.0 Flash
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Vector Store**: ChromaDB
- **Database**: SQLite
- **CLI**: Rich, Click
- **Language**: Python 3.8+

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
