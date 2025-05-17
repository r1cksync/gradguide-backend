from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import logging

# Configure logging
logger = logging.getLogger("gradguide")

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

db = MongoDB()

async def connect_to_mongo():
    try:
        # Initialize MongoDB client with TLS/SSL settings
        db.client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            tls=True,  # Enable TLS/SSL
            tlsAllowInvalidCertificates=True,  # Allow invalid certificates (for testing)
            serverSelectionTimeoutMS=5000,  # 5-second timeout
            connectTimeoutMS=20000  # 20-second connection timeout
        )
        db.db = db.client.gradguide
        # Verify connection
        await db.client.admin.command('ping')
        logger.info("Connected to MongoDB")
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        raise

async def close_mongo_connection():
    try:
        if db.client:
            db.client.close()
            logger.info("MongoDB connection closed")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {e}")