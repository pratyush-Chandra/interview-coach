import streamlit as st
import streamlit_webrtc as webrtc
import plotly.express as px
from dotenv import load_dotenv
import os
import sys
from pathlib import Path
import tempfile
import json
from datetime import datetime
from typing import Tuple
from ml.report.report_generator import ReportGenerator
import base64

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from ml.voice.voice_processor import VoiceProcessor
from ml.rag.vector_store import VectorStoreManager
from ml.resume_parser.resume_processor import ResumeProcessor
from ml.interview.interview_manager import InterviewManager
from ml.avatar.avatar_manager import AvatarManager
from ml.mcq.mcq_manager import MCQManager

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Interview Coach",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .resume-text {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        white-space: pre-wrap;
        font-family: monospace;
    }
    .chunk-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
    }
    .stat-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
    }
    .search-result {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c8e6c9;
        margin-bottom: 1rem;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #2b313e;
    }
    .chat-message.assistant {
        background-color: #475063;
    }
    .chat-message .avatar {
        width: 20%;
    }
    .chat-message .content {
        width: 80%;
    }
    .avatar-container {
        display: flex;
        justify-content: center;
        margin: 2rem 0;
    }
    .avatar-video {
        max-width: 400px;
        border-radius: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .response-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .response-card h4 {
        color: #1f2937;
        margin-bottom: 1rem;
        font-size: 1.1rem;
    }
    .response-card p {
        margin: 0.5rem 0;
        color: #4b5563;
    }
    .response-card strong {
        color: #1f2937;
    }
    .response-card .score {
        font-size: 1.2rem;
        font-weight: bold;
        color: #059669;
    }
    .response-card .feedback {
        background-color: #f3f4f6;
        padding: 0.75rem;
        border-radius: 0.375rem;
        margin-top: 0.5rem;
    }
    .response-card .follow-ups {
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid #e5e7eb;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'voice_processor' not in st.session_state:
    st.session_state.voice_processor = VoiceProcessor()
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = VectorStoreManager()
if 'resume_processor' not in st.session_state:
    st.session_state.resume_processor = ResumeProcessor(st.session_state.vector_store)
if 'interview_manager' not in st.session_state:
    st.session_state.interview_manager = InterviewManager()
if 'avatar_manager' not in st.session_state:
    st.session_state.avatar_manager = AvatarManager()
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_avatar_video' not in st.session_state:
    st.session_state.current_avatar_video = None
if 'mcq_manager' not in st.session_state:
    st.session_state.mcq_manager = MCQManager()
if 'current_questions' not in st.session_state:
    st.session_state.current_questions = []
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
if 'show_results' not in st.session_state:
    st.session_state.show_results = False

def main():
    st.title("🎯 Interview Coach")
    st.subheader("AI-Powered Mock Interview Platform")

    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Go to",
            ["Home", "Mock Interview", "Resume Analysis", "MCQs", "Analytics", "Voice Chat"]
        )

    # Main content
    if page == "Home":
        show_home()
    elif page == "Mock Interview":
        show_mock_interview()
    elif page == "Resume Analysis":
        show_resume_analysis()
    elif page == "MCQs":
        show_mcqs()
    elif page == "Analytics":
        show_analytics()
    elif page == "Voice Chat":
        show_voice_chat()

def show_home():
    st.write("Welcome to Interview Coach! Your AI-powered interview preparation platform.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Features")
        st.write("""
        - 🤖 AI-powered mock interviews
        - 📝 Resume analysis
        - 📚 Role-based MCQs
        - 📊 Performance analytics
        """)
    
    with col2:
        st.subheader("Get Started")
        st.write("Choose an option from the sidebar to begin your interview preparation journey!")

def show_mock_interview():
    st.header("Mock Interview")
    st.write("Start your AI-powered mock interview session")
    
    # Initialize session state variables
    if "interview_manager" not in st.session_state:
        st.session_state.interview_manager = InterviewManager(st.session_state.vector_store)
    if "interview_responses" not in st.session_state:
        st.session_state.interview_responses = []
    if "current_question" not in st.session_state:
        st.session_state.current_question = None
    if "interview_started" not in st.session_state:
        st.session_state.interview_started = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Role and experience level selection
    col1, col2 = st.columns(2)
    with col1:
        role = st.selectbox(
            "Select Role",
            ["Software Engineer", "Data Scientist", "Product Manager", "DevOps Engineer"]
        )
    with col2:
        experience_level = st.selectbox(
            "Experience Level",
            ["Entry Level", "Mid Level", "Senior Level"]
        )
    
    # Start interview button
    if st.button("Start Interview"):
        with st.spinner("Starting interview..."):
            initial_question = st.session_state.interview_manager.start_interview(role, experience_level)
            st.session_state.current_question = initial_question
            st.session_state.interview_started = True
            st.session_state.chat_history = []
            st.session_state.interview_responses = []
            st.session_state.current_question_id = 1
    
    # Interview interface
    if st.session_state.get("interview_started", False):
        # Display chat history
        for message in st.session_state.chat_history:
            with st.container():
                st.markdown(f"""
                    <div class="chat-message {message['role']}">
                        <div class="content">{message['content']}</div>
                    </div>
                """, unsafe_allow_html=True)
        
        # Display current question
        if st.session_state.current_question:
            st.markdown(f"""
                <div class="chat-message assistant">
                    <div class="content">{st.session_state.current_question}</div>
                </div>
            """, unsafe_allow_html=True)
        
        # Answer input
        answer = st.text_area("Your Answer", height=150)
        
        if st.button("Submit Answer"):
            if answer:
                with st.spinner("Evaluating your answer..."):
                    # Get AI response with evaluation
                    response = st.session_state.interview_manager.get_response(answer)
                    
                    # Extract feedback and next question from response
                    feedback, next_question = _parse_response(response)
                    
                    # Get similarity score from interview manager
                    similarity = st.session_state.interview_manager.answer_evaluator.evaluate_answer(
                        candidate_answer=answer,
                        expected_answer=st.session_state.current_question
                    )[0]
                    
                    # Store response data
                    response_data = {
                        "question_id": st.session_state.current_question_id,
                        "question": st.session_state.current_question,
                        "user_answer": answer,
                        "similarity_score": similarity,
                        "feedback": feedback,
                        "follow_ups": [],
                        "timestamp": st.session_state.get("_last_submit_time", None)
                    }
                    
                    # Check if this is a follow-up to a previous question
                    if "follow_up_for" in st.session_state:
                        response_data["follow_up_for"] = st.session_state.follow_up_for
                        # Add to follow-ups of the original question
                        for resp in st.session_state.interview_responses:
                            if resp["question_id"] == st.session_state.follow_up_for:
                                resp["follow_ups"].append(response_data)
                                break
                    else:
                        st.session_state.interview_responses.append(response_data)
                    
                    # Update chat history
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": answer
                    })
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response
                    })
                    
                    # Update current question and state
                    st.session_state.current_question = next_question
                    st.session_state.current_question_id += 1
                    st.session_state._last_submit_time = st.session_state.get("_last_submit_time", None)
                    
                    # Check if this is a follow-up question
                    if "Follow-up question:" in response:
                        st.session_state.follow_up_for = st.session_state.current_question_id - 1
                    else:
                        st.session_state.follow_up_for = None
                    
                    # Rerun to update the display
                    st.experimental_rerun()
            else:
                st.warning("Please provide an answer before submitting.")
        
        # Display interview progress
        if st.session_state.interview_responses:
            st.subheader("Interview Progress")
            
            # Calculate overall score
            total_score = sum(resp["similarity_score"] for resp in st.session_state.interview_responses)
            avg_score = total_score / len(st.session_state.interview_responses)
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Questions Answered", len(st.session_state.interview_responses))
            with col2:
                st.metric("Average Score", f"{avg_score:.2%}")
            with col3:
                st.metric("Follow-up Questions", sum(len(resp["follow_ups"]) for resp in st.session_state.interview_responses))
            
            # Display response history
            with st.expander("View Response History", expanded=False):
                for resp in st.session_state.interview_responses:
                    st.markdown(f"""
                        <div class="response-card">
                            <h4>Question {resp['question_id']}</h4>
                            <p><strong>Question:</strong> {resp['question']}</p>
                            <p><strong>Your Answer:</strong> {resp['user_answer']}</p>
                            <p><strong>Score:</strong> {resp['similarity_score']:.2%}</p>
                            <p><strong>Feedback:</strong> {resp['feedback']}</p>
                            {f"<p><strong>Follow-ups:</strong> {len(resp['follow_ups'])}</p>" if resp['follow_ups'] else ""}
                        </div>
                    """, unsafe_allow_html=True)
        
        # End interview button
        if st.button("End Interview"):
            # Save interview results
            _save_interview_results()
            
            # Reset session state
            st.session_state.interview_started = False
            st.session_state.current_question = None
            st.session_state.chat_history = []
            st.session_state.interview_responses = []
            st.session_state.current_question_id = 1
            st.session_state.follow_up_for = None
            st.experimental_rerun()

