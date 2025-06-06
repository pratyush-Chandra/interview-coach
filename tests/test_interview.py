import pytest
from ml.interview.interview_manager import InterviewManager
from ml.interview.answer_evaluator import AnswerEvaluator

def test_interview_manager_initialization(interview_manager):
    """Test InterviewManager initialization."""
    assert interview_manager is not None
    assert interview_manager.vector_store is not None

def test_generate_questions(interview_manager, sample_resume_text):
    """Test question generation from resume."""
    questions = interview_manager.generate_questions(sample_resume_text)
    
    assert isinstance(questions, list)
    assert len(questions) > 0
    assert all(isinstance(q, dict) for q in questions)
    assert all("question" in q for q in questions)
    assert all("expected_answer" in q for q in questions)
    assert all("category" in q for q in questions)
    assert all("difficulty" in q for q in questions)

def test_generate_questions_with_categories(interview_manager, sample_resume_text):
    """Test question generation with specific categories."""
    categories = ["Technical", "Problem Solving"]
    questions = interview_manager.generate_questions(
        sample_resume_text,
        categories=categories
    )
    
    assert isinstance(questions, list)
    assert len(questions) > 0
    assert all(q["category"] in categories for q in questions)

def test_generate_questions_with_difficulty(interview_manager, sample_resume_text):
    """Test question generation with specific difficulty levels."""
    difficulty = "Intermediate"
    questions = interview_manager.generate_questions(
        sample_resume_text,
        difficulty=difficulty
    )
    
    assert isinstance(questions, list)
    assert len(questions) > 0
    assert all(q["difficulty"] == difficulty for q in questions)

def test_answer_evaluator_initialization():
    """Test AnswerEvaluator initialization."""
    evaluator = AnswerEvaluator()
    assert evaluator is not None

def test_evaluate_answer(interview_manager, sample_question, sample_answer):
    """Test answer evaluation functionality."""
    result = interview_manager.evaluate_answer(
        sample_question["question"],
        sample_answer,
        sample_question["expected_answer"]
    )
    
    assert isinstance(result, dict)
    assert "score" in result
    assert "feedback" in result
    assert "follow_up_questions" in result
    assert isinstance(result["score"], float)
    assert 0 <= result["score"] <= 1
    assert isinstance(result["feedback"], str)
    assert isinstance(result["follow_up_questions"], list)

def test_evaluate_answer_with_threshold(interview_manager, sample_question, sample_answer):
    """Test answer evaluation with custom threshold."""
    threshold = 0.7
    result = interview_manager.evaluate_answer(
        sample_question["question"],
        sample_answer,
        sample_question["expected_answer"],
        threshold=threshold
    )
    
    assert isinstance(result, dict)
    assert "score" in result
    assert "is_acceptable" in result
    assert isinstance(result["is_acceptable"], bool)
    assert result["is_acceptable"] == (result["score"] >= threshold)

def test_generate_follow_up_questions(interview_manager, sample_question, sample_answer):
    """Test follow-up question generation."""
    follow_ups = interview_manager.generate_follow_up_questions(
        sample_question["question"],
        sample_answer,
        sample_question["expected_answer"]
    )
    
    assert isinstance(follow_ups, list)
    assert len(follow_ups) > 0
    assert all(isinstance(q, str) for q in follow_ups)

def test_empty_answer_evaluation(interview_manager, sample_question):
    """Test evaluation of empty answer."""
    result = interview_manager.evaluate_answer(
        sample_question["question"],
        "",
        sample_question["expected_answer"]
    )
    
    assert isinstance(result, dict)
    assert "score" in result
    assert result["score"] == 0.0
    assert "feedback" in result
    assert len(result["feedback"]) > 0

def test_very_short_answer_evaluation(interview_manager, sample_question):
    """Test evaluation of very short answer."""
    short_answer = "Microservices are small services."
    result = interview_manager.evaluate_answer(
        sample_question["question"],
        short_answer,
        sample_question["expected_answer"]
    )
    
    assert isinstance(result, dict)
    assert "score" in result
    assert result["score"] < 0.5  # Should be low score
    assert "feedback" in result
    assert len(result["feedback"]) > 0 