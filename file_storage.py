import json
import os
from datetime import datetime
from typing import List, Dict, Any
import base64

class FileStorage:
    """Manages file uploads, chat history, and conversation analysis for self-tuning"""
    
    def __init__(self, storage_file="luna_storage.json"):
        self.storage_file = storage_file
        self.data = self._load_storage()
    
    def _load_storage(self) -> Dict[str, Any]:
        """Load storage from JSON file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading storage: {e}")
                return self._create_empty_storage()
        return self._create_empty_storage()
    
    def _create_empty_storage(self) -> Dict[str, Any]:
        """Create empty storage structure"""
        return {
            "uploaded_files": [],
            "chat_history": [],
            "user_preferences": {},
            "conversation_patterns": {
                "common_topics": [],
                "response_quality": [],
                "user_satisfaction": []
            },
            "file_analysis_cache": {}
        }
    
    def _save_storage(self):
        """Save storage to JSON file"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving storage: {e}")
    
    def add_uploaded_file(self, file_info: Dict[str, Any]):
        """Add uploaded file information"""
        file_entry = {
            "id": len(self.data["uploaded_files"]) + 1,
            "filename": file_info.get("filename"),
            "file_type": file_info.get("file_type"),
            "file_size": file_info.get("file_size"),
            "upload_time": datetime.now().isoformat(),
            "file_path": file_info.get("file_path"),
            "content_preview": file_info.get("content_preview", ""),
            "analysis_summary": file_info.get("analysis_summary", "")
        }
        self.data["uploaded_files"].append(file_entry)
        self._save_storage()
        return file_entry
    
    def add_chat_message(self, user_id: str, message: Dict[str, Any]):
        """Add chat message to history"""
        chat_entry = {
            "id": len(self.data["chat_history"]) + 1,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "role": message.get("role"),
            "content": message.get("content"),
            "files": message.get("files", []),
            "emotion": message.get("emotion"),
            "response_style": message.get("response_style")
        }
        self.data["chat_history"].append(chat_entry)
        
        # Keep only last 1000 messages to prevent file bloat
        if len(self.data["chat_history"]) > 1000:
            self.data["chat_history"] = self.data["chat_history"][-1000:]
        
        self._save_storage()
        return chat_entry
    
    def get_file_by_name(self, filename: str) -> Dict[str, Any]:
        """Get file information by filename"""
        for file_entry in self.data["uploaded_files"]:
            if file_entry["filename"] == filename:
                return file_entry
        return None
    
    def get_recent_chats(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent chat messages for a user"""
        user_chats = [
            chat for chat in self.data["chat_history"]
            if chat.get("user_id") == user_id
        ]
        return user_chats[-limit:]
    
    def analyze_conversation_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze conversation patterns for self-tuning"""
        user_chats = self.get_recent_chats(user_id, limit=100)
        
        if not user_chats:
            return {}
        
        # Extract topics
        topics = []
        for chat in user_chats:
            if chat.get("role") == "user":
                content = chat.get("content", "").lower()
                # Simple topic extraction (can be enhanced with NLP)
                words = content.split()
                topics.extend([w for w in words if len(w) > 5])
        
        # Count topic frequency
        from collections import Counter
        topic_counts = Counter(topics)
        common_topics = [topic for topic, count in topic_counts.most_common(10)]
        
        # Analyze response patterns
        response_lengths = []
        for chat in user_chats:
            if chat.get("role") == "assistant":
                response_lengths.append(len(chat.get("content", "")))
        
        avg_response_length = sum(response_lengths) / len(response_lengths) if response_lengths else 0
        
        return {
            "common_topics": common_topics,
            "total_messages": len(user_chats),
            "avg_response_length": avg_response_length,
            "conversation_style": self._detect_conversation_style(user_chats)
        }
    
    def _detect_conversation_style(self, chats: List[Dict[str, Any]]) -> str:
        """Detect user's preferred conversation style"""
        casual_indicators = ["da", "dai","di", "dei", "machi", "bro", "dude"]
        formal_indicators = ["please", "thank you", "could you", "would you"]
        
        casual_count = 0
        formal_count = 0
        
        for chat in chats:
            if chat.get("role") == "user":
                content = chat.get("content", "").lower()
                casual_count += sum(1 for word in casual_indicators if word in content)
                formal_count += sum(1 for word in formal_indicators if word in content)
        
        if casual_count > formal_count * 2:
            return "casual"
        elif formal_count > casual_count * 2:
            return "formal"
        else:
            return "balanced"
    
    def cache_file_analysis(self, filename: str, analysis: str):
        """Cache file analysis to avoid re-analyzing"""
        self.data["file_analysis_cache"][filename] = {
            "analysis": analysis,
            "cached_at": datetime.now().isoformat()
        }
        self._save_storage()
    
    def get_cached_analysis(self, filename: str) -> str:
        """Get cached file analysis"""
        cache = self.data["file_analysis_cache"].get(filename)
        if cache:
            return cache.get("analysis")
        return None

# Global instance
file_storage = FileStorage()
