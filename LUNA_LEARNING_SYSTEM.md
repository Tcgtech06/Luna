# Luna Data Storage & Self-Learning System

## 📊 **Current Data Storage Architecture**

### **1. User Memory System (`user_memory` dictionary)**
```python
user_memory = {
    "user_id": {
        "conversation_count": 5,
        "last_interaction": "2026-02-17T19:45:00",
        
        # Emotional Intelligence
        "emotion_history": [
            {"emotion": "happy", "intensity": "medium", "timestamp": "..."},
            {"emotion": "curious", "intensity": "high", "timestamp": "..."}
        ],
        
        # Topic & Interest Tracking
        "topics_discussed": ["website", "development", "budget", "tcgtech"],
        
        # Language Preferences
        "preferences": {
            "casual_language_permission": True,
            "preferred_language": "tanglish"
        },
        
        # Enhanced Learning Data
        "learning_data": {
            "successful_suggestions": [],
            "user_feedback": [],
            "query_types": [
                {"type": "digital_solution", "message": "website develop pannanu", "timestamp": "..."}
            ],
            "language_patterns": {
                "casual_detected": True,
                "formal_requested": False
            },
            "budget_info": [
                {"budget": "7k", "context": "enoda budget only 7k tha", "timestamp": "..."}
            ],
            "project_requirements": [
                {"requirement": "enaku website develop pananu", "timestamp": "..."}
            ]
        }
    }
}
```

### **2. Data Storage Location**
- **In-Memory Storage**: Currently stored in Python dictionary (`user_memory`)
- **Session-Based**: Data persists during server runtime
- **User-Specific**: Each user gets unique memory based on `user_id`

## 🧠 **Self-Learning Mechanisms**

### **1. Real-Time Learning**
```python
def update_user_memory():
    # Extracts and learns from every message
    # Detects patterns, preferences, budget info
    # Updates user profile dynamically
```

### **2. Pattern Recognition**
- **Budget Detection**: "7k", "10k", "5 thousand" → stores budget preferences
- **Project Requirements**: "website develop", "app create" → identifies needs
- **Language Patterns**: "da", "di", "respect ah pesu" → learns communication style
- **Query Types**: Digital solutions, TCG TECH queries → categorizes requests

### **3. Contextual Intelligence**
```python
def get_learning_insights():
    # Provides context based on learned data
    # Example: "[BUDGET INSIGHT: User mentioned 7k budget]"
    # Example: "[PROJECT INSIGHT: User wants website development]"
```

## 🔄 **Learning Process Flow**

### **Step 1: Data Collection**
- Every user message is analyzed
- Keywords, emotions, patterns extracted
- Context stored in memory

### **Step 2: Pattern Analysis**
- Budget patterns identified and stored
- Project requirements categorized
- Language preferences tracked
- Query types classified

### **Step 3: Context Generation**
- Learning insights generated for each response
- Personalized context added to prompts
- Historical patterns referenced

### **Step 4: Response Optimization**
- Suggestions based on learned preferences
- Language style adapted to user patterns
- TCG TECH recommendations tailored to needs

## 💾 **Storage Details**

### **Current Implementation**
- **Type**: In-memory Python dictionary
- **Scope**: Server session (lost on restart)
- **Size**: Limited to prevent memory bloat
- **Retention**: Last 20 emotions, 50 topics, 10 queries

### **Data Points Tracked**
1. **Conversation History**: Messages, responses, timestamps
2. **Emotional Patterns**: Detected emotions, intensity levels
3. **Language Preferences**: Casual vs formal, permission states
4. **Project Information**: Budget, requirements, timelines
5. **Query Patterns**: Types of requests, frequency
6. **TCG TECH Interactions**: Suggestions, feedback, outcomes

## 🚀 **Enhancement Opportunities**

### **Future Improvements**
1. **Persistent Storage**: Database integration for long-term memory
2. **Cross-Session Learning**: Remember users across sessions
3. **Advanced Analytics**: Deeper pattern recognition
4. **Feedback Loop**: User satisfaction tracking
5. **Predictive Suggestions**: Anticipate user needs

### **Current Limitations**
- **Session-Based**: Data lost on server restart
- **Memory Constraints**: Limited storage capacity
- **Single User**: No cross-user learning
- **No Persistence**: No long-term data retention

## 📈 **Learning Effectiveness**

### **What Luna Learns**
✅ User communication preferences  
✅ Budget constraints and requirements  
✅ Project types and needs  
✅ Language comfort levels  
✅ Emotional response patterns  
✅ TCG TECH suggestion effectiveness  

### **How Learning Improves Responses**
- **Better Suggestions**: Based on budget and requirements
- **Appropriate Language**: Matches user communication style
- **Relevant Context**: References past conversations
- **TCG TECH Promotion**: Tailored to user needs
- **Emotional Intelligence**: Responds to detected emotions

## 🔧 **Technical Implementation**

### **Memory Management**
```python
# Prevents memory bloat
if len(memory['emotion_history']) > 20:
    memory['emotion_history'] = memory['emotion_history'][-20:]

# Keeps recent data relevant
if len(memory['topics_discussed']) > 50:
    memory['topics_discussed'] = memory['topics_discussed'][-50:]
```

### **Pattern Extraction**
```python
# Budget extraction
budget_patterns = [
    r'budget.*?(\d+k|\d+ thousand|\d+)',
    r'(\d+k).*?budget',
    r'only.*?(\d+k)'
]

# Project requirement detection
if any(keyword in message.lower() for keyword in ['website', 'app', 'software']):
    memory['learning_data']['project_requirements'].append(...)
```

This system enables Luna to provide increasingly personalized and effective responses through continuous learning from user interactions.
