from pymongo import MongoClient
from app.core.config import settings
import logging

logger = logging.getLogger("gradguide")

class MongoDB:
    client = None
    db = None

db = MongoDB()

def connect_to_mongo():
    try:
        db.client = MongoClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=20000
        )
        db.db = db.client.gradguide
        db.client.admin.command('ping')
        logger.info("Connected to MongoDB")
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        raise

def close_mongo_connection():
    try:
        if db.client:
            db.client.close()
            logger.info("MongoDB connection closed")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {e}")