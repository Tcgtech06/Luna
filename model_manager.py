import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import os

class ModelManager:
    """Manages model selection, quota tracking, and automatic fallback"""
    
    def __init__(self, quota_reset_file="model_quota_status.json"):
        self.quota_reset_file = quota_reset_file
        self.quota_status = self._load_quota_status()
        
        # High-power models for file/image analysis (used infrequently)
        self.analysis_models = [
            "gemini-3.1-pro",
            "gemini-3-pro",
            "gemini-2-pro-exp",
            "gemini-2-flash-exp",
            "gemini-2-flash",
            "gemini-2-flash-lite",
            "gemini-1.5-pro",
            "gemini-2.5-pro"
        ]
        
        # Light models for chat/text responses (used frequently)
        self.chat_models = [
            "gemini-2.5-flash",
            "gemini-3-flash",
            "gemini-2.5-flash-lite",
            "gemini-flash-latest",
            "gemini-pro-latest",
            "gemini-2-flash",
            "gemini-2-flash-lite"
        ]
        
        # Backup models (if all else fails)
        self.backup_models = [
            "gemma-3-27b",
            "gemma-3-12b",
            "gemma-3-4b",
            "gemma-3-2b",
            "gemma-3-1b"
        ]
    
    def _load_quota_status(self) -> Dict:
        """Load quota status from file"""
        if os.path.exists(self.quota_reset_file):
            try:
                with open(self.quota_reset_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_quota_status(self):
        """Save quota status to file"""
        try:
            with open(self.quota_reset_file, 'w') as f:
                json.dump(self.quota_status, f, indent=2)
        except Exception as e:
            print(f"Error saving quota status: {e}")
    
    def mark_model_exhausted(self, model_name: str, retry_after_seconds: int = 60):
        """Mark a model as exhausted and set when it can be retried"""
        reset_time = (datetime.now() + timedelta(seconds=retry_after_seconds)).isoformat()
        self.quota_status[model_name] = {
            "exhausted": True,
            "reset_time": reset_time,
            "exhausted_at": datetime.now().isoformat()
        }
        self._save_quota_status()
        print(f"⏸️ Model {model_name} suspended until {reset_time}")
    
    def is_model_available(self, model_name: str) -> bool:
        """Check if a model is available (not exhausted or reset time passed)"""
        if model_name not in self.quota_status:
            return True
        
        status = self.quota_status[model_name]
        if not status.get("exhausted"):
            return True
        
        # Check if reset time has passed
        reset_time = datetime.fromisoformat(status["reset_time"])
        if datetime.now() >= reset_time:
            # Reset the model
            del self.quota_status[model_name]
            self._save_quota_status()
            print(f"✅ Model {model_name} quota reset - now available")
            return True
        
        return False
    
    def get_available_models(self, model_list: List[str]) -> List[str]:
        """Get list of available models from a given list"""
        available = []
        for model in model_list:
            if self.is_model_available(model):
                available.append(model)
        return available
    
    def get_next_analysis_model(self) -> Optional[str]:
        """Get next available model for file analysis"""
        available = self.get_available_models(self.analysis_models)
        if available:
            return available[0]
        
        # Try backup models
        available = self.get_available_models(self.backup_models)
        if available:
            print("⚠️ Using backup model for analysis")
            return available[0]
        
        return None
    
    def get_next_chat_model(self) -> Optional[str]:
        """Get next available model for chat"""
        available = self.get_available_models(self.chat_models)
        if available:
            return available[0]
        
        # Try analysis models as fallback (powerful models)
        print("⚠️ All chat models exhausted, switching to powerful analysis models")
        available = self.get_available_models(self.analysis_models)
        if available:
            return available[0]
        
        # Try backup models
        available = self.get_available_models(self.backup_models)
        if available:
            print("⚠️ Using backup model for chat")
            return available[0]
        
        return None
    
    def get_all_available_analysis_models(self) -> List[str]:
        """Get all available analysis models in priority order"""
        available = self.get_available_models(self.analysis_models)
        if not available:
            available = self.get_available_models(self.backup_models)
        return available
    
    def get_all_available_chat_models(self) -> List[str]:
        """Get all available chat models in priority order"""
        available = self.get_available_models(self.chat_models)
        if not available:
            # Fallback to analysis models
            available = self.get_available_models(self.analysis_models)
        if not available:
            # Last resort: backup models
            available = self.get_available_models(self.backup_models)
        return available
    
    def extract_retry_delay(self, error_message: str) -> int:
        """Extract retry delay from error message"""
        import re
        
        # Look for patterns like "retry in 42.810231404s" or "retryDelay': '42s'"
        patterns = [
            r'retry in (\d+(?:\.\d+)?)\s*s',
            r"retryDelay['\"]:\s*['\"](\d+)s",
            r'Please retry in (\d+(?:\.\d+)?)\s*seconds'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, error_message, re.IGNORECASE)
            if match:
                return int(float(match.group(1))) + 5  # Add 5 seconds buffer
        
        # Default to 60 seconds if can't parse
        return 60
    
    def handle_quota_error(self, model_name: str, error_message: str):
        """Handle quota exceeded error and mark model as exhausted"""
        retry_delay = self.extract_retry_delay(error_message)
        self.mark_model_exhausted(model_name, retry_delay)
    
    def get_quota_summary(self) -> Dict:
        """Get summary of quota status"""
        total_models = len(self.analysis_models) + len(self.chat_models) + len(self.backup_models)
        exhausted_count = len([m for m in self.quota_status.values() if m.get("exhausted")])
        available_count = total_models - exhausted_count
        
        return {
            "total_models": total_models,
            "available": available_count,
            "exhausted": exhausted_count,
            "exhausted_models": [
                {
                    "model": name,
                    "reset_time": status["reset_time"],
                    "exhausted_at": status["exhausted_at"]
                }
                for name, status in self.quota_status.items()
                if status.get("exhausted")
            ]
        }

# Global instance
model_manager = ModelManager()
