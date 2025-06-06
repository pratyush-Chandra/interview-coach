from setuptools import setup, find_packages
import os

# Core dependencies required for basic functionality
CORE_DEPS = [
    "streamlit>=1.32.0",
    "plotly>=5.18.0",
    "fastapi>=0.109.2",
    "uvicorn>=0.27.1",
    "sqlalchemy>=2.0.27",
    "pydantic>=2.6.1",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "python-multipart>=0.0.9",
    "alembic>=1.13.1",
    "psycopg2-binary>=2.9.9",
    "chromadb>=0.3.29",
    "langchain>=0.1.9",
    "openai>=1.12.0",
    "numpy>=1.24.3",
    "python-dotenv>=1.0.1",
    "tenacity>=8.2.3",
    "tqdm>=4.66.2",
    "requests>=2.31.0",
    "reportlab>=4.0.4",
    "kaleido>=0.2.1",
    "bcrypt>=4.1.2"
]

# Optional dependencies for additional features
EXTRA_DEPS = {
    "webrtc": ["streamlit-webrtc>=0.47.1"],
    "doc": [
        "python-docx>=1.1.0",
        "pdf2image>=1.17.0",
        "pytesseract>=0.3.10",
        "PyMuPDF>=1.23.8",
        "docx2txt>=0.8"
    ],
    "speech": [
        "SpeechRecognition>=3.10.0",
        "gTTS>=2.3.2",
        "openai-whisper>=20231117",
        "soundfile>=0.12.1"
    ],
    "nlp": ["spacy>=3.7.4"],
    "test": [
        "pytest>=8.0.1",
        "pytest-asyncio>=0.23.5",
        "httpx>=0.26.0"
    ]
}

# Combine all dependencies for "all" extra
EXTRA_DEPS["all"] = [dep for deps in EXTRA_DEPS.values() for dep in deps]

setup(
    name="interview_coach",
    version="0.1.0",
    packages=find_packages(),
    install_requires=CORE_DEPS,
    extras_require=EXTRA_DEPS,
    python_requires=">=3.8",
    author="Interview Coach Team",
    description="An AI-powered interview preparation platform",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
) 