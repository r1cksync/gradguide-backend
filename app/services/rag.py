import pandas as pd
import os
from pinecone import Pinecone, ServerlessSpec
from app.services.llm import get_llm_response
from app.db.mongodb import db
import logging
import re
from typing import List, Dict, Optional
from langchain_huggingface import HuggingFaceEmbeddings

logger = logging.getLogger("gradguide")

class LocalLLM:
    @property
    def _llm_type(self) -> str:
        return "grok"

    async def _call(self, prompt: str, stop: List[str] = None) -> str:
        messages = [{"role": "user", "content": prompt}]
        response = await get_llm_response(messages)
        if not response.strip():
            logger.warning("LLM returned empty response")
            return ""
        return response

class RAGService:
    def __init__(self, data_path: Optional[str] = None):
        try:
            self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/multi-qa-MiniLM-L6-cos-v1")
            self.llm = LocalLLM()
            self.pc = Pinecone(api_key="pcsk_7KnaTi_ya3Lm3yWta4SYHExvYKrHhBSNuVwvsGHRUAXM5MDrLTSfBcyGM2B1K61oD6Mh8")
            self.index_name = "gradguide-colleges"
            self.index = None
            logger.info("Initialized RAGService")

            if self.index_name not in self.pc.list_indexes().names():
                self.pc.create_index(
                    name=self.index_name,
                    dimension=384,  # Dimension of multi-qa-MiniLM-L6-cos-v1
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1")
                )
            self.index = self.pc.Index(self.index_name)

            if data_path and os.path.exists(data_path):
                self.load_data(data_path)
        except Exception as e:
            logger.error(f"RAGService init error: {e}")
            raise

    def load_data(self, data_path: str):
        try:
            df = pd.read_excel(data_path)
            required_columns = [
                "exam",
                "college",
                "branch",
                "cutoff_rank",
                "average_placement",
                "median_placement",
                "highest_placement",
            ]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing columns in XLSX: {missing_columns}")

            df["average_placement"] = df["average_placement"].astype(int)
            df["median_placement"] = df["median_placement"].astype(int)
            df["highest_placement"] = df["highest_placement"].astype(int)
            df["cutoff_rank"] = df["cutoff_rank"].astype(int)

            # Load into MongoDB
            collection = db.db.college_data
            collection.delete_many({})
            collection.insert_many(df.to_dict("records"))
            logger.info(f"Loaded {len(df)} documents into MongoDB")

            # Load into Pinecone
            vectors = []
            for i, row in df.iterrows():
                text = f"{row['exam']} | {row['college']} | {row['branch']} | Cutoff: {row['cutoff_rank']} | Avg Placement: {row['average_placement']} LPA"
                embedding = self.embeddings.embed_query(text)
                vectors.append({
                    "id": str(i),
                    "values": embedding,
                    "metadata": {
                        "exam": row["exam"],
                        "college": row["college"],
                        "branch": row["branch"],
                        "cutoff_rank": row["cutoff_rank"],
                        "average_placement": row["average_placement"],
                        "median_placement": row["median_placement"],
                        "highest_placement": row["highest_placement"],
                    }
                })
            self.index.upsert(vectors=vectors)
            logger.info(f"Loaded {len(vectors)} vectors into Pinecone")
        except Exception as e:
            logger.error(f"Load data error: {e}")
            raise

    async def query_rag(
        self,
        query: str,
        user_exams: Optional[List[str]] = None,
        user_ranks: Optional[Dict[str, int]] = None,
        user_id: Optional[str] = None,
    ) -> str:
        try:
            # Parse exam and rank from query
            if not user_exams or not user_ranks:
                user_exams = []
                user_ranks = {}
                query_lower = query.lower().strip()
                logger.info(f"Query lower: {query_lower}")
                exam_map = {
                    "jee main": "JEE Main",
                    "jee mains": "JEE Main",
                    "jee advanced": "JEE Advanced",
                    "wbjee": "WBJEE",
                    "viteee": "VITEEE",
                    "bitsat": "BITSAT",
                }
                for key, exam in exam_map.items():
                    if key in query_lower:
                        match = re.search(r'rank\D*(\d+)', query_lower, re.IGNORECASE)
                        if match:
                            rank = int(match.group(1))
                            user_exams.append(exam)
                            user_ranks[exam] = rank
                            logger.info(f"Parsed exam: {exam}, rank: {rank}")
                            break
                        else:
                            logger.info("No rank found in query")

            # Pinecone vector search
            query_embedding = self.embeddings.embed_query(query)
            pinecone_results = self.index.query(vector=query_embedding, top_k=50, include_metadata=True)
            docs = pinecone_results["matches"]
            context = "\n".join([
                f"{doc['metadata']['exam']} | {doc['metadata']['college']} | {doc['metadata']['branch']} | "
                f"Cutoff: {doc['metadata']['cutoff_rank']} | Avg Placement: {doc['metadata']['average_placement']} LPA"
                for doc in docs
            ])
            logger.info(f"Retrieved {len(docs)} documents from Pinecone")
            logger.info(f"Pinecone context: {context}")

            # MongoDB filtering for rank-based accuracy
            mongo_results = []
            if user_exams and user_ranks:
                mongo_results = self.filter_colleges(user_exams, user_ranks)
                logger.info(f"Filtered {len(mongo_results)} colleges from MongoDB")
                if mongo_results and not context:
                    context = "\n".join([
                        f"{entry['exam']} | {entry['college']} | {entry['branch']} | "
                        f"Cutoff: {entry['cutoff_rank']} | Avg Placement: {entry['average_placement']} LPA"
                        for entry in mongo_results
                    ])
                    logger.info(f"MongoDB context: {context}")

            if not context:
                logger.info("No relevant data found")
                return "No colleges available for your query."

            prompt = f"""
            You are a college admission assistant for Indian B.Tech programs.
            Use the following data to answer the query accurately and intelligently:
            {context}

            Question: {query}

            Instructions:
            - Interpret the query flexibly and provide a complete, relevant response based on the data.
            - If the query specifies a rank and exam (e.g., JEE Main rank 200), recommend colleges and branches where the rank is better than or equal to the cutoff rank, sorted by average placement.
            - Handle requests for multiple colleges (e.g., 'best and second best') by ranking colleges based on average placement.
            - For general queries, provide relevant information from the data.
            - Format the response clearly, using integer values for placements (e.g., 20 LPA).
            - If no colleges match the criteria, state: "No colleges available for your query."
            - Be concise but thorough, addressing all parts of the query.
            """

            response = await self.llm._call(prompt)
            if not response:
                logger.warning("LLM returned empty response, using fallback")
                if mongo_results:
                    sorted_results = sorted(mongo_results, key=lambda x: x["average_placement"], reverse=True)
                    response_lines = []
                    for i, entry in enumerate(sorted_results[:2], 1):  # Top 2 for 'best and second best'
                        response_lines.append(
                            f"{'Best' if i == 1 else 'Second best'} college: "
                            f"{entry['college']} - {entry['branch']} with an average placement of {entry['average_placement']} LPA."
                        )
                    return "\n".join(response_lines)
                return "No colleges available for your query."
            logger.info(f"LLM response: {response}")
            return response
        except Exception as e:
            logger.error(f"Query error: {e}")
            return "Error: Failed to process query."

    def filter_colleges(
        self,
        exams: List[str],
        ranks: Dict[str, int],
        min_average_placement: Optional[int] = None,
        min_median_placement: Optional[int] = None,
        min_highest_placement: Optional[int] = None,
    ) -> List[dict]:
        try:
            results = []
            collection = db.db.college_data
            query = {"exam": {"$in": exams}}
            for exam, rank in ranks.items():
                query["cutoff_rank"] = {"$gte": rank}
            if min_average_placement is not None:
                query["average_placement"] = {"$gte": min_average_placement}
            if min_median_placement is not None:
                query["median_placement"] = {"$gte": min_median_placement}
            if min_highest_placement is not None:
                query["highest_placement"] = {"$gte": min_highest_placement}

            logger.info(f"MongoDB query: {query}")
            for doc in collection.find(query, {"_id": 0}):
                results.append({
                    "exam": doc["exam"],
                    "college": doc["college"],
                    "branch": doc["branch"],
                    "cutoff_rank": doc.get("cutoff_rank"),
                    "average_placement": doc.get("average_placement"),
                    "median_placement": doc.get("median_placement"),
                    "highest_placement": doc.get("highest_placement"),
                })
            logger.info(f"Filtered {len(results)} colleges from MongoDB")

            if not results and os.path.exists("./data/college_data.xlsx"):
                df = pd.read_excel("./data/college_data.xlsx")
                df["average_placement"] = df["average_placement"].astype(int)
                df["median_placement"] = df["median_placement"].astype(int)
                df["highest_placement"] = df["highest_placement"].astype(int)
                df["cutoff_rank"] = df["cutoff_rank"].astype(int)
                filtered = df[df["exam"].isin(exams)]
                for exam, rank in ranks.items():
                    filtered = filtered[filtered["cutoff_rank"] >= rank]
                if min_average_placement is not None:
                    filtered = filtered[filtered["average_placement"] >= min_average_placement]
                if min_median_placement is not None:
                    filtered = filtered[filtered["median_placement"] >= min_median_placement]
                if min_highest_placement is not None:
                    filtered = filtered[filtered["highest_placement"] >= min_highest_placement]
                results = [
                    {
                        "exam": row["exam"],
                        "college": row["college"],
                        "branch": row["branch"],
                        "cutoff_rank": row["cutoff_rank"],
                        "average_placement": row["average_placement"],
                        "median_placement": row["median_placement"],
                        "highest_placement": row["highest_placement"],
                    }
                    for _, row in filtered.iterrows()
                ]
                logger.info(f"Fallback: Filtered {len(results)} colleges from Excel")
            return results
        except Exception as e:
            logger.error(f"Filter colleges error: {e}")
            return []