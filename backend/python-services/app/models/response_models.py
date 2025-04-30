"""
Pydantic models for API response data structures
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union

class QueryMetadata(BaseModel):
    """Metadata for query responses"""
    processing_time: float = Field(..., description="Processing time in seconds")
    model: str = Field(..., description="AI model used for processing")
    user_id: str = Field(..., description="ID of the user who made the request")
    token_usage: Optional[int] = Field(None, description="Number of tokens used")
    tutor_mode: Optional[bool] = Field(False, description="Whether tutor mode was enabled")

class QuerySection(BaseModel):
    """Section of a query response"""
    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content")

class Formula(BaseModel):
    """Mathematical formula"""
    name: str = Field(..., description="Formula name")
    latex: str = Field(..., description="LaTeX representation of the formula")

class Reference(BaseModel):
    """Academic reference"""
    title: str = Field(..., description="Reference title")
    author: Optional[str] = Field(None, description="Author name")
    year: Optional[int] = Field(None, description="Publication year")
    url: Optional[str] = Field(None, description="URL to the reference")
    doi: Optional[str] = Field(None, description="DOI of the reference")

class QueryResult(BaseModel):
    """Result of a query"""
    title: str = Field(..., description="Result title")
    content: str = Field(..., description="Main content")
    sections: Optional[List[QuerySection]] = Field(None, description="Content sections")
    formulas: Optional[List[Formula]] = Field(None, description="Mathematical formulas")
    references: Optional[List[Reference]] = Field(None, description="Academic references")

class QueryResponse(BaseModel):
    """Response model for Smart Query Engine"""
    query: str = Field(..., description="Original query")
    result: QueryResult = Field(..., description="Query result")
    conversation_id: str = Field(..., description="Conversation ID for threading")
    metadata: QueryMetadata = Field(..., description="Query metadata")

class KeyPaper(BaseModel):
    """Key paper for research"""
    title: str = Field(..., description="Paper title")
    authors: List[str] = Field(..., description="Paper authors")
    year: int = Field(..., description="Publication year")
    relevance: float = Field(..., description="Relevance score (0-1)")
    url: Optional[str] = Field(None, description="URL to the paper")
    abstract: Optional[str] = Field(None, description="Paper abstract")

class ResearchResponse(BaseModel):
    """Response model for Research Amplifier"""
    topic: str = Field(..., description="Research topic")
    suggestions: List[str] = Field(..., description="Research directions")
    related_topics: List[str] = Field(..., description="Related topics")
    key_papers: List[KeyPaper] = Field(..., description="Key papers")
    user_id: str = Field(..., description="ID of the user who made the request")

class PDFUploadResponse(BaseModel):
    """Response model for PDF upload"""
    document_id: str = Field(..., description="Document ID")
    filename: str = Field(..., description="Original filename")
    page_count: int = Field(..., description="Number of pages")
    status: str = Field(..., description="Processing status")
    summary: Optional[str] = Field(None, description="Document summary")
    user_id: str = Field(..., description="ID of the user who uploaded the document")

class DocumentAnalysisResponse(BaseModel):
    """Response model for document analysis"""
    document_id: str = Field(..., description="Document ID")
    analysis_type: str = Field(..., description="Type of analysis performed")
    result: str = Field(..., description="Analysis result")
    user_id: str = Field(..., description="ID of the user who requested the analysis")

class WritingSuggestions(BaseModel):
    """Suggestions for writing improvement"""
    grammar: List[str] = Field(..., description="Grammar suggestions")
    style: List[str] = Field(..., description="Style suggestions")
    citations: List[str] = Field(..., description="Citation suggestions")

class WritingResponse(BaseModel):
    """Response model for Writing Assistant"""
    original: str = Field(..., description="Original content")
    suggestions: WritingSuggestions = Field(..., description="Improvement suggestions")
    improved_version: str = Field(..., description="Improved version")
    user_id: str = Field(..., description="ID of the user who made the request")

class ModelSelectionResponse(BaseModel):
    """Response model for AI model selection"""
    selected_model: str = Field(..., description="Selected AI model")
    confidence: float = Field(..., description="Confidence score (0-1)")
    reasoning: str = Field(..., description="Reasoning for model selection")
    user_id: str = Field(..., description="ID of the user who made the request")
