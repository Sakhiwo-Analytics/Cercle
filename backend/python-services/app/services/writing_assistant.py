"""
Writing Assistant service for academic writing feedback and templates
"""
import os
import json
from typing import Dict, Any, List, Optional
from ..utils.openai_client import OpenAIClient

class WritingAssistant:
    """
    Writing Assistant for providing feedback on academic writing,
    implementing templates, and offering live suggestions
    """
    
    def __init__(self):
        """Initialize the Writing Assistant with required components"""
        self.openai_client = OpenAIClient()
        
        # Load academic templates (in production, these would be in a database)
        self.templates = {
            "research_paper": {
                "name": "Research Paper",
                "description": "Standard academic research paper structure",
                "sections": [
                    "Abstract",
                    "Introduction",
                    "Literature Review",
                    "Methodology",
                    "Results",
                    "Discussion",
                    "Conclusion",
                    "References"
                ]
            },
            "thesis": {
                "name": "Thesis",
                "description": "Academic thesis structure",
                "sections": [
                    "Abstract",
                    "Acknowledgments",
                    "Introduction",
                    "Literature Review",
                    "Theoretical Framework",
                    "Methodology",
                    "Results",
                    "Analysis",
                    "Discussion",
                    "Conclusion",
                    "References",
                    "Appendices"
                ]
            },
            "literature_review": {
                "name": "Literature Review",
                "description": "Comprehensive literature review structure",
                "sections": [
                    "Introduction",
                    "Theoretical Background",
                    "Current State of Research",
                    "Research Gaps",
                    "Conclusion",
                    "References"
                ]
            },
            "case_study": {
                "name": "Case Study",
                "description": "Academic case study structure",
                "sections": [
                    "Executive Summary",
                    "Introduction",
                    "Background",
                    "Case Presentation",
                    "Analysis",
                    "Discussion",
                    "Recommendations",
                    "Conclusion",
                    "References"
                ]
            },
            "lab_report": {
                "name": "Lab Report",
                "description": "Scientific lab report structure",
                "sections": [
                    "Title",
                    "Abstract",
                    "Introduction",
                    "Materials and Methods",
                    "Results",
                    "Discussion",
                    "Conclusion",
                    "References"
                ]
            }
        }
    
    async def process_writing(
        self, 
        content: str, 
        template: Optional[str] = None,
        feedback_types: Optional[List[str]] = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Process writing content and provide feedback
        
        Args:
            content: The writing content to analyze
            template: Optional academic template to apply
            feedback_types: Types of feedback to provide
            user_id: ID of the user making the request
            
        Returns:
            Dictionary with writing feedback and suggestions
        """
        if not feedback_types:
            feedback_types = ["grammar", "style", "citations"]
        
        # Apply template if provided
        template_content = None
        if template and template in self.templates:
            template_content = self.templates[template]
        
        # Generate feedback using OpenAI
        feedback = await self._generate_feedback(content, feedback_types, template_content)
        
        # Generate improved version
        improved_version = await self._generate_improved_version(content, feedback, template_content)
        
        # Return results
        return {
            "original": content,
            "suggestions": feedback,
            "improved_version": improved_version,
            "user_id": user_id
        }
    
    async def get_templates(self) -> List[Dict[str, Any]]:
        """
        Get available academic templates
        
        Returns:
            List of available templates with metadata
        """
        template_list = []
        for template_id, template in self.templates.items():
            template_list.append({
                "id": template_id,
                "name": template["name"],
                "description": template["description"],
                "section_count": len(template["sections"])
            })
        
        return template_list
    
    async def _generate_feedback(
        self, 
        content: str, 
        feedback_types: List[str],
        template: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[str]]:
        """
        Generate feedback on writing content
        
        Args:
            content: The writing content to analyze
            feedback_types: Types of feedback to provide
            template: Optional template metadata
            
        Returns:
            Dictionary with feedback categorized by type
        """
        # Create system prompt based on feedback types
        system_prompt = "You are an academic writing assistant for the Cercle platform. "
        system_prompt += "Analyze the following academic writing and provide specific, actionable feedback "
        system_prompt += "in the following categories:\n\n"
        
        if "grammar" in feedback_types:
            system_prompt += "- Grammar: Identify grammatical errors, punctuation issues, and sentence structure problems\n"
        
        if "style" in feedback_types:
            system_prompt += "- Style: Evaluate academic tone, clarity, conciseness, and flow\n"
        
        if "citations" in feedback_types:
            system_prompt += "- Citations: Check citation format, consistency, and completeness\n"
        
        if "structure" in feedback_types:
            system_prompt += "- Structure: Assess overall organization, paragraph structure, and logical flow\n"
        
        if template:
            system_prompt += f"\nThe writing should follow the {template['name']} template with these sections: "
            system_prompt += ", ".join(template["sections"])
        
        system_prompt += "\n\nProvide your feedback as a JSON object with categories as keys and arrays of specific feedback points as values."
        
        # Call OpenAI API
        response = await self.openai_client.generate_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ],
            model="gpt-4",
            temperature=0.7,
            max_tokens=1000
        )
        
        # Parse JSON response
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response["content"], re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response["content"]
            
            # Clean up the JSON string
            json_str = re.sub(r'```.*?```', '', json_str, flags=re.DOTALL)
            
            # Parse JSON
            feedback_data = json.loads(json_str)
            
            # Ensure all requested feedback types are present
            for feedback_type in feedback_types:
                if feedback_type not in feedback_data:
                    feedback_data[feedback_type] = []
            
            return feedback_data
        except Exception as e:
            # Fallback if JSON parsing fails
            feedback_data = {}
            for feedback_type in feedback_types:
                feedback_data[feedback_type] = [f"Error parsing feedback: {str(e)}"]
            
            return feedback_data
    
    async def _generate_improved_version(
        self, 
        content: str, 
        feedback: Dict[str, List[str]],
        template: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate an improved version of the writing content
        
        Args:
            content: The original writing content
            feedback: Feedback on the content
            template: Optional template metadata
            
        Returns:
            Improved version of the content
        """
        # Create system prompt for improvement
        system_prompt = "You are an academic writing assistant for the Cercle platform. "
        system_prompt += "Improve the following academic writing based on this feedback:\n\n"
        
        # Add feedback
        for feedback_type, feedback_points in feedback.items():
            if feedback_points:
                system_prompt += f"{feedback_type.capitalize()} feedback:\n"
                for point in feedback_points:
                    system_prompt += f"- {point}\n"
                system_prompt += "\n"
        
        if template:
            system_prompt += f"\nThe writing should follow the {template['name']} template with these sections: "
            system_prompt += ", ".join(template["sections"])
        
        system_prompt += "\n\nProvide an improved version of the text that addresses all the feedback points. "
        system_prompt += "Maintain the original meaning and content while improving the writing quality."
        
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
        
        return response["content"]
