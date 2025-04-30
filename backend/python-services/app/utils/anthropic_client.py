"""
Anthropic Claude API client utilities
"""
import os
from typing import List, Dict, Any, Optional
from anthropic import Anthropic

class AnthropicClient:
    """Client for interacting with Anthropic Claude API"""
    
    def __init__(self):
        """Initialize the Anthropic client with API key from environment variables"""
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not found in environment variables")
        
        self.client = Anthropic(api_key=self.api_key)
    
    async def generate_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "claude-2",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> Dict[str, Any]:
        """
        Generate a completion using Anthropic's Claude API
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Claude model to use (default: claude-2)
            temperature: Sampling temperature (default: 0.7)
            max_tokens: Maximum tokens to generate (default: 2000)
            
        Returns:
            Dictionary with response content and metadata
        """
        try:
            # Convert messages to Claude's prompt format
            prompt = self._convert_messages_to_prompt(messages)
            
            # Call Claude API
            response = self.client.completions.create(
                model=model,
                prompt=prompt,
                max_tokens_to_sample=max_tokens,
                temperature=temperature
            )
            
            # Calculate approximate token usage (Claude doesn't provide this directly)
            approx_prompt_tokens = len(prompt) // 4  # Rough approximation
            approx_completion_tokens = len(response.completion) // 4  # Rough approximation
            approx_total_tokens = approx_prompt_tokens + approx_completion_tokens
            
            return {
                "content": response.completion,
                "model": model,
                "processing_time": approx_total_tokens / 1000,  # Approximation
                "token_usage": approx_total_tokens  # Approximation
            }
        except Exception as e:
            raise Exception(f"Error calling Anthropic API: {str(e)}")
    
    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """
        Convert a list of messages to Claude's prompt format
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            
        Returns:
            Formatted prompt string for Claude
        """
        prompt = ""
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                # Add system message as a Human instruction about Claude's role
                prompt += f"\n\nHuman: {content}\n\nAssistant: I understand my role."
            elif role == "user":
                prompt += f"\n\nHuman: {content}"
            elif role == "assistant":
                prompt += f"\n\nAssistant: {content}"
        
        # Add final Assistant: to prompt Claude to continue
        prompt += "\n\nAssistant:"
        
        return prompt
