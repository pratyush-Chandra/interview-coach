import pytest
from ml.mcq.mcq_manager import MCQManager
from ml.mcq.mcq_vector_store import MCQVectorStore

def test_mcq_manager_initialization(mcq_manager):
    """Test MCQManager initialization."""
    assert mcq_manager is not None
    assert mcq_manager.mcqs is not None
    assert len(mcq_manager.mcqs) > 0

def test_get_questions_by_role(mcq_manager):
    """Test getting questions for a specific role."""
    role = "Software Engineer"
    questions = mcq_manager.get_questions_by_role(role)
    
    assert isinstance(questions, list)
    assert len(questions) > 0
    assert all(isinstance(q, dict) for q in questions)
    assert all("question" in q for q in questions)
    assert all("options" in q for q in questions)
    assert all("correct_answer" in q for q in questions)
    assert all("explanation" in q for q in questions)

def test_get_random_questions(mcq_manager):
    """Test getting random questions."""
    num_questions = 5
    questions = mcq_manager.get_random_questions(num_questions)
    
    assert isinstance(questions, list)
    assert len(questions) == num_questions
    assert all(isinstance(q, dict) for q in questions)
    assert all("question" in q for q in questions)
    assert all("options" in q for q in questions)
    assert all("correct_answer" in q for q in questions)
    assert all("explanation" in q for q in questions)

def test_check_answer(mcq_manager):
    """Test answer checking functionality."""
    # Get a question
    questions = mcq_manager.get_random_questions(1)
    question = questions[0]
    
    # Test correct answer
    result = mcq_manager.check_answer(question, question["correct_answer"])
    assert result["is_correct"] is True
    assert "explanation" in result
    
    # Test incorrect answer
    incorrect_answer = "A" if question["correct_answer"] != "A" else "B"
    result = mcq_manager.check_answer(question, incorrect_answer)
    assert result["is_correct"] is False
    assert "explanation" in result

def test_mcq_vector_store_initialization(temp_dir):
    """Test MCQVectorStore initialization."""
    vector_store = MCQVectorStore(db_path=temp_dir)
    assert vector_store is not None
    assert vector_store.client is not None

def test_add_mcqs_to_vector_store(temp_dir, mcq_manager):
    """Test adding MCQs to vector store."""
    vector_store = MCQVectorStore(db_path=temp_dir)
    result = vector_store.add_mcqs(mcq_manager.mcqs)
    
    assert result["status"] == "success"
    assert "count" in result
    assert result["count"] > 0

def test_search_mcqs(temp_dir, mcq_manager):
    """Test searching MCQs in vector store."""
    vector_store = MCQVectorStore(db_path=temp_dir)
    vector_store.add_mcqs(mcq_manager.mcqs)
    
    query = "What is the difference between REST and GraphQL?"
    results = vector_store.search_mcqs(query)
    
    assert isinstance(results, list)
    assert len(results) > 0
    assert all(isinstance(r, dict) for r in results)
    assert all("question" in r for r in results)
    assert all("distance" in r for r in results)

def test_get_role_specific_mcqs(temp_dir, mcq_manager):
    """Test getting role-specific MCQs from vector store."""
    vector_store = MCQVectorStore(db_path=temp_dir)
    vector_store.add_mcqs(mcq_manager.mcqs)
    
    role = "Software Engineer"
    results = vector_store.get_role_specific_mcqs(role)
    
    assert isinstance(results, list)
    assert len(results) > 0
    assert all(isinstance(r, dict) for r in results)
    assert all("question" in r for r in results)
    assert all("distance" in r for r in results)

def test_invalid_role_questions(mcq_manager):
    """Test getting questions for invalid role."""
    role = "Invalid Role"
    questions = mcq_manager.get_questions_by_role(role)
    assert isinstance(questions, list)
    assert len(questions) == 0

def test_invalid_num_questions(mcq_manager):
    """Test getting invalid number of random questions."""
    num_questions = 0
    questions = mcq_manager.get_random_questions(num_questions)
    assert isinstance(questions, list)
    assert len(questions) == 0

def test_check_invalid_answer(mcq_manager):
    """Test checking invalid answer."""
    questions = mcq_manager.get_random_questions(1)
    question = questions[0]
    
    result = mcq_manager.check_answer(question, "Invalid Option")
    assert result["is_correct"] is False
    assert "explanation" in result 