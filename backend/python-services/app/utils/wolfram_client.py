"""
Wolfram Alpha API client utilities
"""
import os
import wolframalpha
from typing import List, Dict, Any, Optional

class WolframClient:
    """Client for interacting with Wolfram Alpha API"""
    
    def __init__(self):
        """Initialize the Wolfram Alpha client with API key from environment variables"""
        self.app_id = os.getenv("WOLFRAM_APP_ID")
        if not self.app_id:
            raise ValueError("Wolfram Alpha App ID not found in environment variables")
        
        self.client = wolframalpha.Client(self.app_id)
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a query using Wolfram Alpha API
        
        Args:
            query: The query string to process
            
        Returns:
            Dictionary with response content and metadata
        """
        try:
            # Call Wolfram Alpha API
            result = self.client.query(query)
            
            # Process results
            pods = []
            for pod in result.pods:
                pod_data = {
                    "title": pod.title,
                    "subpods": []
                }
                
                for subpod in pod.subpods:
                    subpod_data = {
                        "plaintext": subpod.plaintext,
                        "img": subpod.img.src if hasattr(subpod, 'img') else None
                    }
                    pod_data["subpods"].append(subpod_data)
                
                pods.append(pod_data)
            
            # Check if result has an answer
            has_answer = hasattr(result, 'results') and len(result.results) > 0
            
            # Extract simple text answer if available
            simple_answer = None
            if hasattr(result, 'results'):
                for pod in result.pods:
                    if pod.title in ['Result', 'Results', 'Solution', 'Solutions', 'Value']:
                        for subpod in pod.subpods:
                            if hasattr(subpod, 'plaintext') and subpod.plaintext:
                                simple_answer = subpod.plaintext
                                break
                        if simple_answer:
                            break
            
            # Format response
            response = {
                "query": query,
                "success": has_answer,
                "pods": pods,
                "simple_answer": simple_answer,
                "model": "wolfram-alpha",
                "processing_time": 0.5  # Placeholder value
            }
            
            return response
        except Exception as e:
            raise Exception(f"Error calling Wolfram Alpha API: {str(e)}")
    
    def is_computational_query(self, query: str) -> bool:
        """
        Determine if a query is likely to be computational and suitable for Wolfram Alpha
        
        Args:
            query: The query string to analyze
            
        Returns:
            Boolean indicating if the query is computational
        """
        # List of keywords that suggest a computational query
        computational_keywords = [
            "calculate", "compute", "solve", "equation", "formula", "graph", 
            "plot", "integral", "derivative", "math", "physics", "chemistry",
            "=", "+", "-", "*", "/", "^", "sqrt", "sin", "cos", "tan", "log",
            "exponential", "factorial", "prime", "convert", "units"
        ]
        
        # Check if any computational keywords are in the query
        query_lower = query.lower()
        for keyword in computational_keywords:
            if keyword in query_lower:
                return True
        
        return False
