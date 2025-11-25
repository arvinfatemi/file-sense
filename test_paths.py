#!/usr/bin/env python3
"""Test script to verify path resolution and file access."""

import sys
from pathlib import Path

print("=" * 60)
print("Path Resolution Test")
print("=" * 60)

# Test 1: Check current working directory
print(f"\n1. Current working directory: {Path.cwd()}")

# Test 2: Import config and check paths
try:
    from config import config
    print("\n2. Config paths:")
    print(f"   PROJECT_ROOT: {config.PROJECT_ROOT}")
    print(f"   SANDBOX_DIR: {config.SANDBOX_DIR}")
    print(f"   DATA_DIR: {config.DATA_DIR}")
    print(f"   SANDBOX_DIR exists: {config.SANDBOX_DIR.exists()}")
    print(f"   DATA_DIR exists: {config.DATA_DIR.exists()}")
except Exception as e:
    print(f"\n2. ERROR loading config: {e}")
    sys.exit(1)

# Test 3: Check sandbox files
print("\n3. Files in sandbox:")
if config.SANDBOX_DIR.exists():
    all_files = list(config.SANDBOX_DIR.rglob("*"))
    file_list = [f for f in all_files if f.is_file()]
    print(f"   Total files: {len(file_list)}")
    for f in sorted(file_list):
        rel_path = f.relative_to(config.SANDBOX_DIR)
        print(f"   - {rel_path} ({f.stat().st_size} bytes)")
else:
    print("   ERROR: Sandbox directory not found!")

# Test 4: Try to import tools (this will trigger validation)
print("\n4. Testing tools import:")
try:
    from src.file_concierge import tools
    print("   ✓ Tools imported successfully")
    print("   ✓ Path validation passed")
except Exception as e:
    print(f"   ✗ ERROR importing tools: {e}")
    sys.exit(1)

# Test 5: Check database
print("\n5. Database status:")
try:
    from src.memory.long_term import LongTermMemory
    memory = LongTermMemory()
    files = memory.get_all_files()
    print(f"   Files in SQLite database: {len(files)}")
    if files:
        print("   Files:")
        for f in files[:5]:
            print(f"      - {f}")
        if len(files) > 5:
            print(f"      ... and {len(files) - 5} more")
except Exception as e:
    print(f"   ERROR accessing database: {e}")

# Test 6: Check vector store
print("\n6. Vector store status:")
try:
    from src.indexing.vector_store import VectorStore
    vector_store = VectorStore()
    count = vector_store.count_documents()
    print(f"   Documents in vector store: {count}")
except Exception as e:
    print(f"   ERROR accessing vector store: {e}")

# Test 7: Test list_files tool
print("\n7. Testing list_files() tool:")
try:
    result = tools.list_files()
    print(f"   Status: {result['status']}")
    print(f"   Files found: {result.get('count', 0)}")
    if result['status'] == 'success' and result.get('files'):
        print("   First few files:")
        for f in result['files'][:3]:
            print(f"      - {f['path']}")
except Exception as e:
    print(f"   ERROR calling list_files(): {e}")

print("\n" + "=" * 60)
print("Summary")
print("=" * 60)
print("\nIf you see errors above, the main issues are likely:")
print("1. Missing dependencies - run: pip install -r requirements.txt")
print("2. Files not indexed - run: python main.py index")
print("\nIf paths resolved correctly but no files in database:")
print("   Run: python main.py index")
print("\nTo test the agent:")
print("   Run: adk run agents/file_concierge")
print("   Or: adk web agents/file_concierge")
print("=" * 60)
