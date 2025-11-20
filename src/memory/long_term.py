"""Long-term memory for persistent metadata, tags, and collections."""

import json
import sqlite3
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from config import config


class LongTermMemory:
    """Manages long-term persistent storage of file metadata, tags, and collections."""

    def __init__(self, db_path: Path = None):
        self.db_path = db_path or config.MEMORY_DB_PATH
        self._init_database()

    def _init_database(self):
        """Initialize the SQLite database with required tables."""
        config.ensure_directories()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # File metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                file_name TEXT NOT NULL,
                file_type TEXT,
                file_size INTEGER,
                created_at TEXT,
                modified_at TEXT,
                indexed_at TEXT,
                text_sample TEXT,
                embedding_id TEXT
            )
        """)

        # Tags table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_name TEXT UNIQUE NOT NULL,
                created_at TEXT
            )
        """)

        # File-tags association table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                tag_id INTEGER NOT NULL,
                applied_at TEXT,
                FOREIGN KEY (tag_id) REFERENCES tags(id),
                UNIQUE(file_path, tag_id)
            )
        """)

        # Collections table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collection_name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # Collection-files association table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collection_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collection_id INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                added_at TEXT,
                FOREIGN KEY (collection_id) REFERENCES collections(id),
                UNIQUE(collection_id, file_path)
            )
        """)

        conn.commit()
        conn.close()

    def store_file_metadata(self, file_path: str, metadata: Dict[str, Any]):
        """Store or update file metadata."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO file_metadata
            (file_path, file_name, file_type, file_size, created_at, modified_at,
             indexed_at, text_sample, embedding_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            file_path,
            metadata.get("file_name"),
            metadata.get("file_type"),
            metadata.get("file_size"),
            metadata.get("created_at"),
            metadata.get("modified_at"),
            datetime.now().isoformat(),
            metadata.get("text_sample"),
            metadata.get("embedding_id")
        ))

        conn.commit()
        conn.close()

    def get_file_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Retrieve metadata for a specific file."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM file_metadata WHERE file_path = ?", (file_path,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def get_all_files(self) -> List[Dict[str, Any]]:
        """Get metadata for all indexed files."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM file_metadata")
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def add_tag(self, tag_name: str) -> int:
        """Add a new tag and return its ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR IGNORE INTO tags (tag_name, created_at)
            VALUES (?, ?)
        """, (tag_name, datetime.now().isoformat()))

        cursor.execute("SELECT id FROM tags WHERE tag_name = ?", (tag_name,))
        tag_id = cursor.fetchone()[0]

        conn.commit()
        conn.close()
        return tag_id

    def tag_file(self, file_path: str, tag_name: str):
        """Associate a tag with a file."""
        tag_id = self.add_tag(tag_name)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR IGNORE INTO file_tags (file_path, tag_id, applied_at)
            VALUES (?, ?, ?)
        """, (file_path, tag_id, datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def get_file_tags(self, file_path: str) -> List[str]:
        """Get all tags for a file."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT t.tag_name FROM tags t
            JOIN file_tags ft ON t.id = ft.tag_id
            WHERE ft.file_path = ?
        """, (file_path,))

        tags = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tags

    def get_files_by_tag(self, tag_name: str) -> List[str]:
        """Get all files with a specific tag."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT ft.file_path FROM file_tags ft
            JOIN tags t ON ft.tag_id = t.id
            WHERE t.tag_name = ?
        """, (tag_name,))

        files = [row[0] for row in cursor.fetchall()]
        conn.close()
        return files

    def create_collection(self, name: str, description: str = "") -> int:
        """Create a new collection."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO collections (collection_name, description, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        """, (name, description, now, now))

        collection_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return collection_id

    def add_file_to_collection(self, collection_name: str, file_path: str):
        """Add a file to a collection."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get collection ID
        cursor.execute("SELECT id FROM collections WHERE collection_name = ?", (collection_name,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            raise ValueError(f"Collection '{collection_name}' not found")

        collection_id = result[0]

        cursor.execute("""
            INSERT OR IGNORE INTO collection_files (collection_id, file_path, added_at)
            VALUES (?, ?, ?)
        """, (collection_id, file_path, datetime.now().isoformat()))

        # Update collection updated_at
        cursor.execute("""
            UPDATE collections SET updated_at = ? WHERE id = ?
        """, (datetime.now().isoformat(), collection_id))

        conn.commit()
        conn.close()

    def get_collection_files(self, collection_name: str) -> List[str]:
        """Get all files in a collection."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT cf.file_path FROM collection_files cf
            JOIN collections c ON cf.collection_id = c.id
            WHERE c.collection_name = ?
        """, (collection_name,))

        files = [row[0] for row in cursor.fetchall()]
        conn.close()
        return files

    def get_all_collections(self) -> List[Dict[str, Any]]:
        """Get all collections with their metadata."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM collections")
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_all_tags(self) -> List[str]:
        """Get all unique tags."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT tag_name FROM tags ORDER BY tag_name")
        tags = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tags