def _parse_response(response: str) -> Tuple[str, str]:
    """
    Parse the AI response to extract feedback and next question.
    
    Args:
        response (str): The AI response
        
    Returns:
        Tuple[str, str]: (feedback, next_question)
    """
    if "Follow-up question:" in response:
        parts = response.split("Follow-up question:")
        feedback = parts[0].strip()
        next_question = parts[1].strip()
    elif "Next question:" in response:
        parts = response.split("Next question:")
        feedback = parts[0].strip()
        next_question = parts[1].strip()
    else:
        feedback = ""
        next_question = response.strip()
    
    return feedback, next_question

def _save_interview_results():
    """Save interview results to a file."""
    try:
        # Create results directory if it doesn't exist
        results_dir = Path("data/interview_results")
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = results_dir / f"interview_{timestamp}.json"
        
        # Prepare results data
        results = {
            "timestamp": timestamp,
            "role": st.session_state.get("role", "Unknown"),
            "experience_level": st.session_state.get("experience_level", "Unknown"),
            "responses": st.session_state.interview_responses,
            "total_questions": len(st.session_state.interview_responses),
            "average_score": sum(resp["similarity_score"] for resp in st.session_state.interview_responses) / len(st.session_state.interview_responses) if st.session_state.interview_responses else 0
        }
        
        # Save to file
        with open(filename, "w") as f:
            json.dump(results, f, indent=2)
        
        st.success(f"Interview results saved to {filename}")
        
    except Exception as e:
        st.error(f"Error saving interview results: {str(e)}")

