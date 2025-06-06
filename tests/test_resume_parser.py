import pytest
from pathlib import Path
import os

def test_resume_processor_initialization(resume_processor):
    """Test ResumeProcessor initialization."""
    assert resume_processor is not None
    assert resume_processor.vector_store is not None

def test_process_resume_file(resume_processor, sample_resume_file):
    """Test processing a resume file."""
    result = resume_processor.process_resume(sample_resume_file)
    
    assert result["status"] == "success"
    assert "chunks" in result
    assert len(result["chunks"]) > 0
    assert all(isinstance(chunk, str) for chunk in result["chunks"])
    assert "metadata" in result
    assert "skills" in result["metadata"]
    assert "experience" in result["metadata"]

def test_process_resume_text(resume_processor, sample_resume_text):
    """Test processing resume text directly."""
    result = resume_processor.process_resume_text(sample_resume_text)
    
    assert result["status"] == "success"
    assert "chunks" in result
    assert len(result["chunks"]) > 0
    assert all(isinstance(chunk, str) for chunk in result["chunks"])
    assert "metadata" in result
    assert "skills" in result["metadata"]
    assert "experience" in result["metadata"]

def test_extract_skills(resume_processor, sample_resume_text):
    """Test skill extraction from resume text."""
    skills = resume_processor._extract_skills(sample_resume_text)
    
    assert isinstance(skills, list)
    assert len(skills) > 0
    assert all(isinstance(skill, str) for skill in skills)
    assert "Python" in skills
    assert "Java" in skills
    assert "JavaScript" in skills

def test_extract_experience(resume_processor, sample_resume_text):
    """Test experience extraction from resume text."""
    experience = resume_processor._extract_experience(sample_resume_text)
    
    assert isinstance(experience, list)
    assert len(experience) > 0
    assert all(isinstance(exp, dict) for exp in experience)
    assert any("Senior Software Engineer" in exp["title"] for exp in experience)
    assert any("Software Engineer" in exp["title"] for exp in experience)

def test_chunk_resume(resume_processor, sample_resume_text):
    """Test resume chunking functionality."""
    chunks = resume_processor._chunk_resume(sample_resume_text)
    
    assert isinstance(chunks, list)
    assert len(chunks) > 0
    assert all(isinstance(chunk, str) for chunk in chunks)
    assert all(len(chunk) <= resume_processor.max_chunk_size for chunk in chunks)

def test_invalid_file_path(resume_processor):
    """Test handling of invalid file path."""
    result = resume_processor.process_resume("nonexistent_file.txt")
    assert result["status"] == "error"
    assert "message" in result

def test_empty_resume_text(resume_processor):
    """Test handling of empty resume text."""
    result = resume_processor.process_resume_text("")
    assert result["status"] == "error"
    assert "message" in result

def test_resume_with_minimal_content(resume_processor):
    """Test processing resume with minimal content."""
    minimal_resume = "John Doe\nSoftware Engineer"
    result = resume_processor.process_resume_text(minimal_resume)
    
    assert result["status"] == "success"
    assert len(result["chunks"]) > 0
    assert len(result["metadata"]["skills"]) == 0
    assert len(result["metadata"]["experience"]) == 0 