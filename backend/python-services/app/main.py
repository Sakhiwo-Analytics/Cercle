from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv
import httpx
from typing import Optional, List, Dict, Any, Union
import json

# Import models
from models.request_models import (
    QueryRequest, 
    ResearchRequest, 
    WritingRequest,
    DocumentAnalysisRequest,
    ModelSelectionRequest,
    NotesRequest,
    MindMapRequest,
    FlashcardsRequest,
    CitationCheckRequest,
    SourceSuggestionRequest,
    CitationFormatRequest
)

# Import services
from services.auto_notes import AutoNotesGenerator
from services.citation_assistant import CitationAssistant

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Cercle AI Services",
    description="FastAPI microservices for AI processing in Cercle",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize services
auto_notes_generator = AutoNotesGenerator()
citation_assistant = CitationAssistant()

# Supabase authentication verification
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase configuration missing"
        )
    
    # Verify token with Supabase
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{supabase_url}/auth/v1/user",
            headers={
                "Authorization": f"Bearer {token}",
                "apikey": supabase_key
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        user_data = response.json()
        return user_data

@app.get("/")
async def root():
    return {"message": "Welcome to Cercle AI Services"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Smart Query Engine endpoint
@app.post("/api/query")
async def process_query(query: str, user: Dict[str, Any] = Depends(verify_token)):
    """
    Process a query using the Smart Query Engine
    """
    # This is a placeholder for the actual AI processing
    # In a real implementation, this would call an AI service
    
    if "quantum" in query.lower():
        result = {
            "title": "Quantum Mechanics",
            "content": f"Processed result for: {query}",
            "sections": [
                {
                    "title": "Basic Principles",
                    "content": "Quantum mechanics is a fundamental theory in physics that provides a description of the physical properties of nature at the scale of atoms and subatomic particles."
                },
                {
                    "title": "Mathematical Formulation",
                    "content": "The mathematical formulations of quantum mechanics are abstract. They describe the wave-like behavior of subatomic particles using complex mathematical structures."
                }
            ],
            "formulas": [
                {
                    "name": "Schrödinger Equation",
                    "latex": "i\\hbar\\frac{\\partial}{\\partial t}\\Psi(\\mathbf{r},t) = \\hat H\\Psi(\\mathbf{r},t)"
                }
            ],
            "references": [
                {
                    "title": "Introduction to Quantum Mechanics",
                    "author": "David J. Griffiths",
                    "year": 2017
                },
                {
                    "title": "Quantum Physics",
                    "author": "Stephen Gasiorowicz",
                    "year": 2003
                }
            ]
        }
    else:
        result = {
            "title": query.title(),
            "content": f"Processed result for: {query}",
            "sections": [
                {
                    "title": "Overview",
                    "content": f"This is an overview of {query}."
                }
            ],
            "references": []
        }
    
    return {
        "query": query,
        "result": result,
        "metadata": {
            "processing_time": 0.5,
            "model": "placeholder-model",
            "user_id": user["id"]
        }
    }

# Research Amplifier endpoint
@app.post("/api/research")
async def amplify_research(topic: str, user: Dict[str, Any] = Depends(verify_token)):
    """
    Amplify research on a given topic
    """
    # This is a placeholder for the actual AI processing
    return {
        "topic": topic,
        "suggestions": [
            f"Research direction 1 for {topic}",
            f"Research direction 2 for {topic}",
            f"Research direction 3 for {topic}"
        ],
        "related_topics": [
            f"Related topic 1 to {topic}",
            f"Related topic 2 to {topic}",
            f"Related topic 3 to {topic}"
        ],
        "key_papers": [
            {
                "title": f"Important paper about {topic}",
                "authors": ["Author 1", "Author 2"],
                "year": 2023,
                "relevance": 0.95
            },
            {
                "title": f"Another key paper on {topic}",
                "authors": ["Author 3", "Author 4"],
                "year": 2022,
                "relevance": 0.88
            }
        ],
        "user_id": user["id"]
    }

# Writing Assistant endpoint
@app.post("/api/writing")
async def assist_writing(content: str, user: Dict[str, Any] = Depends(verify_token)):
    """
    Provide writing assistance
    """
    # This is a placeholder for the actual AI processing
    return {
        "original": content,
        "suggestions": {
            "grammar": ["Grammar suggestion 1", "Grammar suggestion 2"],
            "style": ["Style suggestion 1", "Style suggestion 2"],
            "citations": ["Citation suggestion 1", "Citation suggestion 2"]
        },
        "improved_version": f"Improved version of: {content}",
        "user_id": user["id"]
    }

# Auto-Notes endpoints
@app.post("/api/notes/structure")
async def generate_structured_notes(
    notes_request: NotesRequest,
    user: Dict[str, Any] = Depends(verify_token)
):
    """
    Generate structured notes from unstructured text
    """
    try:
        result = await auto_notes_generator.generate_structured_notes(
            content=notes_request.content,
            format_type=notes_request.format_type,
            subject=notes_request.subject,
            user_id=user["id"]
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating notes: {str(e)}"
        )

@app.post("/api/notes/mindmap")
async def generate_mind_map(
    mindmap_request: MindMapRequest,
    user: Dict[str, Any] = Depends(verify_token)
):
    """
    Generate a mind map from content
    """
    try:
        result = await auto_notes_generator.generate_mind_map(
            content=mindmap_request.content,
            central_topic=mindmap_request.central_topic,
            user_id=user["id"]
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating mind map: {str(e)}"
        )

@app.post("/api/notes/flashcards")
async def generate_flashcards(
    flashcards_request: FlashcardsRequest,
    user: Dict[str, Any] = Depends(verify_token)
):
    """
    Generate study flashcards from content
    """
    try:
        result = await auto_notes_generator.generate_flashcards(
            content=flashcards_request.content,
            difficulty=flashcards_request.difficulty,
            count=flashcards_request.count,
            user_id=user["id"]
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating flashcards: {str(e)}"
        )

# Citation Assistant endpoints
@app.post("/api/writing/check-citations")
async def check_citations(
    citation_check_request: CitationCheckRequest,
    user: Dict[str, Any] = Depends(verify_token)
):
    """
    Check content for statements that need citations
    """
    try:
        result = await citation_assistant.check_citations(
            content=citation_check_request.content,
            user_id=user["id"]
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking citations: {str(e)}"
        )

@app.post("/api/writing/suggest-sources")
async def suggest_sources(
    source_suggestion_request: SourceSuggestionRequest,
    user: Dict[str, Any] = Depends(verify_token)
):
    """
    Suggest potential sources for a statement
    """
    try:
        result = await citation_assistant.suggest_sources(
            statement=source_suggestion_request.statement,
            topic=source_suggestion_request.topic,
            user_id=user["id"]
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error suggesting sources: {str(e)}"
        )

@app.post("/api/writing/format-citations")
async def format_citations(
    citation_format_request: CitationFormatRequest,
    user: Dict[str, Any] = Depends(verify_token)
):
    """
    Format citations according to academic styles
    """
    try:
        result = await citation_assistant.format_citations(
            sources=citation_format_request.sources,
            style=citation_format_request.style,
            user_id=user["id"]
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error formatting citations: {str(e)}"
        )

@app.get("/api/writing/citation-styles")
async def get_citation_styles(
    user: Dict[str, Any] = Depends(verify_token)
):
    """
    Get available citation styles
    """
    try:
        result = await citation_assistant.get_citation_styles()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting citation styles: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8001)))
