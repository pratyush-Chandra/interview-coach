import json
import os
from typing import List, Dict, Any
import random
from pathlib import Path
from typing import Dict, List, Optional
import streamlit as st
from .mcq_vector_store import MCQVectorStore

class MCQManager:
    def __init__(self, mcq_file: str = "data/mcqs.json"):
        """
        Initialize the MCQ manager.
        
        Args:
            mcq_file (str): Path to the MCQ JSON file
        """
        self.mcq_file = mcq_file
        self.mcqs = self._load_mcqs()
        self.vector_store = MCQVectorStore()
        
        # Initialize vector store with MCQs if empty
        if not self._is_vector_store_initialized():
            self._initialize_vector_store()
    
    def _is_vector_store_initialized(self) -> bool:
        """
        Check if vector store is initialized with MCQs.
        
        Returns:
            bool: True if initialized, False otherwise
        """
        try:
            results = self.vector_store.search_mcqs("test", n_results=1)
            return len(results) > 0
        except:
            return False
    
    def _initialize_vector_store(self) -> None:
        """Initialize vector store with MCQs."""
        self.vector_store.add_mcqs(self.mcqs)
    
    def _load_mcqs(self) -> List[Dict[str, Any]]:
        """
        Load MCQs from the JSON file.
        
        Returns:
            List[Dict[str, Any]]: List of MCQs
        """
        try:
            if os.path.exists(self.mcq_file):
                with open(self.mcq_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            st.error(f"Error loading MCQs: {str(e)}")
            return []
    
    def get_questions_by_role(self, role: str) -> List[Dict[str, Any]]:
        """
        Get questions for a specific role.
        
        Args:
            role: Role name
            
        Returns:
            List of question dictionaries
        """
        return [q for q in self.mcqs if q.get("role") == role]
    
    def get_random_questions(self, num_questions: int) -> List[Dict[str, Any]]:
        """
        Get random questions.
        
        Args:
            num_questions: Number of questions to return
            
        Returns:
            List of question dictionaries
        """
        if num_questions <= 0:
            return []
        
        return random.sample(self.mcqs, min(num_questions, len(self.mcqs)))
    
    def search_questions(self, query: str, role_id: Optional[str] = None, n_results: int = 5) -> List[Dict]:
        """
        Search for relevant questions using semantic search.
        
        Args:
            query (str): Search query
            role_id (Optional[str]): Filter by role ID
            n_results (int): Number of results to return
            
        Returns:
            List[Dict]: List of relevant questions
        """
        results = self.vector_store.search_mcqs(query, role_id, n_results)
        
        # Convert vector store results to question format
        questions = []
        for result in results:
            question_id = result["metadata"]["question_id"]
            role_id = result["metadata"]["role_id"]
            
            # Find the original question in the MCQs
            for question in self.mcqs:
                if question["id"] == question_id:
                    questions.append(question)
                    break
        
        return questions
    
    def get_role_specific_questions(self, role_id: str, n_results: int = 5) -> List[Dict]:
        """
        Get role-specific questions using semantic search.
        
        Args:
            role_id (str): The role ID
            n_results (int): Number of results to return
            
        Returns:
            List[Dict]: List of role-specific questions
        """
        results = self.vector_store.get_role_specific_mcqs(role_id, n_results)
        
        # Convert vector store results to question format
        questions = []
        for result in results:
            question_id = result["metadata"]["question_id"]
            
            # Find the original question in the MCQs
            for question in self.mcqs:
                if question["id"] == question_id:
                    questions.append(question)
                    break
        
        return questions
    
    def check_answer(self, question: Dict[str, Any], answer: str) -> Dict[str, Any]:
        """
        Check if an answer is correct.
        
        Args:
            question: Question dictionary
            answer: User's answer
            
        Returns:
            Dict containing result and explanation
        """
        is_correct = answer == question["correct_answer"]
        return {
            "is_correct": is_correct,
            "explanation": question["explanation"]
        }
    
    def get_role_name(self, role_id: str) -> Optional[str]:
        """
        Get the display name for a role.
        
        Args:
            role_id (str): The role ID
            
        Returns:
            Optional[str]: The role name or None if not found
        """
        for role in self.mcqs:
            if role.get("id") == role_id:
                return role.get("name")
        return None 