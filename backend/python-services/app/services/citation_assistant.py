"""
Citation Assistant service for checking sources and suggesting citations
"""
import os
import json
import re
from typing import Dict, Any, List, Optional
from ..utils.openai_client import OpenAIClient
from ..utils.langchain_utils import LangChainManager

class CitationAssistant:
    """
    Citation Assistant for checking sources, suggesting citations,
    and ensuring academic integrity in writing
    """
    
    def __init__(self):
        """Initialize the Citation Assistant with required components"""
        self.openai_client = OpenAIClient()
        self.langchain_manager = LangChainManager()
        
        # Citation styles
        self.citation_styles = {
            "apa": "American Psychological Association (APA) 7th edition",
            "mla": "Modern Language Association (MLA) 9th edition",
            "chicago": "Chicago Manual of Style 17th edition (Author-Date)",
            "harvard": "Harvard referencing style",
            "ieee": "Institute of Electrical and Electronics Engineers (IEEE)",
            "ama": "American Medical Association (AMA)",
            "vancouver": "Vancouver style (for medical sciences)"
        }
    
    async def check_citations(
        self, 
        content: str,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Check content for statements that need citations
        
        Args:
            content: The content to check for needed citations
            user_id: ID of the user making the request
            
        Returns:
            Dictionary with citation suggestions
        """
        # Create system prompt for citation checking
        system_prompt = """
        You are an expert academic citation assistant for the Cercle platform.
        Analyze the following academic writing and identify statements that need citations.
        
        For each statement that needs a citation:
        1. Identify the exact text that needs a citation
        2. Explain why it needs a citation (e.g., factual claim, statistics, specific theory)
        3. Provide a suggestion for what kind of source would be appropriate
        
        Format your response as a JSON array of objects:
        [
            {
                "text": "The exact statement that needs a citation",
                "reason": "Why this statement needs a citation",
                "source_suggestion": "What kind of source would be appropriate",
                "start_index": The character index where the statement starts,
                "end_index": The character index where the statement ends
            },
            ...
        ]
        
        Focus on:
        - Factual claims that aren't common knowledge
        - Statistics, data, and specific numbers
        - Theories, concepts, or ideas attributed to specific scholars
        - Direct quotes or paraphrased content
        - Specific examples or case studies
        """
        
        # Call OpenAI API
        response = await self.openai_client.generate_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ],
            model="gpt-4",
            temperature=0.7,
            max_tokens=2000
        )
        
        # Parse JSON response
        try:
            # Extract JSON from response
            json_match = re.search(r'```json\n(.*?)\n```', response["content"], re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response["content"]
            
            # Clean up the JSON string
            json_str = re.sub(r'```.*?```', '', json_str, flags=re.DOTALL)
            
            # Parse JSON
            citation_needs = json.loads(json_str)
            
            return {
                "citation_needs": citation_needs,
                "count": len(citation_needs),
                "content_length": len(content),
                "metadata": {
                    "processing_time": response.get("processing_time", 0),
                    "model": response.get("model", "gpt-4"),
                    "token_usage": response.get("token_usage", 0),
                    "user_id": user_id
                }
            }
        except Exception as e:
            # Return error if JSON parsing fails
            return {
                "error": f"Error parsing citation needs: {str(e)}",
                "raw_content": response["content"],
                "user_id": user_id
            }
    
    async def suggest_sources(
        self, 
        statement: str,
        topic: Optional[str] = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Suggest potential sources for a statement
        
        Args:
            statement: The statement needing citation
            topic: Optional topic context
            user_id: ID of the user making the request
            
        Returns:
            Dictionary with source suggestions
        """
        # Create system prompt for source suggestions
        system_prompt = """
        You are an expert academic citation assistant for the Cercle platform.
        Suggest potential academic sources for the following statement that needs citation.
        
        For each suggested source, provide:
        1. Author(s)
        2. Year of publication
        3. Title of work
        4. Publication venue (journal, book, etc.)
        5. Brief explanation of why this source is relevant
        
        Format your response as a JSON array of objects:
        [
            {
                "authors": ["Author 1", "Author 2"],
                "year": 2023,
                "title": "Title of the work",
                "publication": "Journal/Book/Conference name",
                "relevance": "Brief explanation of why this source is relevant"
            },
            ...
        ]
        
        Suggest 3-5 high-quality academic sources that would be appropriate for citing this statement.
        Focus on recent, peer-reviewed sources when possible, unless historical or foundational works are more appropriate.
        """
        
        if topic:
            system_prompt += f"\n\nThe statement is related to the topic of: {topic}"
        
        # Call OpenAI API
        response = await self.openai_client.generate_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": statement}
            ],
            model="gpt-4",
            temperature=0.7,
            max_tokens=1500
        )
        
        # Parse JSON response
        try:
            # Extract JSON from response
            json_match = re.search(r'```json\n(.*?)\n```', response["content"], re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response["content"]
            
            # Clean up the JSON string
            json_str = re.sub(r'```.*?```', '', json_str, flags=re.DOTALL)
            
            # Parse JSON
            source_suggestions = json.loads(json_str)
            
            return {
                "statement": statement,
                "topic": topic,
                "source_suggestions": source_suggestions,
                "count": len(source_suggestions),
                "metadata": {
                    "processing_time": response.get("processing_time", 0),
                    "model": response.get("model", "gpt-4"),
                    "token_usage": response.get("token_usage", 0),
                    "user_id": user_id
                }
            }
        except Exception as e:
            # Return error if JSON parsing fails
            return {
                "error": f"Error parsing source suggestions: {str(e)}",
                "raw_content": response["content"],
                "user_id": user_id
            }
    
    async def format_citations(
        self, 
        sources: List[Dict[str, Any]],
        style: str = "apa",
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Format citations according to academic styles
        
        Args:
            sources: List of source information to format
            style: Citation style to use (apa, mla, chicago, etc.)
            user_id: ID of the user making the request
            
        Returns:
            Dictionary with formatted citations
        """
        # Check if style is valid
        if style not in self.citation_styles:
            return {
                "error": f"Invalid citation style: {style}",
                "available_styles": list(self.citation_styles.keys()),
                "user_id": user_id
            }
        
        # Create system prompt for citation formatting
        system_prompt = f"""
        You are an expert academic citation formatter for the Cercle platform.
        Format the following sources according to the {self.citation_styles[style]} style.
        
        For each source, provide:
        1. In-text citation format
        2. Reference list/bibliography format
        
        Format your response as a JSON array of objects:
        [
            {{
                "source_id": The index of the source in the input list,
                "in_text_citation": "The formatted in-text citation",
                "reference_entry": "The formatted reference list/bibliography entry"
            }},
            ...
        ]
        
        Follow all formatting rules for {self.citation_styles[style]} precisely, including:
        - Punctuation
        - Italics (indicated with *asterisks*)
        - Author name formatting
        - Date formatting
        - Title capitalization
        - DOI/URL formatting (if applicable)
        """
        
        # Format sources as JSON for the prompt
        sources_json = json.dumps(sources, indent=2)
        
        # Call OpenAI API
        response = await self.openai_client.generate_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": sources_json}
            ],
            model="gpt-4",
            temperature=0.3,  # Lower temperature for more precise formatting
            max_tokens=2000
        )
        
        # Parse JSON response
        try:
            # Extract JSON from response
            json_match = re.search(r'```json\n(.*?)\n```', response["content"], re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response["content"]
            
            # Clean up the JSON string
            json_str = re.sub(r'```.*?```', '', json_str, flags=re.DOTALL)
            
            # Parse JSON
            formatted_citations = json.loads(json_str)
            
            return {
                "style": style,
                "style_name": self.citation_styles[style],
                "formatted_citations": formatted_citations,
                "count": len(formatted_citations),
                "metadata": {
                    "processing_time": response.get("processing_time", 0),
                    "model": response.get("model", "gpt-4"),
                    "token_usage": response.get("token_usage", 0),
                    "user_id": user_id
                }
            }
        except Exception as e:
            # Return error if JSON parsing fails
            return {
                "error": f"Error parsing formatted citations: {str(e)}",
                "raw_content": response["content"],
                "user_id": user_id
            }
    
    async def get_citation_styles(self) -> Dict[str, Any]:
        """
        Get available citation styles
        
        Returns:
            Dictionary with available citation styles
        """
        styles_list = []
        for style_id, style_name in self.citation_styles.items():
            styles_list.append({
                "id": style_id,
                "name": style_name
            })
        
        return {
            "styles": styles_list,
            "count": len(styles_list),
            "default_style": "apa"
        }
