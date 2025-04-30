"""
AI Notebook / Auto-Notes service for converting text into structured notes
"""
import os
import json
import re
from typing import Dict, Any, List, Optional
from ..utils.openai_client import OpenAIClient

class AutoNotesGenerator:
    """
    Auto-Notes Generator for converting unstructured text or lecture content
    into organized, structured notes and mind maps
    """
    
    def __init__(self):
        """Initialize the Auto-Notes Generator with required components"""
        self.openai_client = OpenAIClient()
    
    async def generate_structured_notes(
        self, 
        content: str, 
        format_type: str = "outline",
        subject: Optional[str] = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Generate structured notes from unstructured text
        
        Args:
            content: The unstructured text to convert
            format_type: Type of notes format (outline, cornell, mindmap, flashcards)
            subject: Optional subject area for context
            user_id: ID of the user making the request
            
        Returns:
            Dictionary with structured notes
        """
        # Create system prompt based on the requested format
        system_prompt = self._create_notes_prompt(format_type, subject)
        
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
        
        # Process the response based on format type
        processed_notes = self._process_notes_response(response["content"], format_type)
        
        return {
            "original_content": content[:500] + "..." if len(content) > 500 else content,  # Truncate for response
            "notes": processed_notes,
            "format_type": format_type,
            "subject": subject,
            "metadata": {
                "processing_time": response.get("processing_time", 0),
                "model": response.get("model", "gpt-4"),
                "token_usage": response.get("token_usage", 0),
                "user_id": user_id
            }
        }
    
    async def generate_mind_map(
        self, 
        content: str,
        central_topic: Optional[str] = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Generate a mind map structure from content
        
        Args:
            content: The content to convert to a mind map
            central_topic: Optional central topic for the mind map
            user_id: ID of the user making the request
            
        Returns:
            Dictionary with mind map structure
        """
        # Create system prompt for mind map generation
        system_prompt = """
        You are an expert academic mind map creator for the Cercle platform.
        Convert the following content into a hierarchical mind map structure.
        
        The mind map should:
        1. Have a clear central topic
        2. Include main branches (key concepts)
        3. Include sub-branches (supporting details)
        4. Be organized logically with relationships between concepts
        5. Include brief descriptions for each node
        
        Format your response as a JSON object with the following structure:
        {
            "central_topic": {
                "title": "Main Topic",
                "description": "Brief description",
                "branches": [
                    {
                        "title": "Branch 1",
                        "description": "Description of branch 1",
                        "sub_branches": [
                            {
                                "title": "Sub-branch 1.1",
                                "description": "Description of sub-branch 1.1"
                            },
                            ...
                        ]
                    },
                    ...
                ]
            }
        }
        """
        
        if central_topic:
            system_prompt += f"\n\nUse '{central_topic}' as the central topic of the mind map."
        
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
            mind_map = json.loads(json_str)
            
            return {
                "mind_map": mind_map,
                "original_content": content[:500] + "..." if len(content) > 500 else content,  # Truncate for response
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
                "error": f"Error parsing mind map: {str(e)}",
                "raw_content": response["content"],
                "user_id": user_id
            }
    
    async def generate_flashcards(
        self, 
        content: str,
        difficulty: str = "medium",
        count: int = 10,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Generate study flashcards from content
        
        Args:
            content: The content to convert to flashcards
            difficulty: Difficulty level (easy, medium, hard)
            count: Number of flashcards to generate
            user_id: ID of the user making the request
            
        Returns:
            Dictionary with flashcards
        """
        # Create system prompt for flashcard generation
        system_prompt = f"""
        You are an expert academic flashcard creator for the Cercle platform.
        Create {count} study flashcards based on the following content.
        
        The flashcards should be at {difficulty} difficulty level.
        
        Format your response as a JSON array of flashcard objects:
        [
            {{
                "question": "Front side of flashcard with question",
                "answer": "Back side of flashcard with answer",
                "tags": ["tag1", "tag2"]
            }},
            ...
        ]
        
        Make sure the questions test understanding, not just memorization.
        Include a variety of question types (definition, application, analysis, etc.).
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
            flashcards = json.loads(json_str)
            
            return {
                "flashcards": flashcards,
                "count": len(flashcards),
                "difficulty": difficulty,
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
                "error": f"Error parsing flashcards: {str(e)}",
                "raw_content": response["content"],
                "user_id": user_id
            }
    
    def _create_notes_prompt(self, format_type: str, subject: Optional[str] = None) -> str:
        """
        Create a system prompt for notes generation
        
        Args:
            format_type: Type of notes format
            subject: Optional subject area
            
        Returns:
            System prompt for OpenAI
        """
        base_prompt = """
        You are an expert academic note-taking assistant for the Cercle platform.
        Convert the following unstructured content into well-organized, structured notes.
        """
        
        if subject:
            base_prompt += f"\n\nThe content is related to the subject of {subject}."
        
        if format_type == "outline":
            base_prompt += """
            
            Format the notes as a hierarchical outline with:
            - Main topics (I, II, III, etc.)
              - Subtopics (A, B, C, etc.)
                - Details (1, 2, 3, etc.)
                  - Supporting points (a, b, c, etc.)
            
            Use clear, concise language and maintain academic rigor.
            Highlight key terms, concepts, and definitions.
            Include all important information from the original content.
            """
        elif format_type == "cornell":
            base_prompt += """
            
            Format the notes using the Cornell Notes system with:
            1. Cues/Questions (left column)
            2. Notes (right column)
            3. Summary (bottom)
            
            For each major section or concept, create appropriate cues or questions in the left column.
            In the right column, provide detailed notes that answer the cues/questions.
            At the bottom, provide a concise summary of the entire content.
            """
        elif format_type == "summary":
            base_prompt += """
            
            Create a comprehensive summary of the content that:
            1. Captures all key points and arguments
            2. Is well-structured with clear paragraphs
            3. Uses academic language
            4. Maintains the logical flow of the original content
            5. Highlights important concepts, theories, or findings
            
            The summary should be thorough yet concise, focusing on the most important information.
            """
        else:  # Default to standard notes
            base_prompt += """
            
            Format the notes in a clear, structured manner with:
            - Headings for main topics
            - Subheadings for subtopics
            - Bullet points for key details
            - Numbered lists for sequential information
            
            Use clear, concise language and maintain academic rigor.
            Highlight key terms, concepts, and definitions.
            Include all important information from the original content.
            """
        
        return base_prompt
    
    def _process_notes_response(self, content: str, format_type: str) -> Dict[str, Any]:
        """
        Process the notes response based on format type
        
        Args:
            content: The raw response content
            format_type: Type of notes format
            
        Returns:
            Processed notes structure
        """
        if format_type == "cornell":
            # Parse Cornell notes format
            # Extract sections
            sections = []
            current_cue = None
            current_notes = []
            summary = ""
            
            # Look for Cornell format patterns
            cornell_pattern = r"Cue/Question:\s*(.*?)\s*Notes:\s*(.*?)(?=Cue/Question:|Summary:|$)"
            summary_pattern = r"Summary:\s*(.*?)$"
            
            # Extract Cornell sections
            matches = re.findall(cornell_pattern, content, re.DOTALL)
            for cue, notes in matches:
                sections.append({
                    "cue": cue.strip(),
                    "notes": notes.strip()
                })
            
            # Extract summary
            summary_match = re.search(summary_pattern, content, re.DOTALL)
            if summary_match:
                summary = summary_match.group(1).strip()
            
            return {
                "format": "cornell",
                "sections": sections,
                "summary": summary,
                "raw_content": content
            }
        else:
            # For other formats, return the content as is
            return {
                "format": format_type,
                "content": content
            }
