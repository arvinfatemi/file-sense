# Troubleshooting: Agent Cannot Find Files

## Problem
The ADK agent returns "cannot find files" or file operations fail when running the File Concierge agent.

## Root Cause
The issue was caused by **relative path resolution** in the configuration that broke when the ADK changed working directories during agent execution.

## Fixes Applied

### 1. Fixed Path Resolution in `config/config.py`
**Changed from relative to absolute paths:**
```python
# Before (relative):
PROJECT_ROOT = Path(__file__).parent.parent

# After (absolute):
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
SANDBOX_DIR = (PROJECT_ROOT / "sandbox").resolve()
DATA_DIR = (PROJECT_ROOT / "data").resolve()
```

**Added path validation:**
- New `validate_paths()` method checks that directories exist
- Automatically called on module import
- Provides clear error messages with actual paths

### 2. Added Validation to `src/file_concierge/tools.py`
**Module-level validation:**
- Checks sandbox directory exists before tool initialization
- Logs all resolved paths for debugging
- Provides clear error messages if paths are wrong

**Enhanced error messages:**
- File operation errors now show both relative and resolved absolute paths
- Makes it easy to diagnose path issues

### 3. Added Debug Logging
**Key functions now log:**
- Input parameters
- Resolved absolute paths
- Whether paths exist
- Helps diagnose issues quickly

Functions with debug logging:
- `list_files()`
- `read_file()`

## How to Use

### Step 1: Install Dependencies
```bash
cd /home/arvin/projects/file-sense
pip install -r requirements.txt
```

### Step 2: Test Path Resolution
```bash
python3 test_paths.py
```

This script will:
- ✓ Verify all paths resolve correctly
- ✓ Check sandbox files exist (8 files expected)
- ✓ Test database connectivity
- ✓ Test vector store
- ✓ Test the `list_files()` tool

### Step 3: Index Files (if needed)
If the test shows 0 files in the database or vector store:
```bash
# Using CLI
python3 main.py index

# Or interactive mode
python3 main.py interactive
# Then type: index
```

### Step 4: Run the Agent
```bash
# Terminal mode
adk run agents/file_concierge

# Web UI mode
adk web agents/file_concierge
```

## Understanding the Sandbox

The "sandbox" is not a security sandbox - it's a **designated directory** where the agent operates on files:

```
/home/arvin/projects/file-sense/sandbox/
├── documents/
│   ├── resume.txt
│   ├── cover_letter.txt
│   └── research_paper_notes.txt
├── code/
│   ├── ml_experiment.py
│   └── data_processing.py
├── notes/
│   ├── meeting_notes.txt
│   └── project_ideas.txt
└── misc/
    └── todo.txt
```

**Total: 8 files**

## Debug Output

When running the agent, you'll now see debug output in stderr:

```
[DEBUG] Tools initialized with paths:
  PROJECT_ROOT: /home/arvin/projects/file-sense
  SANDBOX_DIR: /home/arvin/projects/file-sense/sandbox
  DATA_DIR: /home/arvin/projects/file-sense/data
  Current working directory: /home/arvin/projects/file-sense

[DEBUG] list_files() called with directory='', pattern='*'
[DEBUG] Resolved search_dir: /home/arvin/projects/file-sense/sandbox
[DEBUG] search_dir.exists(): True
```

This helps verify paths are correct when the agent runs.

## Common Issues

### Issue 1: Dependencies Not Installed
**Symptoms:**
```
ModuleNotFoundError: No module named 'dotenv'
```

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue 2: Files Not Indexed
**Symptoms:**
- Agent says "no files found"
- Search returns empty results
- Database shows 0 files

**Solution:**
```bash
python3 main.py index
```

### Issue 3: Wrong Working Directory
**Symptoms:**
```
ERROR: Sandbox directory not found at: /some/wrong/path/sandbox
```

**Solution:**
The fix applied should prevent this. If you still see it:
1. Ensure you're running from project root
2. Check the debug output to see what paths are being used
3. Verify `test_paths.py` passes

### Issue 4: Permission Issues
**Symptoms:**
```
PermissionError: [Errno 13] Permission denied
```

**Solution:**
```bash
# Check file permissions
ls -la sandbox/

# Fix if needed
chmod -R u+rw sandbox/
```

## Testing Commands

### Quick Test
```bash
# Should list 8 files
python3 -c "from pathlib import Path; print(len(list(Path('sandbox').rglob('*.*'))))"
```

### Full Diagnostic
```bash
python3 test_paths.py
```

### Test Agent Query
```bash
# After indexing
python3 main.py search "Python files"
```

## What Changed

### Files Modified:
1. **config/config.py** (lines 13-15, 52-74)
   - Absolute path resolution
   - Path validation method
   - Auto-validation on import

2. **src/file_concierge/tools.py** (lines 8, 15-29, 266-268, 307-309)
   - Added `import sys`
   - Module-level sandbox validation
   - Debug logging in key functions
   - Enhanced error messages

### Files Created:
1. **test_paths.py**
   - Comprehensive path resolution test
   - Database and vector store checks
   - Tool function testing

2. **TROUBLESHOOTING.md** (this file)
   - Complete troubleshooting guide

## How the Fix Works

### Before:
1. ADK runs: `adk run agents/file_concierge`
2. ADK might change working directory
3. `Path(__file__).parent.parent` resolves incorrectly
4. All file operations fail silently
5. Agent returns "cannot find files"

### After:
1. ADK runs: `adk run agents/file_concierge`
2. ADK might change working directory
3. `.resolve()` converts to absolute path immediately
4. Paths are always correct regardless of working directory
5. Validation confirms paths exist
6. Debug output shows actual paths being used
7. Agent works correctly ✓

## Next Steps

1. **Run the test:** `python3 test_paths.py`
2. **Index files:** `python3 main.py index` (if needed)
3. **Test agent:** `adk run agents/file_concierge`
4. **Try queries:**
   - "List all files"
   - "Find Python code files"
   - "Search for documents about machine learning"

## Additional Help

If you still encounter issues:
1. Check the debug output (stderr) when running the agent
2. Verify environment variables are set (GOOGLE_API_KEY)
3. Ensure .env file exists in project root
4. Check that ADK is properly installed: `adk --version`

---

**Summary:** The path resolution issue has been fixed by using absolute paths with `.resolve()`, adding validation, and providing debug logging. The agent should now be able to find and access files correctly regardless of the working directory ADK uses.
