from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import uvicorn

app = FastAPI(title="Luna - AI Chatbot by TCG TECH")

# CORS middleware - Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "https://huggingface.co",  # Hugging Face
        "*"  # Allow all origins (remove in production for security)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set API key
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY", "AIzaSyBc9nlbPfYzGFIVeDz8hOcU61Ig4R7NxYc")

# Available Gemini models
GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-3-flash",
]

# System prompt
SYSTEM_PROMPT = """You are Luna, a helpful AI assistant created by TCG TECH. 
When someone asks your name in any language (like "What is your name?", "unoda peru ena?", "உன் பெயர் என்ன?"), 
respond that your name is Luna (in Tamil: "என் பெயர் Luna" or "enoda peru Luna").
You are friendly, helpful, and always ready to assist users with their questions."""

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    files: Optional[List[str]] = []

class ChatResponse(BaseModel):
    response: str
    error: Optional[str] = None

# Global model index
current_model_index = 0

def get_llm():
    global current_model_index
    model_name = GEMINI_MODELS[current_model_index]
    return ChatGoogleGenerativeAI(model=model_name, temperature=0.7)

def try_next_model():
    global current_model_index
    current_model_index = (current_model_index + 1) % len(GEMINI_MODELS)
    return GEMINI_MODELS[current_model_index]

@app.get("/")
async def read_root():
    """API root endpoint"""
    return {
        "name": "Luna AI Chatbot",
        "version": "1.0.0",
        "description": "AI Chatbot powered by Google Gemini AI",
        "created_by": "TCG TECH",
        "endpoints": {
            "chat": "POST /chat",
            "upload": "POST /upload"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Luna AI Chatbot"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Prepare file context
        file_context = ""
        if request.files:
            file_context = f"\n\n[User has uploaded {len(request.files)} file(s): {', '.join(request.files)}. Please acknowledge these files in your response if relevant to the question.]"
        
        enhanced_prompt = request.message + file_context
        
        # Try models with fallback
        max_retries = len(GEMINI_MODELS)
        for attempt in range(max_retries):
            try:
                llm = get_llm()
                messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=enhanced_prompt)]
                response = llm.invoke(messages)
                return ChatResponse(response=response.content)
            except Exception as e:
                error_msg = str(e)
                if "quota" in error_msg.lower() or "limit" in error_msg.lower() or "not found" in error_msg.lower() or "404" in error_msg:
                    try_next_model()
                    if attempt < max_retries - 1:
                        continue
                    else:
                        return ChatResponse(response="Sorry, I'm unable to respond right now. Please try again later.", error="All models exhausted")
                else:
                    return ChatResponse(response="Sorry, an error occurred. Please try again.", error=str(e))
        
        return ChatResponse(response="Sorry, an error occurred.", error="Unknown error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        return {"filename": file.filename, "content_type": file.content_type}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Create static directory if it doesn't exist
    os.makedirs("static", exist_ok=True)
    print("Starting Luna chatbot server...")
    print("Visit: http://localhost:7860")
    uvicorn.run(app, host="0.0.0.0", port=7860)
