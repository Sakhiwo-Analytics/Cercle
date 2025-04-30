"""
LangChain utilities for AI routing and vector storage
"""
import os
from typing import List, Dict, Any, Optional
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pinecone

class LangChainManager:
    """Manager for LangChain components and utilities"""
    
    def __init__(self):
        """Initialize LangChain components and Pinecone"""
        # Check for required environment variables
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_environment = os.getenv("PINECONE_ENVIRONMENT")
        self.pinecone_index_name = os.getenv("PINECONE_INDEX_NAME", "cercle-vector-index")
        
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        if not self.pinecone_api_key or not self.pinecone_environment:
            raise ValueError("Pinecone configuration not found in environment variables")
        
        # Initialize LangChain components
        self.llm = ChatOpenAI(
            model_name="gpt-4",
            temperature=0.7,
            openai_api_key=self.openai_api_key
        )
        
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002",
            openai_api_key=self.openai_api_key
        )
        
        # Initialize Pinecone
        self._init_pinecone()
    
    def _init_pinecone(self):
        """Initialize Pinecone vector database"""
        pinecone.init(
            api_key=self.pinecone_api_key,
            environment=self.pinecone_environment
        )
        
        # Check if index exists, if not create it
        if self.pinecone_index_name not in pinecone.list_indexes():
            pinecone.create_index(
                name=self.pinecone_index_name,
                dimension=1536,  # OpenAI embeddings dimension
                metric="cosine"
            )
        
        # Connect to the index
        self.index = pinecone.Index(self.pinecone_index_name)
        
        # Create vector store
        self.vector_store = Pinecone(
            index=self.index,
            embedding=self.embeddings,
            text_key="text"
        )
    
    async def select_best_model(self, query: str, task_type: str) -> Dict[str, Any]:
        """
        Select the best AI model for a given query and task type
        
        Args:
            query: The query or content to process
            task_type: Type of task (query, research, writing, etc.)
            
        Returns:
            Dictionary with selected model and reasoning
        """
        # Define prompt template for model selection
        template = """
        You are an AI model selector for the Cercle academic research platform.
        Your job is to select the most appropriate AI model for a given query and task type.
        
        Available models:
        1. OpenAI GPT-4: Best for general knowledge, reasoning, and creative tasks
        2. Anthropic Claude: Best for longer content, nuanced understanding, and ethical considerations
        3. Wolfram Alpha: Best for computational queries, math, science, and factual data
        
        Query: {query}
        Task Type: {task_type}
        
        Based on the query and task type, select the most appropriate model.
        Provide your selection and reasoning in the following format:
        
        Selected Model: [model name]
        Confidence: [confidence score between 0 and 1]
        Reasoning: [brief explanation of your selection]
        """
        
        prompt = PromptTemplate(
            input_variables=["query", "task_type"],
            template=template
        )
        
        # Create chain
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        # Run chain
        result = await chain.arun(query=query, task_type=task_type)
        
        # Parse result
        lines = result.strip().split("\n")
        selected_model = lines[0].replace("Selected Model:", "").strip()
        confidence = float(lines[1].replace("Confidence:", "").strip())
        reasoning = lines[2].replace("Reasoning:", "").strip()
        
        return {
            "selected_model": selected_model,
            "confidence": confidence,
            "reasoning": reasoning
        }
    
    async def store_document(self, text: str, metadata: Dict[str, Any]) -> List[str]:
        """
        Store a document in the vector database
        
        Args:
            text: The document text to store
            metadata: Metadata to associate with the document
            
        Returns:
            List of IDs for the stored document chunks
        """
        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_text(text)
        
        # Create metadata for each chunk
        metadatas = [metadata for _ in chunks]
        
        # Add to vector store
        ids = self.vector_store.add_texts(
            texts=chunks,
            metadatas=metadatas
        )
        
        return ids
    
    async def search_similar_documents(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents in the vector database
        
        Args:
            query: The query to search for
            k: Number of results to return
            
        Returns:
            List of similar documents with scores
        """
        # Generate embedding for query
        results = self.vector_store.similarity_search_with_score(
            query=query,
            k=k
        )
        
        # Format results
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": score
            })
        
        return formatted_results
