import pandas as pd
import os
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from app.core.config import settings
from app.services.llm import get_llm_response
from app.db.mongodb import db
import logging

logger = logging.getLogger("gradguide")

class OpenRouterLLM:
    @property
    def _llm_type(self) -> str:
        return "openrouter"
    
    def _call(self, prompt: str, stop: list[str] = None) -> str:
        messages = [{"role": "user", "content": prompt}]
        return get_llm_response(messages)

class RAGService:
    def __init__(self, data_path=None):
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.db_path = "./chroma_db"
        self.vector_store = None
        self.llm = OpenRouterLLM()
        
        if data_path and os.path.exists(data_path):
            self.load_data(data_path)
    
    def load_data(self, data_path):
        df = pd.read_excel(data_path)
        documents = [
            Document(
                page_content=f"Exam: {row['exam']}, College: {row['college']}, Branch: {row['branch']}, Cutoff Rank: {row['cutoff_rank']}",
                metadata={"exam": row["exam"], "college": row["college"], "branch": row["branch"], "cutoff_rank": row["cutoff_rank"]}
            ) for _, row in df.iterrows()
        ]
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_documents(documents)
        self.vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.db_path
        )
    
    def query_rag(self, query, user_exams=None, user_ranks=None):
        if not self.vector_store and os.path.exists(self.db_path):
            self.vector_store = Chroma(persist_directory=self.db_path, embedding_function=self.embeddings)
        
        if not self.vector_store:
            return "Error: No college data loaded."
        
        context = ""
        if user_exams and user_ranks:
            context += "User exam information:\n" + "\n".join([f"- {exam}: Rank {user_ranks[exam]}" for exam in user_exams if exam in user_ranks])
        query = f"{context}\n\nUser query: {query}"
        
        retriever = self.vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})
        docs = retriever.invoke(query)
        context = "\n\n".join([doc.page_content for doc in docs])
        
        prompt = f"""
        You are a college admission assistant for Indian B.Tech programs.
        Answer based on the retrieved information:
        {context}
        
        Question: {query}
        
        Use the retrieved information for eligibility, admission, or cutoff queries. For general questions, provide helpful guidance or state if information is unavailable.
        """
        
        return get_llm_response([
            {"role": "system", "content": "You are a helpful AI assistant for college admissions in India."},
            {"role": "user", "content": prompt}
        ])
    
    def filter_colleges(self, exams, ranks):
        results = []
        try:
            collection = db.db.college_data
            for exam in exams:
                if exam in ranks:
                    rank = ranks[exam]
                    for doc in collection.find({"exam": exam, "cutoff_rank": {"$gte": rank}}):
                        results.append({
                            "exam": doc["exam"],
                            "college": doc["college"],
                            "branch": doc["branch"],
                            "cutoff_rank": doc["cutoff_rank"]
                        })
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            if os.path.exists("./data/college_data.xlsx"):
                df = pd.read_excel("./data/college_data.xlsx")
                for exam in exams:
                    if exam in ranks:
                        rank = ranks[exam]
                        filtered = df[(df["exam"] == exam) & (df["cutoff_rank"] >= rank)]
                        for _, row in filtered.iterrows():
                            results.append({
                                "exam": row["exam"],
                                "college": row["college"],
                                "branch": row["branch"],
                                "cutoff_rank": row["cutoff_rank"]
                            })
        return results