"""
AI Router service for intelligent model selection and vector database integration
"""
import os
from typing import Dict, Any, List, Optional
from ..utils.langchain_utils import LangChainManager

class AIRouter:
    """
    AI Router for smart model selection and vector database integration
    using LangChain and Pinecone
    """
    
    def __init__(self):
        """Initialize the AI Router with required components"""
        self.langchain_manager = LangChainManager()
        
        # Define available models
        self.available_models = {
            "gpt-4": {
                "provider": "openai",
                "strengths": ["general knowledge", "reasoning", "creative tasks", "code generation"],
                "max_tokens": 8192,
                "cost_per_1k_tokens": 0.06
            },
            "gpt-3.5-turbo": {
                "provider": "openai",
                "strengths": ["fast responses", "general knowledge", "cost-effective"],
                "max_tokens": 4096,
                "cost_per_1k_tokens": 0.002
            },
            "claude-2": {
                "provider": "anthropic",
                "strengths": ["longer content", "nuanced understanding", "ethical considerations"],
                "max_tokens": 100000,
                "cost_per_1k_tokens": 0.08
            },
            "wolfram-alpha": {
                "provider": "wolfram",
                "strengths": ["computational queries", "math", "science", "factual data"],
                "max_tokens": None,
                "cost_per_1k_tokens": None
            }
        }
    
    async def select_model(
        self, 
        query: str, 
        task_type: str,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Select the best AI model for a given query and task type
        
        Args:
            query: The query or content to process
            task_type: Type of task (query, research, writing, etc.)
            user_id: ID of the user making the request
            
        Returns:
            Dictionary with selected model and reasoning
        """
        # Use LangChain to select the best model
        model_selection = await self.langchain_manager.select_best_model(query, task_type)
        
        # Get model details
        selected_model = model_selection["selected_model"]
        model_details = self.available_models.get(selected_model, {})
        
        # Add model details to result
        result = {
            "selected_model": selected_model,
            "confidence": model_selection["confidence"],
            "reasoning": model_selection["reasoning"],
            "provider": model_details.get("provider"),
            "strengths": model_details.get("strengths"),
            "max_tokens": model_details.get("max_tokens"),
            "cost_per_1k_tokens": model_details.get("cost_per_1k_tokens"),
            "user_id": user_id
        }
        
        return result
    
    async def search_similar_content(
        self, 
        query: str,
        k: int = 5,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Search for similar content in the vector database
        
        Args:
            query: The query to search for
            k: Number of results to return
            user_id: ID of the user making the request
            
        Returns:
            Dictionary with search results
        """
        # Search for similar documents
        results = await self.langchain_manager.search_similar_documents(query, k)
        
        # Format results
        return {
            "query": query,
            "results": results,
            "user_id": user_id
        }
    
    async def store_vector_embedding(
        self, 
        text: str,
        metadata: Dict[str, Any],
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Store text as vector embeddings in the database
        
        Args:
            text: The text to store
            metadata: Metadata to associate with the text
            user_id: ID of the user making the request
            
        Returns:
            Dictionary with storage result
        """
        # Add user ID to metadata
        if user_id:
            metadata["user_id"] = user_id
        
        # Store document in vector database
        ids = await self.langchain_manager.store_document(text, metadata)
        
        return {
            "success": True,
            "stored_ids": ids,
            "text_length": len(text),
            "user_id": user_id
        }
