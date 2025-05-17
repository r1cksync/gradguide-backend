import pandas as pd
import os
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from app.core.config import settings
from app.services.llm import get_llm_response
from app.db.mongodb import db

# Custom LLM class for OpenRouter integration
from langchain.llms.base import LLM
from typing import Any, List, Mapping, Optional

class OpenRouterLLM(LLM):
    """Custom LLM class for OpenRouter API"""
    
    @property
    def _llm_type(self) -> str:
        return "openrouter"
    
    async def _acall(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        messages = [{"role": "user", "content": prompt}]
        return await get_llm_response(messages)
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        # Synchronous wrapper for _acall
        import asyncio
        return asyncio.run(self._acall(prompt, stop))

class RAGService:
    def __init__(self, data_path=None):
        """Initialize RAG service"""
        self.embeddings = OpenAIEmbeddings(
            api_key=settings.OPENROUTER_API_KEY,
            api_base="https://openrouter.ai/api/v1"
        )
        self.db_path = "./chroma_db"
        self.vector_store = None
        self.llm = OpenRouterLLM()
        
        # Load data if path is provided
        if data_path and os.path.exists(data_path):
            self.load_data(data_path)
    
    def load_data(self, data_path):
        """Load college data from Excel file and create vector store"""
        df = pd.read_excel(data_path)
        
        # Convert DataFrame to documents
        documents = []
        for _, row in df.iterrows():
            content = f"Exam: {row['exam']}, College: {row['college']}, Branch: {row['branch']}, Cutoff Rank: {row['cutoff_rank']}"
            metadata = {
                "exam": row["exam"],
                "college": row["college"],
                "branch": row["branch"],
                "cutoff_rank": row["cutoff_rank"]
            }
            documents.append(Document(page_content=content, metadata=metadata))
        
        # Create text splitter and split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        chunks = text_splitter.split_documents(documents)
        
        # Create vector store
        self.vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.db_path
        )
    
    async def query_rag(self, query, user_exams=None, user_ranks=None):
        """Query the RAG system with user question and context"""
        # If we have user exam information, add it to the query
        if user_exams and user_ranks:
            context = "User exam information:\n"
            for exam in user_exams:
                if exam in user_ranks:
                    context += f"- {exam}: Rank {user_ranks[exam]}\n"
            query = f"{context}\n\nUser query: {query}"
        
        # Create retriever
        if not self.vector_store:
            # Try to load from disk if it exists
            if os.path.exists(self.db_path):
                self.vector_store = Chroma(
                    persist_directory=self.db_path,
                    embedding_function=self.embeddings
                )
            else:
                return "Error: No college data loaded. Please load data first."
        
        retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
        
        # Get relevant documents
        docs = retriever.get_relevant_documents(query)
        
        # Format context from documents
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Prepare prompt for the LLM
        prompt = f"""
        You are a college admission assistant for Indian B.Tech programs. 
        Answer the question based on the retrieved information.
        
        Retrieved Information:
        {context}
        
        Question: {query}
        
        If the question is about college eligibility, admission, or cutoffs, use the retrieved information.
        If the retrieved information doesn't contain relevant details for the query, explain that you don't have that specific information.
        For general questions about college features, placements, or other aspects not covered in the retrieved information, provide helpful general guidance.
        Always be honest about what you know and don't know.
        
        Answer:
        """
        
        # Get response from LLM
        response = await get_llm_response([
            {"role": "system", "content": "You are a helpful AI assistant for college admissions in India."},
            {"role": "user", "content": prompt}
        ])
        
        return response
    
    async def filter_colleges(self, exams, ranks):
        """Filter colleges based on exams and ranks"""
        results = []
        collection = db.db.college_data
        
        for exam in exams:
            if exam in ranks:
                rank = ranks[exam]
                # Find colleges where cutoff rank is greater than or equal to user's rank
                # (lower rank number is better in competitive exams)
                query = {"exam": exam, "cutoff_rank": {"$gte": rank}}
                cursor = collection.find(query)
                
                async for doc in cursor:
                    results.append({
                        "exam": doc["exam"],
                        "college": doc["college"],
                        "branch": doc["branch"],
                        "cutoff_rank": doc["cutoff_rank"]
                    })
        
        return results