def show_resume_analysis():
    st.header("Resume Analysis")
    st.write("Upload your resume for AI-powered analysis")
    
    # File upload section
    uploaded_file = st.file_uploader(
        "Choose a resume file",
        type=['pdf', 'docx'],
        help="Upload your resume in PDF or DOCX format"
    )
    
    if uploaded_file:
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            # Process the resume
            with st.spinner("Processing your resume..."):
                result = st.session_state.resume_processor.process_resume(tmp_path)
            
            if result["status"] == "success":
                st.success("Resume processed successfully!")
                
                # Display statistics
                st.subheader("Processing Statistics")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Chunks", result["stats"]["total_chunks"])
                with col2:
                    st.metric("Avg Chunk Size", f"{result['stats']['avg_chunk_size']:.0f} chars")
                with col3:
                    st.metric("Min Chunk Size", f"{result['stats']['min_chunk_size']} chars")
                with col4:
                    st.metric("Max Chunk Size", f"{result['stats']['max_chunk_size']} chars")
                
                # Vector store status
                if result["vector_store_status"] == "success":
                    st.success("Resume chunks successfully embedded and stored!")
                else:
                    st.warning("Failed to store resume chunks in vector database.")
                
                # Display extracted text
                with st.expander("View Extracted Text", expanded=False):
                    st.markdown(f'<div class="resume-text">{result["extracted_text"]}</div>', unsafe_allow_html=True)
                
                # Display chunks
                with st.expander("View Text Chunks", expanded=False):
                    for i, chunk in enumerate(result["chunks"]):
                        st.markdown(f'<div class="chunk-card">{chunk["content"]}</div>', unsafe_allow_html=True)
                        st.caption(f"Chunk ID: {chunk['id']}")
                        st.caption(f"Size: {len(chunk['content'])} characters")
                
                # Semantic search section
                st.subheader("Semantic Search")
                search_query = st.text_input(
                    "Search your resume",
                    placeholder="Enter keywords or phrases to search in your resume..."
                )
                
                if search_query:
                    with st.spinner("Searching..."):
                        search_results = st.session_state.resume_processor.search_resume(search_query)
                        
                        if search_results:
                            st.write(f"Found {len(search_results)} relevant sections:")
                            for i, result in enumerate(search_results):
                                with st.expander(f"Result {i+1}", expanded=True):
                                    st.markdown(f"""
                                        <div class="search-result">
                                            <div class="content">{result['content']}</div>
                                            <div class="score">Relevance: {result['score']:.2f}</div>
                                            <div class="chunk-id">Chunk ID: {result['chunk_id']}</div>
                                        </div>
                                    """, unsafe_allow_html=True)
                        else:
                            st.info("No relevant sections found. Try different search terms.")
                
                # Placeholder for AI analysis
                st.info("AI analysis coming soon!")
                
                # Clean up temporary file
                os.unlink(tmp_path)
            else:
                st.error(f"Error processing resume: {result['error']}")
                
        except Exception as e:
            st.error(f"Error processing resume: {str(e)}")
            st.info("Please make sure your file is a valid PDF or DOCX document.")

