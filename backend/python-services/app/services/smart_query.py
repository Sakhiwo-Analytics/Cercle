"""
Smart Query Engine service for processing academic queries
"""
import os
import uuid
from typing import Dict, Any, List, Optional
from ..utils.openai_client import OpenAIClient
from ..utils.anthropic_client import AnthropicClient
from ..utils.wolfram_client import WolframClient
from ..utils.langchain_utils import LangChainManager

class SmartQueryEngine:
    """
    Smart Query Engine for processing academic queries with context-aware threading
    and AI Tutor Mode
    """
    
    def __init__(self):
        """Initialize the Smart Query Engine with required clients"""
        self.openai_client = OpenAIClient()
        self.anthropic_client = AnthropicClient()
        self.wolfram_client = WolframClient()
        self.langchain_manager = LangChainManager()
        
        # In-memory conversation store (in production, this would be a database)
        self.conversations = {}
    
    async def process_query(
        self, 
        query: str, 
        context: Optional[List[Dict[str, Any]]] = None,
        conversation_id: Optional[str] = None,
        tutor_mode: bool = False,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Process a query using the Smart Query Engine
        
        Args:
            query: The query text to process
            context: Optional conversation context for threading
            conversation_id: ID of an existing conversation to continue
            tutor_mode: Enable AI Tutor Mode for step-by-step explanations
            user_id: ID of the user making the query
            
        Returns:
            Dictionary with query results and metadata
        """
        # If conversation_id is provided, retrieve existing conversation
        if conversation_id and conversation_id in self.conversations:
            context = self.conversations[conversation_id]
        
        # If no context is provided, initialize empty context
        if not context:
            context = []
        
        # Determine which AI service to use based on query content and task
        model_selection = await self._select_model(query, tutor_mode)
        selected_model = model_selection["selected_model"]
        
        # Process query with selected model
        if selected_model == "wolfram-alpha":
            result = await self._process_with_wolfram(query)
        elif selected_model == "claude":
            result = await self._process_with_anthropic(query, context, tutor_mode)
        else:  # Default to OpenAI
            result = await self._process_with_openai(query, context, tutor_mode)
        
        # Update conversation context
        context.append({"role": "user", "content": query})
        context.append({"role": "assistant", "content": result["content"]})
        
        # Trim context if it gets too long (keep last 10 messages)
        if len(context) > 10:
            context = context[-10:]
        
        # Generate or use existing conversation ID
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        # Store updated conversation
        self.conversations[conversation_id] = context
        
        # Format query result
        formatted_result = self._format_query_result(query, result, selected_model)
        
        # Return complete response
        return {
            "query": query,
            "result": formatted_result,
            "conversation_id": conversation_id,
            "metadata": {
                "processing_time": result.get("processing_time", 0),
                "model": result.get("model", selected_model),
                "user_id": user_id,
                "token_usage": result.get("token_usage", 0),
                "tutor_mode": tutor_mode
            }
        }
    
    async def _select_model(self, query: str, tutor_mode: bool) -> Dict[str, Any]:
        """
        Select the best AI model for a given query
        
        Args:
            query: The query text to analyze
            tutor_mode: Whether tutor mode is enabled
            
        Returns:
            Dictionary with selected model and reasoning
        """
        # Check if query is computational (suitable for Wolfram Alpha)
        if self.wolfram_client.is_computational_query(query):
            return {
                "selected_model": "wolfram-alpha",
                "confidence": 0.9,
                "reasoning": "Query contains computational elements suitable for Wolfram Alpha"
            }
        
        # Use Claude for tutor mode or longer queries
        if tutor_mode or len(query) > 500:
            return {
                "selected_model": "claude",
                "confidence": 0.8,
                "reasoning": "Query requires detailed explanations or is lengthy, suitable for Claude"
            }
        
        # Default to OpenAI for general queries
        return {
            "selected_model": "gpt-4",
            "confidence": 0.7,
            "reasoning": "General query suitable for GPT-4"
        }
    
    async def _process_with_openai(
        self, 
        query: str, 
        context: List[Dict[str, Any]],
        tutor_mode: bool
    ) -> Dict[str, Any]:
        """Process a query using OpenAI"""
        # Build messages with context
        messages = []
        
        # Add system message based on tutor mode
        if tutor_mode:
            messages.append({
                "role": "system", 
                "content": "You are an educational AI tutor for students and researchers. "
                           "Provide step-by-step explanations and break down complex concepts clearly. "
                           "Use examples and analogies where appropriate. "
                           "For mathematical or scientific concepts, explain the underlying principles. "
                           "Cite academic sources when possible."
            })
        else:
            messages.append({
                "role": "system", 
                "content": "You are a helpful academic research assistant. "
                           "Provide accurate, detailed information with citations when possible. "
                           "Focus on scholarly sources and academic rigor. "
                           "Present balanced viewpoints on controversial topics. "
                           "Highlight key concepts and relationships between ideas."
            })
        
        # Add context messages
        for msg in context:
            messages.append(msg)
        
        # Add the current query
        messages.append({"role": "user", "content": query})
        
        # Call OpenAI API
        return await self.openai_client.generate_completion(
            messages=messages,
            model="gpt-4",
            temperature=0.7,
            max_tokens=2000
        )
    
    async def _process_with_anthropic(
        self, 
        query: str, 
        context: List[Dict[str, Any]],
        tutor_mode: bool
    ) -> Dict[str, Any]:
        """Process a query using Anthropic Claude"""
        # Build messages with context
        messages = []
        
        # Add system message based on tutor mode
        if tutor_mode:
            messages.append({
                "role": "system", 
                "content": "You are an educational AI tutor for students and researchers. "
                           "Provide step-by-step explanations and break down complex concepts clearly. "
                           "Use examples and analogies where appropriate. "
                           "For mathematical or scientific concepts, explain the underlying principles. "
                           "Cite academic sources when possible."
            })
        else:
            messages.append({
                "role": "system", 
                "content": "You are a helpful academic research assistant. "
                           "Provide accurate, detailed information with citations when possible. "
                           "Focus on scholarly sources and academic rigor. "
                           "Present balanced viewpoints on controversial topics. "
                           "Highlight key concepts and relationships between ideas."
            })
        
        # Add context messages
        for msg in context:
            messages.append(msg)
        
        # Add the current query
        messages.append({"role": "user", "content": query})
        
        # Call Anthropic API
        return await self.anthropic_client.generate_completion(
            messages=messages,
            model="claude-2",
            temperature=0.7,
            max_tokens=2000
        )
    
    async def _process_with_wolfram(self, query: str) -> Dict[str, Any]:
        """Process a query using Wolfram Alpha"""
        # Call Wolfram Alpha API
        wolfram_result = await self.wolfram_client.process_query(query)
        
        # Format the result as content
        content = ""
        
        # Add simple answer if available
        if wolfram_result.get("simple_answer"):
            content += f"Answer: {wolfram_result['simple_answer']}\n\n"
        
        # Add pod results
        for pod in wolfram_result.get("pods", []):
            content += f"## {pod['title']}\n\n"
            
            for subpod in pod.get("subpods", []):
                if subpod.get("plaintext"):
                    content += f"{subpod['plaintext']}\n\n"
                
                if subpod.get("img"):
                    content += f"[Image: {pod['title']}]({subpod['img']})\n\n"
        
        # Return formatted result
        return {
            "content": content,
            "model": "wolfram-alpha",
            "processing_time": wolfram_result.get("processing_time", 0.5)
        }
    
    def _format_query_result(self, query: str, result: Dict[str, Any], model: str) -> Dict[str, Any]:
        """
        Format the query result into a structured response
        
        Args:
            query: The original query
            result: The raw result from the AI service
            model: The model used for processing
            
        Returns:
            Structured query result
        """
        content = result.get("content", "")
        
        # For Wolfram Alpha results, use the existing format
        if model == "wolfram-alpha":
            return {
                "title": query,
                "content": content,
                "sections": [],
                "formulas": [],
                "references": []
            }
        
        # For text-based models, try to extract sections, formulas, and references
        # This is a simplified implementation - in production, you would use more robust parsing
        
        # Extract title (first line or query)
        title = query
        lines = content.split("\n")
        if lines and lines[0].strip():
            title = lines[0].strip()
        
        # Extract sections (look for markdown headings)
        sections = []
        current_section = None
        current_content = []
        
        for line in lines:
            if line.startswith("## "):
                # Save previous section if exists
                if current_section:
                    sections.append({
                        "title": current_section,
                        "content": "\n".join(current_content).strip()
                    })
                
                # Start new section
                current_section = line.replace("## ", "").strip()
                current_content = []
            elif line.startswith("# "):
                # Skip top-level headings (likely the title)
                continue
            elif current_section:
                # Add line to current section
                current_content.append(line)
            
        # Add final section if exists
        if current_section:
            sections.append({
                "title": current_section,
                "content": "\n".join(current_content).strip()
            })
        
        # If no sections were found, create a default one
        if not sections:
            sections.append({
                "title": "Overview",
                "content": content
            })
        
        # Extract formulas (look for LaTeX delimiters)
        import re
        formulas = []
        latex_pattern = r"\$\$(.*?)\$\$"
        latex_matches = re.findall(latex_pattern, content, re.DOTALL)
        
        for i, latex in enumerate(latex_matches):
            formulas.append({
                "name": f"Formula {i+1}",
                "latex": latex.strip()
            })
        
        # Extract references (look for citation patterns)
        references = []
        reference_patterns = [
            r"\[(.*?)\]\((.*?)\)",  # Markdown links
            r"([A-Za-z]+, [A-Za-z]\.(?:, [A-Za-z]\.)* \(\d{4}\).*?)\.",  # APA style
            r"(\d+\. .*?\(\d{4}\).*?)\."  # Numbered references
        ]
        
        for pattern in reference_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple):
                    # For markdown links
                    title = match[0]
                    url = match[1]
                    references.append({
                        "title": title,
                        "url": url
                    })
                else:
                    # For text citations
                    references.append({
                        "title": match
                    })
        
        # Return structured result
        return {
            "title": title,
            "content": content,
            "sections": sections,
            "formulas": formulas,
            "references": references
        }
