from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

db = MongoDB()

async def connect_to_mongo():
    # Add SSL configuration
    db.client = AsyncIOMotorClient(
        settings.MONGODB_URI,
        ssl=True,
        ssl_cert_reqs='CERT_NONE',  # Disable certificate verification
        serverSelectionTimeoutMS=5000,  # 5 second timeout
        connectTimeoutMS=20000
    )
    db.db = db.client.gradguide
    # Verify connection
    await db.client.admin.command('ping')
    print("Connected to MongoDB")

async def close_mongo_connection():
    if db.client:
        db.client.close()
        print("MongoDB connection closed")