import os
from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import base64
from PIL import Image
import io

class FileAnalyzer:
    """Analyzes uploaded files using Gemini models"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.models = [
            "gemini-2.5-flash",
            "gemini-2.5-pro",
            "gemini-2.0-flash",
            "gemini-flash-latest"
        ]
    
    def analyze_file(self, file_path: str, file_type: str, filename: str) -> Dict[str, Any]:
        """Analyze file content based on type"""
        try:
            if file_type.startswith('image/'):
                return self._analyze_image(file_path, filename)
            elif file_type in ['text/plain', 'application/pdf'] or filename.endswith('.txt'):
                return self._analyze_text_file(file_path, filename)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported file type: {file_type}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _analyze_image(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Analyze image using Gemini Vision"""
        try:
            # Read and encode image
            with open(file_path, 'rb') as f:
                image_data = f.read()
            
            # Convert to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Try multiple models
            for model_name in self.models:
                try:
                    llm = ChatGoogleGenerativeAI(
                        model=model_name,
                        google_api_key=self.api_key,
                        temperature=0.3
                    )
                    
                    # Create message with image
                    message = HumanMessage(
                        content=[
                            {
                                "type": "text",
                                "text": "Analyze this image in detail. Describe what you see, including objects, people, text, colors, mood, and any other relevant details. Be descriptive but concise."
                            },
                            {
                                "type": "image_url",
                                "image_url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        ]
                    )
                    
                    response = llm.invoke([message])
                    
                    return {
                        "success": True,
                        "analysis": response.content,
                        "file_type": "image",
                        "model_used": model_name
                    }
                    
                except Exception as e:
                    print(f"Model {model_name} failed for image analysis: {e}")
                    if model_name == self.models[-1]:
                        raise e
                    continue
            
            return {
                "success": False,
                "error": "All models failed for image analysis"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Image analysis error: {str(e)}"
            }
    
    def _analyze_text_file(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Analyze text file content"""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Limit content size for analysis
            max_chars = 10000
            if len(content) > max_chars:
                content_preview = content[:max_chars] + f"\n\n[Content truncated - showing first {max_chars} characters of {len(content)} total]"
            else:
                content_preview = content
            
            # Try multiple models
            for model_name in self.models:
                try:
                    llm = ChatGoogleGenerativeAI(
                        model=model_name,
                        google_api_key=self.api_key,
                        temperature=0.3
                    )
                    
                    prompt = f"""Analyze this text file content and provide a comprehensive summary:

Filename: {filename}
Content:
{content_preview}

Please provide:
1. A brief summary of the content
2. Main topics or themes
3. Key information or insights
4. Content type (e.g., chat log, document, code, etc.)

Be concise but informative."""
                    
                    response = llm.invoke([HumanMessage(content=prompt)])
                    
                    return {
                        "success": True,
                        "analysis": response.content,
                        "content_preview": content[:500] + "..." if len(content) > 500 else content,
                        "file_type": "text",
                        "char_count": len(content),
                        "model_used": model_name
                    }
                    
                except Exception as e:
                    print(f"Model {model_name} failed for text analysis: {e}")
                    if model_name == self.models[-1]:
                        raise e
                    continue
            
            return {
                "success": False,
                "error": "All models failed for text analysis"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Text analysis error: {str(e)}"
            }
    
    def quick_summary(self, file_path: str, file_type: str) -> str:
        """Get a quick one-line summary of the file"""
        try:
            if file_type.startswith('image/'):
                return "📷 Image file - ready for visual analysis"
            elif file_type in ['text/plain'] or file_path.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(200)
                return f"📄 Text file - {len(content)} characters preview available"
            else:
                return f"📎 {file_type} file uploaded"
        except:
            return "📎 File uploaded successfully"
