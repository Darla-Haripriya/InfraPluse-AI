"""
Configuration module for InfraPulse AI Agent.
Loads settings from environment variables with safe enterprise defaults.
"""
import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    # App Information
    app_name: str = "InfraPulse AI - Hindsight SRE Agent"
    environment: str = os.getenv("ENVIRONMENT", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Hindsight Memory Bank Configuration (Vectorize Cloud)
    hindsight_api_key: str = os.getenv("HINDSIGHT_API_KEY", "")
    hindsight_api_url: str = os.getenv("HINDSIGHT_API_URL", "https://api.vectorize.io/v1/hindsight")
    hindsight_memory_bank_id: str = os.getenv("HINDSIGHT_MEMORY_BANK_ID", "mb_infrapulse_sre_prod_01")
    
    # LLM Provider Configuration (Groq Primary)
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "qwen/qwen3-32b")
    
    # Google Gemini Fallback & Grounding
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    # Server Ports
    backend_host: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    backend_port: int = int(os.getenv("BACKEND_PORT", "8000"))

settings = Settings()
