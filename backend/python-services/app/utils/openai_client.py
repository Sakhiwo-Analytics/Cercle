"""
OpenAI API client utilities
"""
import os
import openai
from typing import List, Dict, Any, Optional

class OpenAIClient:
    """Client for interacting with OpenAI API"""
    
    def __init__(self):
        """Initialize the OpenAI client with API key from environment variables"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        openai.api_key = self.api_key
        
        # Set organization if available
        self.organization = os.getenv("OPENAI_ORGANIZATION")
        if self.organization:
            openai.organization = self.organization
    
    async def generate_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0
    ) -> Dict[str, Any]:
        """
        Generate a completion using OpenAI's Chat Completion API
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: OpenAI model to use (default: gpt-4)
            temperature: Sampling temperature (default: 0.7)
            max_tokens: Maximum tokens to generate (default: 2000)
            top_p: Nucleus sampling parameter (default: 1.0)
            frequency_penalty: Frequency penalty (default: 0.0)
            presence_penalty: Presence penalty (default: 0.0)
            
        Returns:
            Dictionary with response content and metadata
        """
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty
            )
            
            return {
                "content": response.choices[0].message.content,
                "model": response.model,
                "processing_time": response.usage.total_tokens / 1000,  # Approximation
                "token_usage": response.usage.total_tokens
            }
        except Exception as e:
            raise Exception(f"Error calling OpenAI API: {str(e)}")
    
    async def generate_embeddings(self, texts: List[str], model: str = "text-embedding-ada-002") -> List[List[float]]:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings to embed
            model: OpenAI embedding model to use
            
        Returns:
            List of embedding vectors
        """
        try:
            response = openai.Embedding.create(
                model=model,
                input=texts
            )
            
            # Extract embeddings from response
            embeddings = [item.embedding for item in response.data]
            
            return embeddings
        except Exception as e:
            raise Exception(f"Error generating embeddings: {str(e)}")
