"""RAG (Retrieval-Augmented Generation) module for local document retrieval."""

from pathlib import Path
from typing import List

# Simple text search based RAG (no complex embedding models needed)
# For production, you could use LangChain's document loaders + vector stores


class SimpleRAG:
    """
    Simple RAG system using text-based retrieval.
    
    This implementation:
    - Loads documents from data/ folder
    - Splits them into chunks
    - Performs keyword-based search (no ML embeddings needed)
    - Returns relevant passages with source information
    """

    def __init__(self, data_dir: str = "data"):
        """Initialize RAG with documents from data_dir."""
        self.data_dir = Path(data_dir)
        self.documents = {}
        self.chunks = []
        self._load_documents()

    def _load_documents(self) -> None:
        """Load all .txt files from data directory."""
        if not self.data_dir.exists():
            print(f"Warning: {self.data_dir} does not exist. RAG will have no documents.")
            return

        for file_path in self.data_dir.glob("*.txt"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.documents[file_path.stem] = content
                    self._chunk_document(file_path.stem, content)
                print(f"Loaded document: {file_path.stem}")
            except Exception as e:
                print(f"Error loading {file_path}: {e}")

    def _chunk_document(self, doc_name: str, content: str, chunk_size: int = 500) -> None:
        """Split document into overlapping chunks for better retrieval."""
        sentences = content.split(". ")
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) > chunk_size:
                if current_chunk:
                    self.chunks.append({
                        "text": current_chunk.strip(),
                        "source": doc_name,
                        "size": len(current_chunk)
                    })
                current_chunk = sentence + ". "
            else:
                current_chunk += sentence + ". "
        
        # Add remaining chunk
        if current_chunk:
            self.chunks.append({
                "text": current_chunk.strip(),
                "source": doc_name,
                "size": len(current_chunk)
            })

    def _calculate_relevance(self, query: str, text: str) -> float:
        """
        Simple relevance scoring based on keyword matching.
        
        Returns a score between 0 and 1.
        """
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())
        
        # Remove common stop words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", 
            "to", "for", "of", "is", "are", "be", "was", "were"
        }
        
        query_words = query_words - stop_words
        text_words = text_words - stop_words
        
        if not query_words:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(query_words & text_words)
        union = len(query_words | text_words)
        
        return intersection / union if union > 0 else 0.0

    def search(self, query: str, top_k: int = 3) -> List[dict]:
        """
        Search for relevant documents using keyword matching.
        
        Args:
            query: Search query string
            top_k: Number of top results to return
            
        Returns:
            List of relevant passages with metadata
        """
        if not self.chunks:
            return []
        
        # Score all chunks
        scored_chunks = []
        for chunk in self.chunks:
            score = self._calculate_relevance(query, chunk["text"])
            if score > 0:  # Only include relevant chunks
                scored_chunks.append({
                    **chunk,
                    "relevance_score": score
                })
        
        # Sort by relevance and return top_k
        scored_chunks.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored_chunks[:top_k]

    def get_documents_summary(self) -> str:
        """Get a summary of loaded documents."""
        if not self.documents:
            return "No documents loaded."
        
        summary = "Loaded documents:\n"
        for doc_name, content in self.documents.items():
            word_count = len(content.split())
            summary += f"- {doc_name}: {word_count} words\n"
        return summary


# Global RAG instance
_rag_instance = None


def get_rag() -> SimpleRAG:
    """Get or create the global RAG instance."""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = SimpleRAG(data_dir="data")
    return _rag_instance


def search_local_docs(query: str, top_k: int = 3) -> List[dict]:
    """
    Search local documents.
    
    This is the main interface for the agent to search local documents.
    
    Args:
        query: Search query
        top_k: Number of results to return
        
    Returns:
        List of relevant passages with source and relevance scores
    """
    rag = get_rag()
    results = rag.search(query, top_k=top_k)
    
    # Format results for cleaner agent consumption
    formatted_results = []
    for result in results:
        formatted_results.append({
            "content": result["text"],
            "source": result["source"],
            "relevance": f"{result['relevance_score']:.2%}",
            "type": "local_document"
        })
    
    return formatted_results
