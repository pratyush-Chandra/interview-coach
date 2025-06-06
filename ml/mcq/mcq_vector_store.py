import os
from typing import Dict, List, Optional
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import json
from pathlib import Path
import streamlit as st

class MCQVectorStore:
    def __init__(self, collection_name: str = "mcqs"):
        """
        Initialize the MCQ vector store.
        
        Args:
            collection_name (str): Name of the ChromaDB collection
        """
        self.client = chromadb.PersistentClient(
            path=os.getenv("CHROMA_DB_PATH", "./data/chroma"),
            settings=Settings(allow_reset=True)
        )
        
        # Initialize OpenAI embedding function
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="text-embedding-3-small"
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function
        )
    
    def add_mcqs(self, mcqs: Dict) -> bool:
        """
        Add MCQs to the vector store.
        
        Args:
            mcqs (Dict): Dictionary containing MCQs by role
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Prepare documents and metadata
            documents = []
            metadatas = []
            ids = []
            
            for role_id, role_data in mcqs.items():
                for question in role_data["questions"]:
                    # Create a rich text representation of the question
                    document = f"""
                    Role: {role_data['name']}
                    Question: {question['question']}
                    Options: {', '.join(question['options'])}
                    Explanation: {question['explanation']}
                    """
                    
                    documents.append(document)
                    metadatas.append({
                        "role_id": role_id,
                        "role_name": role_data["name"],
                        "question_id": question["id"],
                        "correct_answer": question["correct_answer"]
                    })
                    ids.append(question["id"])
            
            # Add to collection
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            return True
            
        except Exception as e:
            st.error(f"Error adding MCQs to vector store: {str(e)}")
            return False
    
    def search_mcqs(self, query: str, role_id: Optional[str] = None, n_results: int = 5) -> List[Dict]:
        """
        Search for relevant MCQs.
        
        Args:
            query (str): Search query
            role_id (Optional[str]): Filter by role ID
            n_results (int): Number of results to return
            
        Returns:
            List[Dict]: List of relevant MCQs with metadata
        """
        try:
            # Prepare where clause if role_id is provided
            where = {"role_id": role_id} if role_id else None
            
            # Search collection
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where
            )
            
            # Format results
            mcqs = []
            for i in range(len(results["ids"][0])):
                mcq = {
                    "id": results["ids"][0][i],
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None
                }
                mcqs.append(mcq)
            
            return mcqs
            
        except Exception as e:
            st.error(f"Error searching MCQs: {str(e)}")
            return []
    
    def get_role_specific_mcqs(self, role_id: str, n_results: int = 5) -> List[Dict]:
        """
        Get role-specific MCQs using a role-specific prompt.
        
        Args:
            role_id (str): The role ID
            n_results (int): Number of results to return
            
        Returns:
            List[Dict]: List of role-specific MCQs
        """
        # Create a role-specific prompt
        prompt = f"Find important technical questions and concepts for {role_id} role"
        return self.search_mcqs(prompt, role_id=role_id, n_results=n_results)
    
    def reset_collection(self) -> bool:
        """
        Reset the collection.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.collection.delete()
            self.collection = self.client.get_or_create_collection(
                name=self.collection.name,
                embedding_function=self.embedding_function
            )
            return True
        except Exception as e:
            st.error(f"Error resetting collection: {str(e)}")
            return False 