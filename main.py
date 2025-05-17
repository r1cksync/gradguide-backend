from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
from app.api import auth, chatbot, filters
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.core.config import settings
from app.db.mongodb import db
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("gradguide")

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(chatbot.router, prefix="/api/chatbot", tags=["chatbot"])
app.include_router(filters.router, prefix="/api/filters", tags=["filters"])

# Database events
@app.on_event("startup")
async def startup_db_client():
    try:
        await connect_to_mongo()
        logger.info("MongoDB connection successful")
        
        # Load college data from Excel if it exists
        if os.path.exists("./data/college_data.xlsx"):
            try:
                logger.info("Found college_data.xlsx, loading into database")
                df = pd.read_excel("./data/college_data.xlsx")
                logger.info(f"Excel file loaded with {len(df)} records")
                
                try:
                    # Create collection if it doesn't exist
                    collections = await db.db.list_collection_names()
                    logger.info(f"Found collections: {collections}")
                    
                    if "college_data" not in collections:
                        # Convert DataFrame to dictionary and insert into MongoDB
                        records = df.to_dict("records")
                        if records:
                            logger.info(f"Inserting {len(records)} records into MongoDB")
                            await db.db.college_data.insert_many(records)
                            logger.info(f"Successfully loaded {len(records)} college records into MongoDB")
                    else:
                        logger.info("college_data collection already exists, skipping import")
                except Exception as db_e:
                    logger.error(f"Error interacting with database: {db_e}")
                    # Create a local backup of the data
                    try:
                        os.makedirs("./data/backup", exist_ok=True)
                        df.to_json("./data/backup/college_data.json", orient="records")
                        logger.info("Created backup JSON file for data")
                    except Exception as backup_e:
                        logger.error(f"Error creating backup file: {backup_e}")
            except Exception as excel_e:
                logger.error(f"Error loading Excel file: {excel_e}")
        else:
            logger.warning("No college_data.xlsx file found in ./data/ directory")
            
            # Check if we have a JSON backup
            if os.path.exists("./data/backup/college_data.json"):
                logger.info("Found backup JSON file, will use this instead")
    except Exception as e:
        logger.error(f"MongoDB connection error: {e}")
        logger.info("Application will continue without database connection")

@app.on_event("shutdown")
async def shutdown_db_client():
    try:
        await close_mongo_connection()
        logger.info("MongoDB connection closed")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {e}")

@app.get("/")
async def root():
    return {"message": "Welcome to GradGuide API", "status": "online"}

@app.get("/health")
async def health_check():
    """Endpoint for health checks"""
    db_status = "connected"
    data_status = "available"
    
    try:
        # Test database connection
        await db.client.admin.command('ping')
    except Exception as e:
        db_status = f"disconnected: {str(e)}"
    
    # Check if data is available
    try:
        if not os.path.exists("./data/college_data.xlsx") and not os.path.exists("./data/backup/college_data.json"):
            data_status = "unavailable"
    except Exception:
        data_status = "error checking data"
    
    return {
        "status": "healthy",
        "database": db_status,
        "data": data_status,
        "version": settings.PROJECT_VERSION
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)