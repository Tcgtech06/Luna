# Add this to your Hugging Face backend app.py file
# This enables CORS so your frontend can communicate with the backend

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware - ADD THIS SECTION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (for development)
    # For production, replace with: allow_origins=["https://your-frontend-domain.com"]
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Your existing routes below...
@app.post("/chat")
async def chat(request: dict):
    # Your existing chat logic
    pass
