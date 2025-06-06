import os
from typing import Dict, List, Optional, Any
from openai import OpenAI
import streamlit as st
from ..rag.vector_store import VectorStoreManager
from .answer_evaluator import AnswerEvaluator

class InterviewManager:
    def __init__(self, vector_store: VectorStoreManager):
        """Initialize InterviewManager with vector store."""
        self.vector_store = vector_store
        self.answer_evaluator = AnswerEvaluator()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.interview_history = []
    
    def generate_questions(self, resume_text: str, categories: Optional[List[str]] = None, difficulty: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Generate interview questions based on resume.
        
        Args:
            resume_text: Resume text
            categories: Optional list of question categories
            difficulty: Optional difficulty level
            
        Returns:
            List of question dictionaries
        """
        # Search for relevant content
        results = self.vector_store.search(resume_text, n_results=5)
        
        # Generate questions based on results
        questions = []
        for result in results:
            question = self._generate_question_from_chunk(result["document"])
            if question:
                if categories and question["category"] not in categories:
                    continue
                if difficulty and question["difficulty"] != difficulty:
                    continue
                questions.append(question)
        
        return questions
    
    def evaluate_answer(self, question: str, answer: str, expected_answer: str, threshold: float = 0.5) -> Dict[str, Any]:
        """
        Evaluate a candidate's answer.
        
        Args:
            question: Interview question
            answer: Candidate's answer
            expected_answer: Expected answer
            threshold: Similarity threshold
            
        Returns:
            Dict containing evaluation results
        """
        return self.answer_evaluator.evaluate_answer(
            question=question,
            answer=answer,
            expected_answer=expected_answer,
            threshold=threshold
        )
    
    def generate_follow_up_questions(self, question: str, answer: str, expected_answer: str) -> List[str]:
        """
        Generate follow-up questions based on the answer.
        
        Args:
            question: Original question
            answer: Candidate's answer
            expected_answer: Expected answer
            
        Returns:
            List of follow-up questions
        """
        return self.answer_evaluator.generate_follow_up_questions(
            question=question,
            answer=answer,
            expected_answer=expected_answer
        )
    
    def _generate_question_from_chunk(self, chunk: str) -> Optional[Dict[str, Any]]:
        """Generate a question from a resume chunk."""
        # This is a placeholder for the actual question generation logic
        # In a real implementation, this would use an LLM to generate questions
        return {
            "question": f"Can you elaborate on your experience with {chunk[:50]}...?",
            "expected_answer": "The candidate should provide detailed information about their experience.",
            "category": "Technical",
            "difficulty": "Intermediate"
        }
    
    def start_interview(self, role: str, experience_level: str) -> str:
        """
        Start a new interview session.
        
        Args:
            role (str): The role being interviewed for
            experience_level (str): Candidate's experience level
            
        Returns:
            str: Initial interview question
        """
        try:
            # Prepare system message
            system_message = f"""
            You are an expert interviewer conducting a technical interview for a {role} position.
            The candidate's experience level is {experience_level}.
            Focus on asking relevant technical questions and evaluating their responses.
            """
            
            # Generate initial question
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": "Start the interview with an appropriate technical question."}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            initial_question = response.choices[0].message.content.strip()
            
            # Store in history
            self.interview_history.append({
                "role": "assistant",
                "content": initial_question,
                "type": "question"
            })
            
            return initial_question
            
        except Exception as e:
            st.error(f"Error starting interview: {str(e)}")
            return "Let's begin the interview. Could you tell me about your experience with [relevant technology]?"
    
    def get_response(self, user_input: str) -> str:
        """
        Get AI response to user input.
        
        Args:
            user_input (str): User's input/answer
            
        Returns:
            str: AI response
        """
        try:
            # Store user input in history
            self.interview_history.append({
                "role": "user",
                "content": user_input,
                "type": "answer"
            })
            
            # Get the last question from history
            last_question = next(
                (item["content"] for item in reversed(self.interview_history) 
                 if item["type"] == "question"),
                None
            )
            
            if last_question:
                # Evaluate the answer
                similarity, is_acceptable = self.answer_evaluator.evaluate_answer(
                    candidate_answer=user_input,
                    expected_answer=last_question  # Using question as expected answer for now
                )
                
                # Get feedback
                feedback = self.answer_evaluator.get_feedback(similarity, is_acceptable)
                
                # Generate follow-up if needed
                if not is_acceptable:
                    follow_up = self.answer_evaluator.generate_follow_up(
                        question=last_question,
                        candidate_answer=user_input
                    )
                    
                    # Store follow-up in history
                    self.interview_history.append({
                        "role": "assistant",
                        "content": follow_up,
                        "type": "question"
                    })
                    
                    return f"{feedback}\n\nFollow-up question: {follow_up}"
                else:
                    # Generate next question
                    next_question = self._generate_next_question(user_input)
                    
                    # Store next question in history
                    self.interview_history.append({
                        "role": "assistant",
                        "content": next_question,
                        "type": "question"
                    })
                    
                    return f"{feedback}\n\nNext question: {next_question}"
            else:
                # Generate new question if no previous question
                new_question = self._generate_next_question(user_input)
                
                # Store new question in history
                self.interview_history.append({
                    "role": "assistant",
                    "content": new_question,
                    "type": "question"
                })
                
                return new_question
            
        except Exception as e:
            st.error(f"Error getting response: {str(e)}")
            return "I apologize, but I'm having trouble processing your response. Could you please rephrase your answer?"
    
    def _generate_next_question(self, context: str) -> str:
        """
        Generate the next interview question based on context.
        
        Args:
            context (str): Context from previous interaction
            
        Returns:
            str: Next question
        """
        try:
            # Get relevant context from vector store
            search_results = self.vector_store.search(
                query=context,
                n_results=3
            )
            
            # Prepare prompt
            prompt = f"""
            Previous interaction: {context}
            
            Based on the candidate's response, generate the next appropriate technical question that:
            1. Builds upon their previous answer
            2. Explores related technical concepts
            3. Maintains a logical progression in the interview
            4. Is specific and focused
            
            Next Question:
            """
            
            # Add relevant context
            if search_results:
                context = "\n".join([result["content"] for result in search_results])
                prompt += f"\nRelevant Context:\n{context}"
            
            # Generate next question
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert technical interviewer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            st.error(f"Error generating next question: {str(e)}")
            return "Could you tell me more about your experience with [relevant technology]?" 