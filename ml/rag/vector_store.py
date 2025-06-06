from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings

load_dotenv()

class VectorStoreManager:
    def __init__(self, collection_name: str = "resume_chunks"):
        """Initialize the vector store manager."""
        self.collection_name = collection_name
        self.embeddings = OpenAIEmbeddings()
        self.persist_directory = os.getenv("CHROMA_DB_PATH", "./data/chroma")
        
        # Initialize ChromaDB client
        self.client = chromadb.Client(Settings(
            persist_directory=self.persist_directory,
            anonymized_telemetry=False
        ))
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def create_documents(self, chunks: List[Dict[str, Any]]) -> List[Document]:
        """Convert chunks to LangChain documents."""
        documents = []
        for chunk in chunks:
            doc = Document(
                page_content=chunk["content"],
                metadata={
                    "chunk_id": chunk["id"],
                    "chunk_index": chunk["chunk_index"],
                    "total_chunks": chunk["total_chunks"],
                    "source": chunk["metadata"]["source"],
                    "created_at": chunk["created_at"]
                }
            )
            documents.append(doc)
        return documents

    def add_documents(self, chunks: List[Dict[str, Any]]) -> None:
        """Add documents to the vector store."""
        documents = self.create_documents(chunks)
        
        # Add documents to ChromaDB
        self.collection.add(
            documents=[doc.page_content for doc in documents],
            metadatas=[doc.metadata for doc in documents],
            ids=[doc.metadata["chunk_id"] for doc in documents]
        )

    def create_retriever(self, search_kwargs: Dict[str, Any] = None) -> Any:
        """Create a retriever from the vector store."""
        if search_kwargs is None:
            search_kwargs = {"k": 4}  # Default to retrieving 4 most similar chunks
            
        # Create vector store
        vector_store = Chroma(
            client=self.client,
            collection_name=self.collection_name,
            embedding_function=self.embeddings
        )
        
        # Create retriever
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs=search_kwargs
        )
        
        return retriever

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Perform similarity search on the vector store."""
        vector_store = Chroma(
            client=self.client,
            collection_name=self.collection_name,
            embedding_function=self.embeddings
        )
        
        return vector_store.similarity_search(query, k=k)

    def clear_collection(self) -> None:
        """Clear all documents from the collection."""
        self.collection.delete(where={}) 