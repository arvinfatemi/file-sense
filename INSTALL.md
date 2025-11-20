# Installation Guide

Complete installation instructions for AI File Concierge.

## System Requirements

- **Python**: 3.8 or higher
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: ~500MB for dependencies and embeddings
- **OS**: Linux, macOS, or Windows

## Step-by-Step Installation

### 1. Install Python

If you don't have Python installed:

**macOS:**
```bash
brew install python@3.11
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

**Windows:**
Download from [python.org](https://www.python.org/downloads/)

### 2. Clone the Repository

```bash
git clone https://github.com/yourusername/file-sense.git
cd file-sense
```

### 3. Create Virtual Environment

```bash
python3 -m venv venv

# Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- Google Generative AI SDK
- ChromaDB (vector database)
- Sentence Transformers (for embeddings)
- Rich (for CLI formatting)
- SQLAlchemy (for database)
- And other dependencies

### 5. Get Google API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy your API key

### 6. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API key
# On Linux/macOS:
nano .env

# On Windows:
notepad .env
```

Add your API key:
```
GOOGLE_API_KEY=your_actual_api_key_here
```

### 7. Initialize the System

Index the sample files in the sandbox:

```bash
python main.py index
```

You should see output like:
```
Indexing files in sandbox...
Processing files... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%
Indexing complete!
  • Files indexed: 8
  • Files in vector store: 8
```

### 8. Test the Installation

Run the interactive CLI:

```bash
python main.py interactive
```

Try a test query:
```
You: Find my Python files
```

If you see a response from the agent, your installation is successful!

## Troubleshooting

### Issue: "No module named 'google.generativeai'"

**Solution:** Make sure you've activated the virtual environment and installed dependencies:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: "GOOGLE_API_KEY not configured"

**Solution:** Check that your .env file exists and contains the API key:
```bash
cat .env  # Linux/macOS
type .env  # Windows
```

### Issue: ChromaDB errors on Apple Silicon (M1/M2)

**Solution:** You may need to install additional dependencies:
```bash
pip install --upgrade chromadb
```

### Issue: Sentence Transformers download fails

**Solution:** The first run downloads the embedding model (~80MB). Ensure you have internet connection and try:
```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Issue: Permission errors when indexing

**Solution:** Ensure the sandbox directory has proper permissions:
```bash
chmod -R 755 sandbox
```

## Verifying Installation

Run the evaluation suite to verify everything works:

```bash
python evaluation/test_scenarios.py
```

You should see test results for search accuracy, tagging quality, and workflow scenarios.

## Uninstallation

To remove the application:

```bash
# Deactivate virtual environment
deactivate

# Remove the project directory
cd ..
rm -rf file-sense
```

## Next Steps

- Read the [README.md](README.md) for usage examples
- Try the example queries
- Explore the [evaluation scripts](evaluation/)
- Check out [PRODUCTION_SCALING.md](PRODUCTION_SCALING.md) for scaling ideas

## Getting Help

If you encounter issues:
1. Check this troubleshooting section
2. Review the [README.md](README.md)
3. Open an issue on GitHub
4. Check the Kaggle course forums
