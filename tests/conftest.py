import pytest
import os
import tempfile
from pathlib import Path
from ml.rag.vector_store import VectorStoreManager
from ml.resume_parser.resume_processor import ResumeProcessor
from ml.interview.interview_manager import InterviewManager
from ml.mcq.mcq_manager import MCQManager

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir

@pytest.fixture
def vector_store(temp_dir):
    """Create a VectorStoreManager instance with a temporary database."""
    db_path = os.path.join(temp_dir, "test_chroma")
    return VectorStoreManager(db_path=db_path)

@pytest.fixture
def resume_processor(vector_store):
    """Create a ResumeProcessor instance with the test vector store."""
    return ResumeProcessor(vector_store)

@pytest.fixture
def interview_manager(vector_store):
    """Create an InterviewManager instance with the test vector store."""
    return InterviewManager(vector_store)

@pytest.fixture
def mcq_manager():
    """Create an MCQManager instance."""
    return MCQManager()

@pytest.fixture
def sample_resume_text():
    """Return a sample resume text for testing."""
    return """
    JOHN DOE
    Software Engineer
    
    EXPERIENCE
    Senior Software Engineer
    Tech Company Inc.
    2020 - Present
    - Led development of microservices architecture
    - Implemented CI/CD pipelines
    - Mentored junior developers
    
    Software Engineer
    Startup Co.
    2018 - 2020
    - Developed REST APIs
    - Optimized database queries
    - Implemented unit tests
    
    SKILLS
    - Python, Java, JavaScript
    - Docker, Kubernetes
    - AWS, GCP
    - SQL, NoSQL
    """

@pytest.fixture
def sample_resume_file(temp_dir, sample_resume_text):
    """Create a sample resume file for testing."""
    file_path = os.path.join(temp_dir, "sample_resume.txt")
    with open(file_path, "w") as f:
        f.write(sample_resume_text)
    return file_path

@pytest.fixture
def sample_question():
    """Return a sample interview question for testing."""
    return {
        "question": "Explain the concept of microservices architecture.",
        "expected_answer": "Microservices architecture is a design pattern where an application is structured as a collection of small, independent services that communicate through APIs. Each service is responsible for a specific business capability and can be developed, deployed, and scaled independently.",
        "category": "Technical",
        "difficulty": "Intermediate"
    }

@pytest.fixture
def sample_answer():
    """Return a sample answer for testing."""
    return """
    Microservices architecture is a way of building applications where each component is a separate service. 
    These services are independent and can be developed and deployed on their own. 
    They communicate with each other through APIs, usually REST or gRPC. 
    This approach makes the system more maintainable and scalable.
    """ 