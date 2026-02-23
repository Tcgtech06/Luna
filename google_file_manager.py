import os
import json
import time
from typing import Dict, Any, Optional
import google.generativeai as genai
from datetime import datetime
from model_manager import model_manager

class GoogleFileManager:
    """Manages file uploads using Google's File API and caches analysis"""
    
    def __init__(self, api_key: str, cache_file="file_analysis_cache.json"):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.cache_file = cache_file
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load analysis cache from JSON file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading cache: {e}")
                return {"files": {}, "analyses": {}}
        return {"files": {}, "analyses": {}}
    
    def _save_cache(self):
        """Save analysis cache to JSON file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def upload_file_to_google(self, file_path: str, display_name: str) -> Optional[Dict[str, Any]]:
        """Upload file to Google's File API"""
        try:
            print(f"📤 Uploading {display_name} to Google File API...")
            
            # Upload file using Google's File API
            uploaded_file = genai.upload_file(path=file_path, display_name=display_name)
            
            # Wait for file to be processed
            print(f"⏳ Waiting for file processing...")
            while uploaded_file.state.name == "PROCESSING":
                time.sleep(2)
                uploaded_file = genai.get_file(uploaded_file.name)
            
            if uploaded_file.state.name == "FAILED":
                raise Exception(f"File processing failed: {uploaded_file.state.name}")
            
            print(f"✅ File uploaded successfully: {uploaded_file.uri}")
            
            # Store file info in cache
            file_info = {
                "uri": uploaded_file.uri,
                "name": uploaded_file.name,
                "display_name": display_name,
                "mime_type": uploaded_file.mime_type,
                "size_bytes": uploaded_file.size_bytes,
                "upload_time": datetime.now().isoformat(),
                "state": uploaded_file.state.name
            }
            
            self.cache["files"][display_name] = file_info
            self._save_cache()
            
            return file_info
            
        except Exception as e:
            print(f"❌ Error uploading file: {e}")
            return None
    
    def analyze_file_with_google(self, file_uri: str, file_name: str, prompt: str = None) -> Dict[str, Any]:
        """Analyze file using Google's models with automatic fallback"""
        try:
            # Check if analysis already exists in cache
            cache_key = f"{file_name}_{hash(prompt) if prompt else 'default'}"
            if cache_key in self.cache["analyses"]:
                print(f"📋 Using cached analysis for {file_name}")
                return self.cache["analyses"][cache_key]
            
            print(f"🔍 Analyzing {file_name} with Google models...")
            
            # Default comprehensive analysis prompt
            if not prompt:
                prompt = """Analyze this file comprehensively and provide:

1. **Content Summary**: A detailed summary of what this file contains
2. **Main Topics/Themes**: Key topics, themes, or subjects covered
3. **Key Information**: Important facts, data, or insights
4. **Content Type**: What type of content this is (e.g., chat log, document, image, code, etc.)
5. **Notable Details**: Any interesting or notable details worth mentioning

For images: Describe what you see, including objects, people, text, colors, mood, and context.
For text/documents: Summarize the content, extract key points, and identify the purpose.
For chat logs: Summarize the conversation, identify participants, main topics discussed.

Be thorough but concise. Provide actionable insights."""

            # Get available analysis models
            available_models = model_manager.get_all_available_analysis_models()
            
            if not available_models:
                return {
                    "success": False,
                    "error": "All analysis models are currently exhausted. Please wait a moment and try again."
                }
            
            # Try available models
            for model_name in available_models:
                try:
                    print(f"🤖 Trying analysis model: {model_name}")
                    model = genai.GenerativeModel(model_name)
                    
                    # Get the file from Google's API
                    google_file = genai.get_file(file_uri.split('/')[-1])
                    
                    # Generate content with the file
                    response = model.generate_content([google_file, prompt])
                    
                    analysis_result = {
                        "success": True,
                        "analysis": response.text,
                        "model_used": model_name,
                        "analyzed_at": datetime.now().isoformat(),
                        "file_name": file_name,
                        "prompt_used": prompt
                    }
                    
                    # Cache the analysis
                    self.cache["analyses"][cache_key] = analysis_result
                    self._save_cache()
                    
                    print(f"✅ Analysis complete with {model_name}")
                    return analysis_result
                    
                except Exception as e:
                    error_str = str(e)
                    print(f"❌ Model {model_name} failed: {error_str[:200]}")
                    
                    if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                        # Mark model as exhausted
                        model_manager.handle_quota_error(model_name, error_str)
                        print(f"⏭️ Trying next available model...")
                        time.sleep(1)  # Brief delay
                        continue
                    else:
                        # Other error, try next model
                        if model_name != available_models[-1]:
                            continue
                        else:
                            return {
                                "success": False,
                                "error": f"Analysis failed: {error_str[:200]}"
                            }
            
            return {
                "success": False,
                "error": "All available models failed or are exhausted"
            }
            
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_cached_analysis(self, file_name: str, prompt: str = None) -> Optional[Dict[str, Any]]:
        """Get cached analysis for a file"""
        cache_key = f"{file_name}_{hash(prompt) if prompt else 'default'}"
        return self.cache["analyses"].get(cache_key)
    
    def get_file_info(self, file_name: str) -> Optional[Dict[str, Any]]:
        """Get file information from cache"""
        return self.cache["files"].get(file_name)
    
    def answer_question_about_file(self, file_name: str, question: str) -> Dict[str, Any]:
        """Answer a question about a file using cached analysis or new query"""
        try:
            # Get file info
            file_info = self.get_file_info(file_name)
            if not file_info:
                return {
                    "success": False,
                    "error": f"File {file_name} not found in cache"
                }
            
            # Check if we have a cached analysis for this specific question
            cache_key = f"{file_name}_{hash(question)}"
            if cache_key in self.cache["analyses"]:
                print(f"📋 Using cached answer for question about {file_name}")
                return self.cache["analyses"][cache_key]
            
            # Get general analysis first
            general_analysis = self.get_cached_analysis(file_name)
            
            if general_analysis and general_analysis.get("success"):
                # Use the cached analysis to answer the question
                answer_prompt = f"""Based on this file analysis:

{general_analysis['analysis']}

Please answer this question: {question}

Provide a clear, concise answer based on the analysis above."""

                # Try to answer using chat models (lighter, for frequent use)
                available_models = model_manager.get_all_available_chat_models()
                
                if not available_models:
                    # Fallback to cached analysis
                    return {
                        "success": True,
                        "answer": f"Based on the file analysis: {general_analysis['analysis'][:500]}...",
                        "note": "All models exhausted - using cached analysis"
                    }
                
                for model_name in available_models:
                    try:
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(answer_prompt)
                        
                        result = {
                            "success": True,
                            "answer": response.text,
                            "model_used": model_name,
                            "answered_at": datetime.now().isoformat()
                        }
                        
                        # Cache this Q&A
                        self.cache["analyses"][cache_key] = result
                        self._save_cache()
                        
                        return result
                        
                    except Exception as e:
                        error_str = str(e)
                        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                            model_manager.handle_quota_error(model_name, error_str)
                            if model_name != available_models[-1]:
                                time.sleep(1)
                                continue
                        else:
                            if model_name != available_models[-1]:
                                continue
                        
                        # Fallback to using just the cached analysis
                        if model_name == available_models[-1]:
                            return {
                                "success": True,
                                "answer": f"Based on the file analysis: {general_analysis['analysis'][:500]}...",
                                "note": "Using cached analysis due to API limits"
                            }
            else:
                # No cached analysis, need to analyze the file with the question
                return self.analyze_file_with_google(
                    file_info["uri"],
                    file_name,
                    f"Analyze this file and answer: {question}"
                )
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_uploaded_files(self) -> list:
        """List all uploaded files"""
        return list(self.cache["files"].keys())
    
    def delete_file_from_google(self, file_name: str) -> bool:
        """Delete file from Google's File API and cache"""
        try:
            file_info = self.get_file_info(file_name)
            if file_info:
                # Delete from Google
                genai.delete_file(file_info["name"])
                
                # Remove from cache
                del self.cache["files"][file_name]
                
                # Remove all analyses for this file
                keys_to_remove = [k for k in self.cache["analyses"].keys() if k.startswith(file_name)]
                for key in keys_to_remove:
                    del self.cache["analyses"][key]
                
                self._save_cache()
                print(f"🗑️ Deleted {file_name} from Google and cache")
                return True
            return False
        except Exception as e:
            print(f"❌ Error deleting file: {e}")
            return False