def show_mcqs():
    st.header("Multiple Choice Questions")
    
    # Initialize MCQ manager if not already done
    if "mcq_manager" not in st.session_state:
        st.session_state.mcq_manager = MCQManager()
    
    # Initialize session state variables if not present
    if "current_questions" not in st.session_state:
        st.session_state.current_questions = []
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {}
    if "show_results" not in st.session_state:
        st.session_state.show_results = False
    
    # Role selection
    roles = st.session_state.mcq_manager.get_available_roles()
    selected_role = st.selectbox(
        "Select Role",
        options=[role["id"] for role in roles],
        format_func=lambda x: st.session_state.mcq_manager.get_role_name(x)
    )
    
    # Search interface
    st.subheader("Search Questions")
    search_query = st.text_input("Enter your search query")
    search_role = st.checkbox("Filter by selected role", value=True)
    
    if search_query:
        # Perform semantic search
        questions = st.session_state.mcq_manager.search_questions(
            search_query,
            role_id=selected_role if search_role else None
        )
        if questions:
            st.session_state.current_questions = questions
            st.session_state.show_results = False
            st.session_state.user_answers = {}
        else:
            st.warning("No questions found matching your search.")
    
    # Generate new questions button
    if st.button("Generate New Questions"):
        # Get role-specific questions using semantic search
        questions = st.session_state.mcq_manager.get_role_specific_questions(selected_role)
        st.session_state.current_questions = questions
        st.session_state.show_results = False
        st.session_state.user_answers = {}
    
    # Display questions
    if st.session_state.current_questions:
        st.subheader("Questions")
        
        for i, question in enumerate(st.session_state.current_questions):
            st.write(f"**Question {i+1}:** {question['question']}")
            
            # Display options
            for j, option in enumerate(question["options"]):
                key = f"q{i}_option{j}"
                if key not in st.session_state.user_answers:
                    st.session_state.user_answers[key] = None
                
                st.radio(
                    f"Option {j+1}",
                    [option],
                    key=key,
                    disabled=st.session_state.show_results
                )
            
            # Show feedback if results are displayed
            if st.session_state.show_results:
                result = st.session_state.mcq_manager.check_answer(
                    question,
                    st.session_state.user_answers.get(f"q{i}_option{question['correct_answer']}")
                )
                
                if result["is_correct"]:
                    st.success("Correct!")
                else:
                    st.error(f"Incorrect. The correct answer is: {question['options'][result['correct_option']]}")
                
                st.info(f"Explanation: {result['explanation']}")
            
            st.markdown("---")
        
        # Submit button
        if not st.session_state.show_results:
            if st.button("Submit Answers"):
                st.session_state.show_results = True
                st.experimental_rerun()
        
        # Try new questions button
        if st.button("Try New Questions"):
            st.session_state.current_questions = []
            st.session_state.user_answers = {}
            st.session_state.show_results = False
            st.experimental_rerun()

