from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import base64
import PIL.Image
from io import BytesIO

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

GOOGLE_API_KEY = "AIzaSyB32ht69HpJiaRT06eiWy7D8_T-nJOVjuk"
genai.configure(api_key=GOOGLE_API_KEY)

class ImageRequest(BaseModel):
    prompt: str

@app.post("/generate-image")
async def generate_image(request: ImageRequest):
    try:
        print(f"Generating image: {request.prompt}")
        
        # Try different model names
        model_names = [
            'gemini-2.5-flash-image',
            'gemini-2.0-flash-exp-image',
            'imagen-3.0-generate-001'
        ]
        
        for model_name in model_names:
            try:
                print(f"Trying model: {model_name}")
                model = genai.GenerativeModel(model_name)
                
                response = model.generate_content(
                    f"Generate an image: {request.prompt}",
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.9,
                    )
                )
                
                print(f"Response: {response}")
                
                if response.parts:
                    for part in response.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            image_data = part.inline_data.data
                            img_str = base64.b64encode(image_data).decode()
                            print(f"Success with {model_name}!")
                            return {"image": f"data:image/png;base64,{img_str}"}
                        elif hasattr(part, 'text'):
                            print(f"Got text response: {part.text[:100]}")
                
            except Exception as e:
                print(f"Model {model_name} failed: {e}")
                continue
        
        raise HTTPException(status_code=500, detail="Image generation not available with current API key. Gemini image generation may require a different API or model.")
        
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}
