from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
from app.api import auth, chatbot, filters
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.core.config import settings
from app.db.mongodb import db
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("gradguide")

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(chatbot.router, prefix="/api/chatbot", tags=["chatbot"])
app.include_router(filters.router, prefix="/api/filters", tags=["filters"])

@app.on_event("startup")
def startup_db_client():
    try:
        connect_to_mongo()
        if os.path.exists("./data/college_data.xlsx"):
            df = pd.read_excel("./data/college_data.xlsx")
            collections = db.db.list_collection_names()
            if "college_data" not in collections:
                records = df.to_dict("records")
                if records:
                    db.db.college_data.insert_many(records)
                    logger.info(f"Loaded {len(records)} college records into MongoDB")
        else:
            logger.warning("No college_data.xlsx found")
    except Exception as e:
        logger.error(f"Startup error: {e}")

@app.on_event("shutdown")
def shutdown_db_client():
    close_mongo_connection()

@app.get("/")
def root():
    return {"message": "Welcome to GradGuide API", "status": "online"}

@app.get("/health")
def health_check():
    db_status = "connected"
    data_status = "available"
    try:
        db.client.admin.command('ping')
    except Exception as e:
        db_status = f"disconnected: {str(e)}"
    if not os.path.exists("./data/college_data.xlsx") and not os.path.exists("./data/backup/college_data.json"):
        data_status = "unavailable"
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