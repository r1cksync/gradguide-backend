from pymongo import MongoClient
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger("gradguide")

class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None

    def connect_to_database(self):
        try:
            mongodb_uri = os.getenv("MONGODB_URI", "mongodb+srv://sagnik23102:j9TildStvOeklXmg@gradguide.zdinpa4.mongodb.net/?retryWrites=true&w=majority&appName=gradguide")
            self.client = MongoClient(
                mongodb_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=20000,
                tls=True
            )
            self.client.admin.command("ping")
            self.db = self.client.gradguide
            logger.info("MongoDB connection established")
        except Exception as e:
            logger.error(f"MongoDB connection error: {str(e)}")
            raise

    def close_database_connection(self):
        try:
            if self.client:
                self.client.close()
                logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"MongoDB close error: {str(e)}")
            raise

db = MongoDB()