import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "GradGuide API"
    PROJECT_VERSION: str = "1.0.0"
    MONGODB_URI: str = os.getenv("MONGODB_URI")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3-haiku")
    CLERK_SECRET_KEY: str = os.getenv("CLERK_SECRET_KEY")
    CLERK_API_URL: str = os.getenv("CLERK_API_URL")

settings = Settings()