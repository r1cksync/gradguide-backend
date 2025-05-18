# import os
# from pydantic_settings import BaseSettings
# from dotenv import load_dotenv

# load_dotenv()

# class Settings(BaseSettings):
#     PROJECT_NAME: str = "GradGuide API"
#     PROJECT_VERSION: str = "1.0.0"
#     MONGODB_URI: str
#     GROK_API_KEY: str

#     class Config:
#         env_file = ".env"
#         env_file_encoding = "utf-8"
#         extra = "ignore"  # Allow extra environment variables

# settings = Settings()


from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "GradGuide API"
    PROJECT_VERSION: str = "1.0.0"
    MONGODB_URI: str
    OPENROUTER_API_KEY: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore" 

settings = Settings()