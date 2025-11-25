"""Vector store for semantic search using ChromaDB."""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
from pathlib import Path
from config import config


class VectorStore:
    """Manages vector embeddings and semantic search."""

    def __init__(self, persist_dir: Path = None, embedding_model: str = None):
        self.persist_dir = persist_dir or config.CHROMA_PERSIST_DIR
        self.embedding_model_name = embedding_model or config.EMBEDDING_MODEL

        # Initialize embedding model
        self.embedding_model = SentenceTransformer(self.embedding_model_name)

        # Initialize ChromaDB
        config.ensure_directories()
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collection with cosine distance metric
        self.collection = self.client.get_or_create_collection(
            name="file_embeddings",
            metadata={
                "description": "File content embeddings for semantic search",
                "hnsw:space": "cosine"  # Use cosine similarity
            }
        )

    def add_document(self, file_path: str, content: str, metadata: Dict[str, Any] = None):
        """
        Add a document to the vector store.

        Args:
            file_path: Unique identifier for the file
            content: Text content to embed
            metadata: Additional metadata to store
        """
        if not content or not content.strip():
            return

        # Generate embedding
        embedding = self.embedding_model.encode(content).tolist()

        # Store in ChromaDB
        self.collection.add(
            ids=[file_path],
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata or {}]
        )

    def update_document(self, file_path: str, content: str, metadata: Dict[str, Any] = None):
        """Update an existing document."""
        # ChromaDB upsert behavior
        self.add_document(file_path, content, metadata)

    def search(self, query: str, top_k: int = None, filter_metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Perform semantic search.

        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filters

        Returns:
            List of search results with metadata
        """
        top_k = top_k or config.TOP_K_RESULTS

        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()

        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata
        )

        # Format results
        formatted_results = []
        if results["ids"] and results["ids"][0]:
            for i, file_path in enumerate(results["ids"][0]):
                formatted_results.append({
                    "file_path": file_path,
                    "distance": results["distances"][0][i] if "distances" in results else None,
                    "similarity": 1 - results["distances"][0][i] if "distances" in results else None,
                    "content": results["documents"][0][i] if "documents" in results else None,
                    "metadata": results["metadatas"][0][i] if "metadatas" in results else {}
                })

        return formatted_results

    def delete_document(self, file_path: str):
        """Remove a document from the vector store."""
        try:
            self.collection.delete(ids=[file_path])
        except Exception:
            pass

    def get_document(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific document."""
        try:
            result = self.collection.get(ids=[file_path])
            if result["ids"]:
                return {
                    "file_path": result["ids"][0],
                    "content": result["documents"][0] if result["documents"] else None,
                    "metadata": result["metadatas"][0] if result["metadatas"] else {}
                }
        except Exception:
            pass
        return None

    def count_documents(self) -> int:
        """Get the total number of documents in the store."""
        return self.collection.count()

    def clear(self):
        """Clear all documents from the collection."""
        self.client.delete_collection("file_embeddings")
        self.collection = self.client.get_or_create_collection(
            name="file_embeddings",
            metadata={"description": "File content embeddings for semantic search"}
        )
