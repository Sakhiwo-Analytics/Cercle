"""
Research Amplifier service for enhancing academic research
"""
import os
import uuid
from typing import Dict, Any, List, Optional
from fastapi import UploadFile
from ..utils.openai_client import OpenAIClient
from ..utils.langchain_utils import LangChainManager
from ..utils.pdf_processor import PDFProcessor

class ResearchAmplifier:
    """
    Research Amplifier for enhancing academic research with AI-powered analysis,
    PDF processing, and semantic source mapping
    """
    
    def __init__(self):
        """Initialize the Research Amplifier with required components"""
        self.openai_client = OpenAIClient()
        self.langchain_manager = LangChainManager()
        self.pdf_processor = PDFProcessor()
        
        # In-memory document store (in production, this would be a database)
        self.documents = {}
    
    async def process_research(
        self, 
        topic: str, 
        sources: Optional[List[str]] = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Process a research topic and provide enhanced insights
        
        Args:
            topic: The research topic to amplify
            sources: Optional list of source document IDs to include
            user_id: ID of the user making the request
            
        Returns:
            Dictionary with research results
        """
        # Gather source content if provided
        source_content = ""
        if sources:
            for doc_id in sources:
                if doc_id in self.documents:
                    source_content += f"\nDocument: {self.documents[doc_id]['filename']}\n"
                    source_content += self.documents[doc_id]['content'] + "\n\n"
        
        # Generate research insights using OpenAI
        prompt = self._create_research_prompt(topic, source_content)
        
        response = await self.openai_client.generate_completion(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Research Topic: {topic}"}
            ],
            model="gpt-4",
            temperature=0.7,
            max_tokens=2000
        )
        
        # Parse the response to extract structured information
        parsed_result = await self._parse_research_response(response["content"])
        
        # Add source documents to result if provided
        if sources:
            parsed_result["source_documents"] = sources
        
        # Add user ID to result
        parsed_result["user_id"] = user_id
        parsed_result["topic"] = topic
        
        return parsed_result
    
    async def process_pdf(self, file: UploadFile, user_id: str) -> Dict[str, Any]:
        """
        Process a PDF file and extract its content for research
        
        Args:
            file: The uploaded PDF file
            user_id: ID of the user who uploaded the file
            
        Returns:
            Dictionary with document metadata and summary
        """
        # Process the PDF file
        result = await self.pdf_processor.process_pdf(file, user_id)
        
        # Store the document in memory (in production, this would be in a database)
        self.documents[result["document_id"]] = {
            "filename": result["filename"],
            "content": "Document content would be stored here",  # Placeholder
            "summary": result["summary"],
            "user_id": user_id
        }
        
        # Store document in vector database for semantic search
        # In a real implementation, you would store the actual content
        await self.langchain_manager.store_document(
            text=result["summary"],
            metadata={
                "document_id": result["document_id"],
                "filename": result["filename"],
                "user_id": user_id
            }
        )
        
        return result
    
    async def analyze_document(
        self, 
        document_id: str, 
        analysis_type: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Analyze a document based on its ID and analysis type
        
        Args:
            document_id: ID of the document to analyze
            analysis_type: Type of analysis to perform
            user_id: ID of the user requesting the analysis
            
        Returns:
            Dictionary with analysis results
        """
        # Check if document exists
        if document_id not in self.documents:
            raise ValueError(f"Document with ID {document_id} not found")
        
        # Get document content
        document = self.documents[document_id]
        
        # In a real implementation, you would retrieve the actual content
        # For this example, we'll use the summary as a placeholder
        document_content = document["summary"]
        
        # Analyze the document
        result = await self.pdf_processor.analyze_document(
            document_id=document_id,
            analysis_type=analysis_type,
            text_content=document_content
        )
        
        # Add user ID to result
        result["user_id"] = user_id
        
        return result
    
    def _create_research_prompt(self, topic: str, source_content: str = "") -> str:
        """
        Create a system prompt for research amplification
        
        Args:
            topic: The research topic
            source_content: Optional source document content
            
        Returns:
            System prompt for OpenAI
        """
        prompt = """
        You are an advanced academic research assistant for the Cercle platform.
        Your task is to amplify research on a given topic by providing:
        
        1. Research Directions: Suggest 3-5 promising research directions or angles to explore
        2. Related Topics: Identify 3-5 related topics that could provide valuable context
        3. Key Papers: Recommend 3-5 important academic papers or sources on this topic
        4. Methodology Suggestions: Recommend 1-3 research methodologies appropriate for this topic
        5. Research Gaps: Identify 1-3 potential gaps in the current research landscape
        
        Format your response using clear headings for each section.
        Be specific, scholarly, and focus on academic value.
        Cite sources properly with author, year, and title.
        """
        
        if source_content:
            prompt += """
            
            Use the following source documents to inform your recommendations:
            
            """
            prompt += source_content
        
        return prompt
    
    async def _parse_research_response(self, content: str) -> Dict[str, Any]:
        """
        Parse the research response into structured data
        
        Args:
            content: The raw response content
            
        Returns:
            Structured research data
        """
        # This is a simplified implementation - in production, you would use more robust parsing
        import re
        
        # Extract research directions
        research_directions = []
        directions_match = re.search(r"Research Directions:(.*?)(?=Related Topics:|$)", content, re.DOTALL)
        if directions_match:
            directions_text = directions_match.group(1).strip()
            # Extract numbered or bulleted items
            directions = re.findall(r"(?:^|\n)(?:\d+\.|\*|\-)\s*(.*?)(?=(?:\n(?:\d+\.|\*|\-))|$)", directions_text, re.DOTALL)
            research_directions = [direction.strip() for direction in directions if direction.strip()]
        
        # Extract related topics
        related_topics = []
        topics_match = re.search(r"Related Topics:(.*?)(?=Key Papers:|$)", content, re.DOTALL)
        if topics_match:
            topics_text = topics_match.group(1).strip()
            topics = re.findall(r"(?:^|\n)(?:\d+\.|\*|\-)\s*(.*?)(?=(?:\n(?:\d+\.|\*|\-))|$)", topics_text, re.DOTALL)
            related_topics = [topic.strip() for topic in topics if topic.strip()]
        
        # Extract key papers
        key_papers = []
        papers_match = re.search(r"Key Papers:(.*?)(?=Methodology Suggestions:|$)", content, re.DOTALL)
        if papers_match:
            papers_text = papers_match.group(1).strip()
            papers = re.findall(r"(?:^|\n)(?:\d+\.|\*|\-)\s*(.*?)(?=(?:\n(?:\d+\.|\*|\-))|$)", papers_text, re.DOTALL)
            
            for paper in papers:
                if not paper.strip():
                    continue
                
                # Try to extract author and year
                author_year_match = re.search(r"(.*?)\((\d{4})\)(.*)", paper)
                if author_year_match:
                    authors_text = author_year_match.group(1).strip()
                    year = int(author_year_match.group(2))
                    title = author_year_match.group(3).strip(". ")
                    
                    # Split authors
                    authors = [author.strip() for author in authors_text.split(",") if author.strip()]
                else:
                    title = paper
                    year = 0
                    authors = ["Unknown"]
                
                key_papers.append({
                    "title": title,
                    "authors": authors,
                    "year": year,
                    "relevance": 0.9  # Placeholder
                })
        
        # Extract methodology suggestions
        methodology_suggestions = []
        methodology_match = re.search(r"Methodology Suggestions:(.*?)(?=Research Gaps:|$)", content, re.DOTALL)
        if methodology_match:
            methodology_text = methodology_match.group(1).strip()
            methodologies = re.findall(r"(?:^|\n)(?:\d+\.|\*|\-)\s*(.*?)(?=(?:\n(?:\d+\.|\*|\-))|$)", methodology_text, re.DOTALL)
            methodology_suggestions = [method.strip() for method in methodologies if method.strip()]
        
        # Extract research gaps
        research_gaps = []
        gaps_match = re.search(r"Research Gaps:(.*?)(?=$)", content, re.DOTALL)
        if gaps_match:
            gaps_text = gaps_match.group(1).strip()
            gaps = re.findall(r"(?:^|\n)(?:\d+\.|\*|\-)\s*(.*?)(?=(?:\n(?:\d+\.|\*|\-))|$)", gaps_text, re.DOTALL)
            research_gaps = [gap.strip() for gap in gaps if gap.strip()]
        
        # Return structured data
        return {
            "suggestions": research_directions,
            "related_topics": related_topics,
            "key_papers": key_papers,
            "methodology_suggestions": methodology_suggestions,
            "research_gaps": research_gaps
        }
