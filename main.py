from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
from app.api import auth, chatbot, filters
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.core.config import settings
from app.db.mongodb import db

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
    await connect_to_mongo()
    
    # Load college data from Excel if it exists
    try:
        if os.path.exists("./data/college_data.xlsx"):
            df = pd.read_excel("./data/college_data.xlsx")
            
            # Create collection if it doesn't exist
            if "college_data" not in await db.db.list_collection_names():
                # Convert DataFrame to dictionary and insert into MongoDB
                records = df.to_dict("records")
                await db.db.college_data.insert_many(records)
                print(f"Loaded {len(records)} college records into MongoDB")
    except Exception as e:
        print(f"Error loading college data: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

@app.get("/")
async def root():
    return {"message": "Welcome to GradGuide API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)