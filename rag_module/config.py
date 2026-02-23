import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Google Gemini Configuration
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # RAG Settings
    # Optimized for large PDFs - larger chunks = fewer API calls, faster processing
    # A 100-page PDF creates ~125 chunks instead of 250 with these settings
    CHUNK_SIZE = 2000  # Increased from 1000 for better performance
    CHUNK_OVERLAP = 400  # Proportional overlap maintained (20%)
    
    # Batch processing settings for API rate limiting
    EMBEDDING_BATCH_SIZE = 10  # Reduced from 50 to avoid quota issues
    
    # Multiple Embedding Models for fallback when rate limited
    EMBEDDING_MODELS = [
        "models/gemini-embedding-001",
        "models/text-embedding-004",
        "models/embedding-001"
    ]
    
    # Primary embedding model (first in list)
    EMBEDDING_MODEL = EMBEDDING_MODELS[0]
    
    # Get models from model_manager dynamically
    @staticmethod
    def get_llm_models():
        """Get available LLM models from model_manager"""
        try:
            from model_manager import model_manager
            return model_manager.get_all_available_chat_models()
        except:
            # Fallback to default list if model_manager not available
            return [
                "gemini-2.5-flash-lite",
                "gemini-2-flash-lite",
                "gemini-flash-latest",
                "gemini-2-flash",
                "gemini-pro-latest"
            ]
    
    # Multiple Generation Models for fallback (use chat models, not analysis models)
    LLM_MODELS = [
        "gemini-2.5-flash",
        "gemini-flash-latest",
        "gemini-pro-latest",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b"
    ]
    
    # Primary generation model (first in list)
    LLM_MODEL = LLM_MODELS[0]
    
    PERSIST_DIRECTORY = "./chroma_db"
