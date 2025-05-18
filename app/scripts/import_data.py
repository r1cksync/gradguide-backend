# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# import pandas as pd
# from pymongo import MongoClient
# from pinecone import Pinecone, ServerlessSpec
# from langchain_huggingface import HuggingFaceEmbeddings
# import logging

# MONGODB_URI = "mongodb+srv://sagnik23102:j9TildStvOeklXmg@gradguide.zdinpa4.mongodb.net/?retryWrites=true&w=majority&appName=gradguide"
# PINECONE_API_KEY = "pcsk_7KnaTi_ya3Lm3yWta4SYHExvYKrHhBSNuVwvsGHRUAXM5MDrLTSfBcyGM2B1K61oD6Mh8"

# logger = logging.getLogger("gradguide")
# logging.basicConfig(level=logging.INFO)

# def import_college_data(xlsx_path: str):
#     try:
#         df = pd.read_excel(xlsx_path)
#         logger.info(f"Read {len(df)} records from {xlsx_path}")

#         required_columns = [
#             "exam",
#             "college",
#             "branch",
#             "cutoff_rank",
#             "average_placement",
#             "median_placement",
#             "highest_placement",
#         ]
#         missing_columns = [col for col in required_columns if col not in df.columns]
#         if missing_columns:
#             raise ValueError(f"Missing columns in XLSX: {missing_columns}")

#         df["average_placement"] = df["average_placement"].astype(int)
#         df["median_placement"] = df["median_placement"].astype(int)
#         df["highest_placement"] = df["highest_placement"].astype(int)
#         df["cutoff_rank"] = df["cutoff_rank"].astype(int)

#         # Load into MongoDB
#         client = MongoClient(MONGODB_URI)
#         db = client.get_database("gradguide")
#         collection = db["college_data"]
#         collection.delete_many({})
#         collection.insert_many(df.to_dict("records"))
#         logger.info(f"Inserted {len(df)} records into 'college_data' collection")

#         # Load into Pinecone
#         pc = Pinecone(api_key=PINECONE_API_KEY)
#         index_name = "gradguide-colleges"
#         if index_name not in pc.list_indexes().names():
#             pc.create_index(
#                 name=index_name,
#                 dimension=384,
#                 metric="cosine",
#                 spec=ServerlessSpec(cloud="aws", region="us-east-1")
#             )
#         index = pc.Index(index_name)
#         embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/multi-qa-MiniLM-L6-cos-v1")
#         vectors = []
#         for i, row in df.iterrows():
#             text = f"{row['exam']} | {row['college']} | {row['branch']} | Cutoff: {row['cutoff_rank']} | Avg Placement: {row['average_placement']} LPA"
#             embedding = embeddings.embed_query(text)
#             vectors.append({
#                 "id": str(i),
#                 "values": embedding,
#                 "metadata": {
#                     "exam": row["exam"],
#                     "college": row["college"],
#                     "branch": row["branch"],
#                     "cutoff_rank": row["cutoff_rank"],
#                     "average_placement": row["average_placement"],
#                     "median_placement": row["median_placement"],
#                     "highest_placement": row["highest_placement"],
#                 }
#             })
#         index.upsert(vectors=vectors)
#         logger.info(f"Loaded {len(vectors)} vectors into Pinecone")

#         collection.create_index([("exam", 1)])
#         collection.create_index([("college", 1)])
#         collection.create_index([("branch", 1)])
#         collection.create_index([("cutoff_rank", 1)])
#         collection.create_index([("average_placement", 1)])
#         collection.create_index([("median_placement", 1)])
#         collection.create_index([("highest_placement", 1)])
#         logger.info("Created indexes for query optimization")

#         df.to_json("data/colleges.json", orient="records", lines=True)
#         logger.info("Saved data to data/colleges.json")

#     except Exception as e:
#         logger.error(f"Error importing data: {str(e)}", exc_info=True)
#         raise
#     finally:
#         client.close()

# if __name__ == "__main__":
#     XLSX_PATH = "data/college_data.xlsx"
#     import_college_data(XLSX_PATH)