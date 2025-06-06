# AI-Powered Mock Interview Application

An intelligent mock interview platform that helps users prepare for technical interviews through AI-driven conversations, resume analysis, and role-based assessments.

## Features

- 🤖 AI-powered mock interviews with voice/text interaction
- 📝 Resume parsing and analysis
- 📚 Role-based technical MCQs
- 🎯 Personalized interview feedback
- 📊 Visual analytics and performance tracking
- 🔐 User authentication and profile management

## Tech Stack

### Frontend
- Streamlit (Web Interface)
- WebRTC (Real-time Communication)
- Plotly (Data Visualization)

### Backend
- FastAPI (REST API)
- LangChain (RAG Implementation)
- ChromaDB (Vector Store)
- SQLAlchemy (Database ORM)

### AI/ML
- OpenAI GPT Models
- LangChain for RAG
- Custom ML models for resume parsing

### Database
- PostgreSQL (User data, interview history)
- ChromaDB (Vector store for embeddings)

## Project Structure

```
interview_coach/
├── frontend/                 # Streamlit application
│   ├── pages/               # Streamlit pages
│   ├── components/          # Reusable UI components
│   └── assets/             # Static assets
├── backend/                 # FastAPI application
│   ├── api/                # API endpoints
│   ├── core/               # Core functionality
│   ├── models/             # Database models
│   └── services/           # Business logic
├── ml/                     # Machine Learning components
│   ├── resume_parser/      # Resume parsing logic
│   ├── rag/               # RAG implementation
│   └── interview_bot/      # Interview bot logic
├── tests/                  # Test suite
├── docs/                   # Documentation
└── config/                 # Configuration files
```

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Homebrew (for macOS)
- Git

### Quick Setup (macOS)
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/interview-coach.git
   cd interview-coach
   ```

2. Run the setup script:
   ```bash
   ./setup.sh
   ```

### Manual Setup
1. Install system dependencies:
   ```bash
   # macOS
   brew install tesseract poppler

   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr poppler-utils
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Download spaCy model:
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. Initialize the database:
   ```bash
   python backend/scripts/init_db.py
   ```

7. Start the backend server:
   ```bash
   uvicorn backend.main:app --reload
   ```

8. Start the frontend:
   ```bash
   streamlit run frontend/app.py
   ```

## Environment Variables

Create a `.env` file with the following variables:

```
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=postgresql://user:password@localhost:5432/interview_coach
CHROMA_DB_PATH=./data/chroma
```

## Troubleshooting

### Common Issues
1. **ChromaDB Installation Error**
   - Try using the older version specified in requirements.txt
   - Make sure you have the latest pip: `pip install --upgrade pip`

2. **Tesseract/Poppler Not Found**
   - Ensure system dependencies are installed using Homebrew (macOS) or apt (Ubuntu)
   - Verify installation: `tesseract --version` and `pdftoppm -v`

3. **Python Package Installation Errors**
   - Try installing packages one by one to identify problematic dependencies
   - Use `pip install --no-cache-dir` to force fresh downloads

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

## Contact

For any queries or support, please open an issue in the repository. 