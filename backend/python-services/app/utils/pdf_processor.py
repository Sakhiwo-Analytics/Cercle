"""
PDF processing utilities for document analysis
"""
import os
import tempfile
import uuid
from typing import Dict, Any, List, Optional
from fastapi import UploadFile
from unstructured.partition.pdf import partition_pdf
from pdf2image import convert_from_path
import pytesseract
from .openai_client import OpenAIClient

class PDFProcessor:
    """Processor for PDF documents"""
    
    def __init__(self):
        """Initialize the PDF processor"""
        # Set pytesseract path if provided in environment variables
        pytesseract_path = os.getenv("PYTESSERACT_PATH")
        if pytesseract_path:
            pytesseract.pytesseract.tesseract_cmd = pytesseract_path
        
        # Initialize OpenAI client for summarization
        self.openai_client = OpenAIClient()
    
    async def process_pdf(self, file: UploadFile, user_id: str) -> Dict[str, Any]:
        """
        Process a PDF file and extract its content
        
        Args:
            file: The uploaded PDF file
            user_id: ID of the user who uploaded the file
            
        Returns:
            Dictionary with document metadata and summary
        """
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                # Write the uploaded file content to the temporary file
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            # Process the PDF file
            elements = partition_pdf(temp_file_path)
            
            # Extract text content
            text_content = "\n\n".join([str(element) for element in elements])
            
            # Generate a document ID
            document_id = str(uuid.uuid4())
            
            # Count pages in the PDF
            try:
                images = convert_from_path(temp_file_path)
                page_count = len(images)
            except Exception:
                # Fallback: estimate page count based on elements
                page_count = max(1, len(elements) // 5)
            
            # Generate a summary using OpenAI
            summary = await self._generate_summary(text_content[:8000])
            
            # Clean up the temporary file
            os.unlink(temp_file_path)
            
            # Return document metadata
            return {
                "document_id": document_id,
                "filename": file.filename,
                "page_count": page_count,
                "status": "processed",
                "summary": summary,
                "user_id": user_id
            }
        except Exception as e:
            # Clean up the temporary file if it exists
            if 'temp_file_path' in locals():
                try:
                    os.unlink(temp_file_path)
                except Exception:
                    pass
            
            raise Exception(f"Error processing PDF: {str(e)}")
    
    async def _generate_summary(self, text: str) -> str:
        """
        Generate a summary of the document text
        
        Args:
            text: The document text to summarize
            
        Returns:
            Summary of the document
        """
        try:
            # Truncate text if it's too long
            if len(text) > 8000:
                text = text[:8000] + "..."
            
            # Generate summary using OpenAI
            response = await self.openai_client.generate_completion(
                messages=[
                    {"role": "system", "content": "You are a helpful research assistant. Provide a brief summary of the following document."},
                    {"role": "user", "content": text}
                ],
                model="gpt-3.5-turbo",
                max_tokens=300
            )
            
            return response["content"]
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    async def analyze_document(self, document_id: str, analysis_type: str, text_content: str) -> Dict[str, Any]:
        """
        Analyze a document based on its content and analysis type
        
        Args:
            document_id: ID of the document to analyze
            analysis_type: Type of analysis to perform
            text_content: Text content of the document
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Define system prompts for different analysis types
            system_prompts = {
                "summary": "You are a research assistant. Provide a comprehensive summary of the following document.",
                "key_points": "You are a research assistant. Extract and list the key points from the following document.",
                "bias": "You are a critical research analyst. Identify potential biases in the following document, considering author perspective, methodology, and language.",
                "methodology": "You are a research methodology expert. Analyze and evaluate the methodology used in the following document."
            }
            
            if analysis_type not in system_prompts:
                raise ValueError(f"Invalid analysis type: {analysis_type}")
            
            # Truncate text if it's too long
            if len(text_content) > 8000:
                text_content = text_content[:8000] + "..."
            
            # Generate analysis using OpenAI
            response = await self.openai_client.generate_completion(
                messages=[
                    {"role": "system", "content": system_prompts[analysis_type]},
                    {"role": "user", "content": text_content}
                ],
                model="gpt-4",
                max_tokens=1000
            )
            
            return {
                "document_id": document_id,
                "analysis_type": analysis_type,
                "result": response["content"]
            }
        except Exception as e:
            raise Exception(f"Error analyzing document: {str(e)}")