def show_analytics():
    st.header("Analytics")
    st.write("View your interview performance metrics")
    
    # Check if there are any interview responses
    if not st.session_state.get("interview_responses", []):
        st.info("Complete an interview to see your analytics!")
        return
    
    # Calculate metrics
    responses = st.session_state.interview_responses
    total_questions = len(responses)
    correct_answers = sum(1 for r in responses if r["similarity_score"] >= 0.5)
    incorrect_answers = total_questions - correct_answers
    
    # Create two columns for the pie charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Answer Distribution")
        # Create pie chart for answer distribution
        fig1 = px.pie(
            values=[correct_answers, incorrect_answers],
            names=["Correct", "Incorrect"],
            color=["Correct", "Incorrect"],
            color_discrete_map={
                "Correct": "#059669",  # Green
                "Incorrect": "#DC2626"  # Red
            },
            hole=0.4
        )
        fig1.update_traces(textposition='inside', textinfo='percent+label')
        fig1.update_layout(
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),
            margin=dict(t=30, l=0, r=0, b=0)
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # Display metrics
        st.metric("Total Questions", total_questions)
        st.metric("Correct Answers", correct_answers)
        st.metric("Accuracy", f"{(correct_answers/total_questions)*100:.1f}%")
    
    with col2:
        st.subheader("Question Categories")
        # Categorize questions
        categories = {
            "Technical": 0,
            "Problem Solving": 0,
            "System Design": 0,
            "Behavioral": 0,
            "Other": 0
        }
        
        # Count questions by category
        for response in responses:
            question = response["question"].lower()
            if any(tech in question for tech in ["algorithm", "data structure", "code", "programming"]):
                categories["Technical"] += 1
            elif any(ps in question for ps in ["solve", "approach", "optimize", "efficiency"]):
                categories["Problem Solving"] += 1
            elif any(sd in question for sd in ["design", "architecture", "system", "scalability"]):
                categories["System Design"] += 1
            elif any(beh in question for beh in ["experience", "team", "challenge", "situation"]):
                categories["Behavioral"] += 1
            else:
                categories["Other"] += 1
        
        # Create pie chart for question categories
        fig2 = px.pie(
            values=list(categories.values()),
            names=list(categories.keys()),
            color=list(categories.keys()),
            color_discrete_sequence=px.colors.qualitative.Set3,
            hole=0.4
        )
        fig2.update_traces(textposition='inside', textinfo='percent+label')
        fig2.update_layout(
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),
            margin=dict(t=30, l=0, r=0, b=0)
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # Display category metrics
        for category, count in categories.items():
            if count > 0:
                st.metric(category, count)
    
    # Performance over time
    st.subheader("Performance Over Time")
    
    # Create line chart for similarity scores
    scores = [r["similarity_score"] for r in responses]
    question_numbers = list(range(1, len(scores) + 1))
    
    fig3 = px.line(
        x=question_numbers,
        y=scores,
        markers=True,
        labels={
            "x": "Question Number",
            "y": "Similarity Score"
        }
    )
    fig3.update_layout(
        yaxis=dict(
            range=[0, 1],
            tickformat=".0%"
        ),
        showlegend=False,
        margin=dict(t=30, l=0, r=0, b=0)
    )
    fig3.add_hline(
        y=0.5,
        line_dash="dash",
        line_color="red",
        annotation_text="Acceptable Score Threshold",
        annotation_position="bottom right"
    )
    st.plotly_chart(fig3, use_container_width=True)
    
    # Detailed analysis
    st.subheader("Detailed Analysis")
    
    # Create expandable sections for different metrics
    with st.expander("Answer Quality Analysis", expanded=True):
        # Calculate average scores by category
        category_scores = {category: [] for category in categories.keys()}
        for response in responses:
            question = response["question"].lower()
            score = response["similarity_score"]
            
            if any(tech in question for tech in ["algorithm", "data structure", "code", "programming"]):
                category_scores["Technical"].append(score)
            elif any(ps in question for ps in ["solve", "approach", "optimize", "efficiency"]):
                category_scores["Problem Solving"].append(score)
            elif any(sd in question for sd in ["design", "architecture", "system", "scalability"]):
                category_scores["System Design"].append(score)
            elif any(beh in question for beh in ["experience", "team", "challenge", "situation"]):
                category_scores["Behavioral"].append(score)
            else:
                category_scores["Other"].append(score)
        
        # Display average scores by category
        col1, col2, col3 = st.columns(3)
        for i, (category, scores) in enumerate(category_scores.items()):
            if scores:
                avg_score = sum(scores) / len(scores)
                with [col1, col2, col3][i % 3]:
                    st.metric(
                        f"{category} Average",
                        f"{avg_score:.1%}",
                        delta=f"{avg_score - 0.5:.1%}" if avg_score >= 0.5 else None
                    )
    
    with st.expander("Follow-up Analysis", expanded=True):
        # Calculate follow-up statistics
        total_follow_ups = sum(len(r["follow_ups"]) for r in responses)
        questions_with_follow_ups = sum(1 for r in responses if r["follow_ups"])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Follow-ups", total_follow_ups)
        with col2:
            st.metric("Questions with Follow-ups", questions_with_follow_ups)
        
        # Display follow-up success rate
        if total_follow_ups > 0:
            follow_up_scores = []
            for response in responses:
                for follow_up in response["follow_ups"]:
                    follow_up_scores.append(follow_up["similarity_score"])
            
            avg_follow_up_score = sum(follow_up_scores) / len(follow_up_scores)
            st.metric(
                "Average Follow-up Score",
                f"{avg_follow_up_score:.1%}",
                delta=f"{avg_follow_up_score - 0.5:.1%}" if avg_follow_up_score >= 0.5 else None
            )
    
    # Generate and download PDF report
    st.subheader("Download Report")
    if st.button("Generate PDF Report"):
        with st.spinner("Generating report..."):
            # Prepare interview data for report
            interview_data = {
                'total_questions': total_questions,
                'correct_answers': correct_answers,
                'accuracy': (correct_answers/total_questions)*100,
                'average_score': sum(scores)/len(scores)*100,
                'categories': categories,
                'scores': scores,
                'category_scores': category_scores,
                'total_follow_ups': total_follow_ups,
                'avg_follow_up_score': avg_follow_up_score if total_follow_ups > 0 else 0
            }
            
            # Create temporary file for PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                # Generate PDF report
                report_generator = ReportGenerator()
                pdf_path = report_generator.generate_report(interview_data, tmp_file.name)
                
                # Read the PDF file
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                
                # Create download button
                st.download_button(
                    label="Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"interview_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
                
                # Clean up temporary file
                os.unlink(pdf_path)

def show_voice_chat():
    st.header("Voice Chat")
    
    # Avatar selection
    avatar_id = st.selectbox(
        "Choose your interviewer",
        ["amy", "john", "sarah"],
        format_func=lambda x: x.capitalize()
    )
    
    # Avatar container
    st.markdown('<div class="avatar-container">', unsafe_allow_html=True)
    if st.session_state.current_avatar_video:
        st.video(st.session_state.current_avatar_video)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Initialize WebRTC
    webrtc_ctx = webrtc.webrtc_streamer(
        key="voice-chat",
        mode=webrtc.StreamingMode.SOUND,
        audio_receiver_size=1024,
        media_stream_constraints={"video": False, "audio": True},
    )
    
    # Chat interface
    st.subheader("Chat")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.container():
            st.markdown(f"""
                <div class="chat-message {message['role']}">
                    <div class="content">{message['content']}</div>
                </div>
            """, unsafe_allow_html=True)
    
    # Process audio input
    if webrtc_ctx.audio_receiver:
        try:
            audio_frames = webrtc_ctx.audio_receiver.get_frames()
            for audio_frame in audio_frames:
                # Convert audio frame to numpy array
                audio_data = audio_frame.to_ndarray()
                
                # Process audio input
                transcribed_text = st.session_state.voice_processor.process_audio_input(
                    audio_data=audio_data,
                    sample_rate=audio_frame.sample_rate
                )
                
                if transcribed_text:
                    # Add to chat history
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": transcribed_text
                    })
                    
                    # Get AI response
                    response = st.session_state.interview_manager.get_response(transcribed_text)
                    
                    # Generate avatar video
                    with st.spinner("Generating avatar response..."):
                        video_path = st.session_state.avatar_manager.create_talking_avatar(
                            text=response,
                            avatar_id=avatar_id
                        )
                        
                        if video_path:
                            st.session_state.current_avatar_video = video_path
                            st.experimental_rerun()
                    
                    # Add response to chat history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response
                    })
        except Exception as e:
            st.error(f"Error processing audio: {str(e)}")
    
    # Text input as fallback
    text_input = st.text_input("Or type your message here")
    if st.button("Send"):
        if text_input:
            # Add to chat history
            st.session_state.chat_history.append({
                "role": "user",
                "content": text_input
            })
            
            # Get AI response
            response = st.session_state.interview_manager.get_response(text_input)
            
            # Generate avatar video
            with st.spinner("Generating avatar response..."):
                video_path = st.session_state.avatar_manager.create_talking_avatar(
                    text=response,
                    avatar_id=avatar_id
                )
                
                if video_path:
                    st.session_state.current_avatar_video = video_path
                    st.experimental_rerun()
            
            # Add response to chat history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response
            })

if __name__ == "__main__":
    main() 