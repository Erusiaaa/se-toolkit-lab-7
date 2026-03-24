import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Get the project root directory (parent of bot/)
PROJECT_ROOT = Path(__file__).parent.parent

class Settings(BaseSettings):
    bot_token: str = ""
    lms_api_base_url: str = "http://localhost:42002"
    lms_api_key: str = "13"
    llm_api_key: str = ""
    llm_api_base_url: str = "http://localhost:42005/v1"
    llm_api_model: str = "meta-llama/llama-3-8b-instruct"
    
    class Config:
        env_file = PROJECT_ROOT / ".env.bot.secret"

settings = Settings()
