import os
from typing import Dict, List, Optional, Tuple
import numpy as np
from openai import OpenAI
import streamlit as st
from ..rag.vector_store import VectorStoreManager

class AnswerEvaluator:
    def __init__(self, vector_store: VectorStoreManager):
        """
        Initialize the answer evaluator.
        
        Args:
            vector_store (VectorStoreManager): Vector store manager for RAG
        """
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.vector_store = vector_store
        self.similarity_threshold = 0.5
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a text using OpenAI's API.
        
        Args:
            text (str): Text to embed
            
        Returns:
            List[float]: Embedding vector
        """
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            st.error(f"Error getting embedding: {str(e)}")
            return []
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1 (List[float]): First vector
            vec2 (List[float]): Second vector
            
        Returns:
            float: Cosine similarity score
        """
        if not vec1 or not vec2:
            return 0.0
        
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        # Normalize vectors
        vec1_norm = np.linalg.norm(vec1)
        vec2_norm = np.linalg.norm(vec2)
        
        if vec1_norm == 0 or vec2_norm == 0:
            return 0.0
        
        return np.dot(vec1, vec2) / (vec1_norm * vec2_norm)
    
    def evaluate_answer(self, candidate_answer: str, expected_answer: str) -> Tuple[float, bool]:
        """
        Evaluate candidate's answer against expected answer.
        
        Args:
            candidate_answer (str): Candidate's answer
            expected_answer (str): Expected answer
            
        Returns:
            Tuple[float, bool]: (similarity score, is_acceptable)
        """
        # Get embeddings
        candidate_embedding = self.get_embedding(candidate_answer)
        expected_embedding = self.get_embedding(expected_answer)
        
        # Calculate similarity
        similarity = self.cosine_similarity(candidate_embedding, expected_embedding)
        
        # Check if answer is acceptable
        is_acceptable = similarity >= self.similarity_threshold
        
        return similarity, is_acceptable
    
    def generate_follow_up(self, question: str, candidate_answer: str, context: Optional[str] = None) -> str:
        """
        Generate a follow-up question using RAG.
        
        Args:
            question (str): Original question
            candidate_answer (str): Candidate's answer
            context (Optional[str]): Additional context for the question
            
        Returns:
            str: Follow-up question
        """
        try:
            # Prepare prompt for follow-up generation
            prompt = f"""
            Original Question: {question}
            Candidate's Answer: {candidate_answer}
            Context: {context if context else 'No additional context provided'}
            
            Based on the candidate's answer, generate a follow-up question that:
            1. Addresses gaps or misunderstandings in their response
            2. Probes deeper into the topic
            3. Helps clarify their understanding
            4. Is specific and focused
            
            Follow-up Question:
            """
            
            # Get relevant context from vector store
            search_results = self.vector_store.search(
                query=f"{question} {candidate_answer}",
                n_results=3
            )
            
            # Add relevant context to the prompt
            if search_results:
                context = "\n".join([result["content"] for result in search_results])
                prompt += f"\nRelevant Context:\n{context}"
            
            # Generate follow-up question
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert interviewer helping to evaluate and guide candidates."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            st.error(f"Error generating follow-up question: {str(e)}")
            return "Could you elaborate more on your answer?"
    
    def get_feedback(self, similarity: float, is_acceptable: bool) -> str:
        """
        Generate feedback based on answer evaluation.
        
        Args:
            similarity (float): Similarity score
            is_acceptable (bool): Whether the answer is acceptable
            
        Returns:
            str: Feedback message
        """
        if is_acceptable:
            if similarity >= 0.8:
                return "Excellent answer! You've demonstrated a strong understanding of the topic."
            elif similarity >= 0.6:
                return "Good answer! You've covered the main points well."
            else:
                return "Acceptable answer. You've addressed the key aspects, but there's room for more detail."
        else:
            if similarity >= 0.4:
                return "Your answer is partially correct, but missing some important aspects."
            else:
                return "Your answer needs improvement. Consider providing more specific details and examples." 