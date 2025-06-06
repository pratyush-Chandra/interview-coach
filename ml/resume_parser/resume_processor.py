import fitz  # PyMuPDF
import docx2txt
import re
from typing import Optional, Dict, Any, List
import io
from .text_processor import TextProcessor
from ..rag.vector_store import VectorStoreManager

class ResumeProcessor:
    def __init__(self):
        """Initialize the resume processor with text processor and vector store."""
        self.text_processor = TextProcessor()
        self.vector_store = VectorStoreManager()

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize extracted text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,;:!?()-]', '', text)
        # Remove multiple newlines
        text = re.sub(r'\n+', '\n', text)
        return text.strip()

    @staticmethod
    def extract_from_pdf(file_content: bytes) -> Optional[str]:
        """Extract text from PDF file content."""
        try:
            # Create a PDF document object
            pdf_document = fitz.open(stream=file_content, filetype="pdf")
            text = ""
            
            # Extract text from each page
            for page in pdf_document:
                text += page.get_text()
            
            pdf_document.close()
            return ResumeProcessor.clean_text(text)
        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
            return None

    @staticmethod
    def extract_from_docx(file_content: bytes) -> Optional[str]:
        """Extract text from DOCX file content."""
        try:
            # Create a BytesIO object from the file content
            docx_file = io.BytesIO(file_content)
            # Extract text using docx2txt
            text = docx2txt.process(docx_file)
            return ResumeProcessor.clean_text(text)
        except Exception as e:
            print(f"Error processing DOCX: {str(e)}")
            return None

    def process_resume(self, file_content: bytes, file_type: str) -> Dict[str, Any]:
        """
        Process resume file and return extracted text and chunks.
        
        Args:
            file_content (bytes): The file content
            file_type (str): The type of file ('pdf' or 'docx')
            
        Returns:
            Dict[str, Any]: Dictionary containing extracted text and chunks
        """
        # Extract text from file
        if file_type.lower() == 'pdf':
            extracted_text = self.extract_from_pdf(file_content)
        elif file_type.lower() == 'docx':
            extracted_text = self.extract_from_docx(file_content)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        if not extracted_text:
            return {
                "success": False,
                "error": "Failed to extract text from the resume"
            }
        
        # Create chunks from extracted text
        chunks = self.text_processor.create_chunks(extracted_text)
        chunk_stats = self.text_processor.get_chunk_statistics(chunks)
        
        # Add chunks to vector store
        try:
            self.vector_store.add_documents(chunks)
            vector_store_status = "success"
        except Exception as e:
            print(f"Error adding documents to vector store: {str(e)}")
            vector_store_status = "error"
        
        return {
            "success": True,
            "extracted_text": extracted_text,
            "chunks": chunks,
            "statistics": chunk_stats,
            "vector_store_status": vector_store_status
        }

    def search_resume(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """
        Search the resume content using semantic search.
        
        Args:
            query (str): The search query
            k (int): Number of results to return
            
        Returns:
            List[Dict[str, Any]]: List of relevant chunks with metadata
        """
        try:
            results = self.vector_store.similarity_search(query, k=k)
            return [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": doc.metadata.get("score", 0.0)
                }
                for doc in results
            ]
        except Exception as e:
            print(f"Error searching resume: {str(e)}")
            return [] 