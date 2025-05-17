import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    PROJECT_NAME: str = "GradGuide API"
    PROJECT_VERSION: str = "1.0.0"
    
    # MongoDB
    MONGODB_URI: str = os.getenv("MONGODB_URI")
    
    # OpenRouter
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3-haiku")
    
    # Clerk Auth
    CLERK_SECRET_KEY: str = os.getenv("CLERK_SECRET_KEY")
    CLERK_API_URL: str = os.getenv("CLERK_API_URL")

settings = Settings()