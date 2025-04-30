"""
Pydantic models for API request data structures
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union

class QueryRequest(BaseModel):
    """Request model for Smart Query Engine"""
    query: str = Field(..., description="The query text to process")
    context: Optional[List[Dict[str, Any]]] = Field(
        None, 
        description="Optional conversation context for threading"
    )
    conversation_id: Optional[str] = Field(
        None, 
        description="ID of an existing conversation to continue"
    )
    tutor_mode: Optional[bool] = Field(
        False, 
        description="Enable AI Tutor Mode for step-by-step explanations"
    )

class ResearchRequest(BaseModel):
    """Request model for Research Amplifier"""
    topic: str = Field(..., description="The research topic to amplify")
    sources: Optional[List[str]] = Field(
        None, 
        description="Optional list of source document IDs to include in research"
    )
    analysis_type: Optional[str] = Field(
        "comprehensive", 
        description="Type of analysis to perform (comprehensive, summary, key_points, bias, methodology)"
    )

class WritingRequest(BaseModel):
    """Request model for Writing Assistant"""
    content: str = Field(..., description="The writing content to analyze")
    template: Optional[str] = Field(
        None, 
        description="Optional academic template to apply"
    )
    feedback_types: Optional[List[str]] = Field(
        ["grammar", "style", "citations"], 
        description="Types of feedback to provide"
    )

class DocumentAnalysisRequest(BaseModel):
    """Request model for document analysis"""
    document_id: str = Field(..., description="ID of the document to analyze")
    analysis_type: str = Field(
        ..., 
        description="Type of analysis to perform (summary, key_points, bias, methodology)"
    )

class ModelSelectionRequest(BaseModel):
    """Request model for AI model selection"""
    query: str = Field(..., description="The query or content to process")
    task_type: str = Field(
        ..., 
        description="Type of task (query, research, writing, etc.)"
    )
    user_preferences: Optional[Dict[str, Any]] = Field(
        None, 
        description="Optional user preferences for model selection"
    )

# Auto-Notes Request Models
class NotesRequest(BaseModel):
    """Request model for structured notes generation"""
    content: str = Field(..., description="The content to convert to structured notes")
    format_type: str = Field("outline", description="Type of notes format (outline, cornell, summary)")
    subject: Optional[str] = Field(None, description="Optional subject area for context")

class MindMapRequest(BaseModel):
    """Request model for mind map generation"""
    content: str = Field(..., description="The content to convert to a mind map")
    central_topic: Optional[str] = Field(None, description="Optional central topic for the mind map")

class FlashcardsRequest(BaseModel):
    """Request model for flashcard generation"""
    content: str = Field(..., description="The content to convert to flashcards")
    difficulty: str = Field("medium", description="Difficulty level (easy, medium, hard)")
    count: int = Field(10, description="Number of flashcards to generate")

# Citation Assistant Request Models
class CitationCheckRequest(BaseModel):
    """Request model for citation checking"""
    content: str = Field(..., description="The content to check for needed citations")

class SourceSuggestionRequest(BaseModel):
    """Request model for source suggestions"""
    statement: str = Field(..., description="The statement needing citation")
    topic: Optional[str] = Field(None, description="Optional topic context")

class CitationFormatRequest(BaseModel):
    """Request model for citation formatting"""
    sources: List[Dict[str, Any]] = Field(..., description="List of source information to format")
    style: str = Field("apa", description="Citation style to use (apa, mla, chicago, etc.)")
