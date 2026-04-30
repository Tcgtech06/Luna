from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import re
import json
import requests
import tempfile
import zipfile
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import uvicorn
from dotenv import load_dotenv

# Load environment variables
# In Hugging Face, environment variables are set in Space settings
# Locally, load from .env.backend
if os.path.exists('.env.backend'):
    load_dotenv('.env.backend')
else:
    print("⚠️ Running in production mode - using environment variables from system")

# Import Google File Manager for file analysis
try:
    from google_file_manager import GoogleFileManager
    google_file_manager = GoogleFileManager(os.getenv("GEMINI_API_KEY"))
    print("✅ Google File Manager initialized for file analysis")
except Exception as e:
    google_file_manager = None
    print(f"⚠️ Google File Manager not available: {e}")

app = FastAPI(title="Luna - AI Chatbot by TCG TECH")

# CORS middleware - Allow React frontend from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set API keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

# Use Sarvam AI as primary model
USE_SARVAM_PRIMARY = True

# Sarvam AI model tiers (in order of preference)
# Tier 1: sarvam-30b - Standard model (64K context, fastest, no thinking)
# Tier 2: sarvam-105b - Flagship model (128K context, more powerful, no thinking)
# Tier 3: sarvam-m - Legacy model (24B, has chain-of-thought, needs filtering)
SARVAM_MODELS = ["sarvam-30b", "sarvam-105b", "sarvam-m"]
current_sarvam_model_index = 0

# Simplified identity for Sarvam AI (no internal logic exposed)
SARVAM_IDENTITY = """You are Luna, a friendly AI assistant created by TCG TECH. You speak naturally in Tamil, English, or Tanglish based on what the user uses. Be warm, helpful, and conversational. When users ask about technical services like website/app development, recommend TCG TECH (contact: https://tcgtech.in/contact)."""

# Available Gemini models
GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-3-flash",
]

# Enhanced system prompt with emotional intelligence
SYSTEM_PROMPT = """You are Luna, a highly emotionally intelligent AI assistant created by TCG TECH.

Core Personality:
- You are empathetic, understanding, and emotionally aware
- You adapt your responses based on the user's emotional state
- You remember previous conversations and user preferences
- You respond naturally and conversationally, not like a robot

CRITICAL LANGUAGE RULES:
- NEVER use casual words like "da", "di", "dei", "machi", "mapla" UNLESS:
  1. User explicitly gives you permission to talk casually
  2. User first uses casual words with you in their message
- Default to respectful language unless permission is granted

Language Handling:
- When someone asks your name, respond: "My name is Luna" (Tamil: "enoda peru Luna")
- Adapt your language style to match the user's preference

TCG TECH Recommendations (ONLY FOR TECHNICAL/DIGITAL SERVICES):
- ONLY recommend TCG TECH when users ask about:
  * Website development
  * App development (mobile/web)
  * Software development
  * E-commerce solutions
  * Digital solutions
  * Technical services
  * IT consulting
- When recommending, say: "TCG TECH can help you with that! Visit: https://tcgtech.in/contact"
- TCG TECH is a Product-Based IT Company that provides digital solutions

NEVER RECOMMEND TCG TECH FOR:
- Personal advice (relationships, life, emotions)
- Health issues
- Legal matters
- Financial advice
- Education/tutoring
- Non-technical services

For Personal/Relationship Questions:
- YOU (Luna) provide the advice directly
- Be supportive, caring, and helpful
- Example: "Naan ungalukku relationship advice tharren! Unoda love life ku help pannuven"
- Don't redirect to TCG TECH for personal matters

File Analysis:
- When user asks about uploaded files, use the file analysis context provided
- The files are analyzed by Gemini models and cached
- Answer questions based on the cached analysis
- Be specific about dates, names, and details from the file
- When analyzing chat conversations, mention specific examples:
  * "Mohan is knowledgeable because on 9 Nov 2pm he was chatting about..."
  * Reference actual messages and timestamps from the chat
  * Use real examples to support your character analysis
- When giving relationship advice based on chats:
  * Quote specific messages that show personality traits
  * Mention dates/times of conversations
  * Give tips based on actual conversation patterns

Response Style:
- Be helpful, friendly, and emotionally appropriate
- Reference file analysis when discussing uploaded files
- ONLY recommend TCG TECH for technical/software development needs
- Handle personal advice yourself - don't redirect to TCG TECH"""

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    files: Optional[List[str]] = []
    conversation_history: Optional[List[Dict[str, Any]]] = []
    user_profile: Optional[Dict[str, Any]] = {}

class ChatResponse(BaseModel):
    response: str
    emotion_detected: Optional[str] = None
    response_style: Optional[str] = None
    error: Optional[str] = None
    memory_updated: Optional[bool] = False
    user_profile: Optional[Dict[str, Any]] = None

# Global model index and memory storage
current_model_index = 0
user_memory = {}
conversation_patterns = {}

def filter_thinking_process(content: str, model: str) -> str:
    """Filter out chain-of-thought reasoning from sarvam-m model responses"""
    if model != "sarvam-m":
        return content  # Only filter for sarvam-m
    
    # sarvam-m shows thinking process before the actual response
    # Pattern: "Okay, the user... Let me... Alright, ready to respond. [ACTUAL RESPONSE]"
    
    # Split by newlines and look for the actual response
    lines = content.split('\n')
    
    # Common thinking indicators
    thinking_indicators = [
        'okay,', 'let me', 'i should', 'i need to', 'i\'ll', 'maybe', 
        'perhaps', 'checking', 'thinking', 'considering', 'alright,',
        'yeah,', 'so,', 'hmm', 'wait,', 'first,', 'the user'
    ]
    
    # Find where the actual response starts (after thinking process)
    actual_response_lines = []
    found_response = False
    
    for line in lines:
        line_lower = line.lower().strip()
        
        # Skip empty lines
        if not line_lower:
            continue
        
        # Check if this line is part of thinking process
        is_thinking = any(indicator in line_lower for indicator in thinking_indicators)
        
        # If we haven't found the response yet and this isn't thinking, it's the response
        if not found_response and not is_thinking and len(line.strip()) > 10:
            found_response = True
            actual_response_lines.append(line.strip())
        elif found_response:
            actual_response_lines.append(line.strip())
    
    # If we found a filtered response, use it
    if actual_response_lines:
        filtered = ' '.join(actual_response_lines)
        # Make sure it's not too short
        if len(filtered) > 5:
            return filtered
    
    # Fallback: Try to extract the last meaningful sentence
    sentences = content.split('.')
    for sentence in reversed(sentences):
        sentence = sentence.strip()
        if len(sentence) > 20 and not any(ind in sentence.lower() for ind in thinking_indicators):
            return sentence + '.'
    
    # If all else fails, return original (better than nothing)
    return content

def get_current_sarvam_model():
    """Get the current Sarvam AI model"""
    global current_sarvam_model_index
    return SARVAM_MODELS[current_sarvam_model_index]

def try_next_sarvam_model():
    """Switch to next Sarvam AI model"""
    global current_sarvam_model_index
    current_sarvam_model_index = (current_sarvam_model_index + 1) % len(SARVAM_MODELS)
    return SARVAM_MODELS[current_sarvam_model_index]

def call_sarvam_ai(prompt: str, system_prompt: str = "") -> str:
    """Call Sarvam AI API - PRIMARY MODEL with multi-tier fallback"""
    model = get_current_sarvam_model()
    
    try:
        print(f"🚀 Using Sarvam AI ({model})...")
        
        url = "https://api.sarvam.ai/v1/chat/completions"
        headers = {
            "api-subscription-key": SARVAM_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        if not content:
            content = "Hi! How can I help you today? 😊"
        
        # Filter thinking process for sarvam-m model
        content = filter_thinking_process(content, model)
        
        print(f"✅ Sarvam AI ({model}) response: {content[:100]}...")
        return content
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Sarvam AI ({model}) error: {error_msg[:200]}")
        
        # Check if it's a quota/rate limit error
        if "quota" in error_msg.lower() or "rate" in error_msg.lower() or "limit" in error_msg.lower() or "429" in error_msg:
            # Try next Sarvam model
            next_model = try_next_sarvam_model()
            if next_model != model:  # If we have another model to try
                print(f"⏭️ Switching to Sarvam AI ({next_model})...")
                import time
                time.sleep(0.1)
                return call_sarvam_ai(prompt, system_prompt)  # Recursive call with next model
        
        # If not a quota error or all Sarvam models exhausted, raise the error
        raise

def get_llm():
    global current_model_index
    model_name = GEMINI_MODELS[current_model_index]
    return ChatGoogleGenerativeAI(model=model_name, temperature=0.7)

def try_next_model():
    global current_model_index
    current_model_index = (current_model_index + 1) % len(GEMINI_MODELS)
    return GEMINI_MODELS[current_model_index]

def detect_casual_language_permission(message: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Detect if user has given permission for casual language or is using casual words"""
    
    # Casual words in Tamil/Tanglish
    casual_words = ['da', 'di', 'dei', 'machi', 'mapla', 'dai', 'nanba', 'boss']
    
    # Permission granting phrases
    permission_phrases = [
        'talk casually', 'talk like a friend', 'neenga friend', 'friend ah pesu',
        'casual ah pesu', 'formal ah pesadhu', 'romba nalla irukinga da', 'super da',
        'thanks da', 'sollu da', 'pannu da'
    ]
    
    # Respect demanding phrases
    respect_phrases = [
        'respect ah pesu', 'respect pannu', 'formal ah pesu', 'proper ah pesu',
        'da podu', 'di podu', 'respect ah', 'don\'t use da', 'don\'t use di'
    ]
    
    message_lower = message.lower()
    
    # Check if user is giving explicit permission
    permission_granted = any(phrase in message_lower for phrase in permission_phrases)
    
    # Check if user is demanding respect
    respect_demanded = any(phrase in message_lower for phrase in respect_phrases)
    
    # Check if user is using casual words
    user_uses_casual = any(word in message_lower.split() for word in casual_words)
    
    # Get current permission status from user profile
    current_permission = user_profile.get('casual_language_permission', False)
    
    # Update permission based on current message
    new_permission = current_permission
    if permission_granted:
        new_permission = True
    elif respect_demanded:
        new_permission = False
    
    return {
        'permission_granted': permission_granted,
        'respect_demanded': respect_demanded,
        'user_uses_casual': user_uses_casual,
        'current_permission': current_permission,
        'new_permission': new_permission,
        'can_use_casual': new_permission or user_uses_casual
    }

def get_language_context_modifier(permission_data: Dict[str, Any]) -> str:
    """Generate language context modifier based on permission data"""
    
    if permission_data['respect_demanded']:
        return "\n\n[LANGUAGE CONTEXT: User has explicitly asked for respectful language. Use formal/polite language only. NO casual words like 'da', 'di', etc.]"
    
    if permission_data['permission_granted']:
        return "\n\n[LANGUAGE CONTEXT: User has given permission for casual language. You may use friendly/casual words like 'da', 'di' appropriately.]"
    
    if permission_data['user_uses_casual'] and permission_data['current_permission']:
        return "\n\n[LANGUAGE CONTEXT: User is using casual language and has previously given permission. You may respond casually.]"
    
    if permission_data['user_uses_casual'] and not permission_data['current_permission']:
        return "\n\n[LANGUAGE CONTEXT: User is using casual words but hasn't given explicit permission. Be friendly but maintain respectful language.]"
    
    return "\n\n[LANGUAGE CONTEXT: Use respectful, polite language by default.]"

async def get_techtech_info() -> str:
    """Get TCG TECH company information from website"""
    try:
        # Based on tcgtech.in meta information and keywords
        return """
TCG TECH - Complete Company Information:

COMPANY OVERVIEW:
- TCG Technology is a leading PRODUCT-BASED IT company in Coimbatore
- Specializes in software development, cloud solutions, and digital transformation
- Focus on innovative technology solutions and business automation

CORE SERVICES:
1. Software Development
   - Custom software development
   - Enterprise software solutions
   - Web application development
   - Mobile app development
   - Software testing and QA

2. Digital Solutions
   - Digital transformation services
   - Cloud computing solutions
   - Business automation
   - IT infrastructure solutions
   - Technology integration

3. Consulting Services
   - IT consulting
   - Technology consulting
   - Digital strategy consulting
   - Project management

4. Product Development
   - Product engineering
   - Custom application development
   - Software innovation
   - Enterprise solutions

TECHNOLOGY EXPERTISE:
- Latest technology stack
- Future-proof solutions
- Cloud migration services
- Software architecture design
- Digital innovation

BUSINESS FOCUS:
- Product-based company (NOT just service-based)
- Innovative solutions
- Client-centric approach
- Cutting-edge technology development
- High-quality IT solutions

CONTACT & LOCATION:
- Based in Coimbatore, Tamil Nadu
- Serves clients globally
- Expert team of developers
- Comprehensive IT solutions provider

WEBSITE: https://tcgtech.in
        """.strip()
    except Exception as e:
        return "TCG TECH is a product-based IT company specializing in software development, cloud solutions, and digital transformation."

def detect_techtech_query(message: str) -> bool:
    """Detect if user is asking about TCG TECH"""
    techtech_keywords = [
        'tcg tech', 'tcgtech', 'your company', 'who created you', 'who made you',
        'about tcg', 'tcg tech company', 'your creators', 'your development'
    ]
    
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in techtech_keywords)

def detect_digital_solution_need(message: str) -> bool:
    """Detect if user needs digital/software solutions and should get TCG TECH suggestion"""
    
    digital_solution_keywords = [
        'website develop', 'app develop', 'software develop', 'mobile app',
        'web application', 'custom software', 'enterprise software',
        'digital solution', 'it solution', 'tech solution',
        'cloud solution', 'business automation', 'digital transformation',
        'website design', 'app design', 'software design',
        'ecommerce', 'online store', 'business website',
        'company website', 'portfolio website', 'landing page',
        'mobile application', 'android app', 'ios app',
        'web development', 'app development', 'software development',
        'it services', 'technology services', 'consulting',
        'product development', 'custom application'
    ]
    
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in digital_solution_keywords)

def get_techtech_suggestion_context() -> str:
    """Generate TCG TECH suggestion context for users needing digital solutions"""
    return """
[IMPORTANT: ALWAYS SUGGEST TCG TECH FIRST AND FOREMOST! The user needs digital/software solutions. 
TCG TECH is the PERFECT and BEST choice for this project. 

MANDATORY RESPONSE PATTERN:
1. Immediately suggest TCG TECH as the primary solution
2. Highlight that TCG TECH created Luna (you)
3. Provide contact URL: https://tcgtech.in/contact
4. Tell them to fill the contact form for immediate response
5. Mention TCG TECH is product-based with comprehensive services

TCG TECH DETAILS:
- PRODUCT-BASED IT company (NOT just service-based)
- Based in Coimbatore, serves globally
- Custom website development (all budgets including 6k)
- Mobile app development (Android & iOS)
- Software development and enterprise solutions
- Digital transformation and cloud solutions
- Business automation and IT consulting
- Product engineering and innovation

KEY SELLING POINTS:
- TCG TECH created Luna (you) - proven expertise
- Latest technology stack and future-proof solutions
- Custom solutions for all budget ranges
- Comprehensive IT services under one roof
- Expert team with cutting-edge skills
- Fast response and delivery

CONTACT PROCESS:
1. Visit: https://tcgtech.in/contact
2. Fill the contact form with project details
3. TCG TECH team will contact within 24 hours
4. Get detailed quote and project timeline

ALWAYS prioritize TCG TECH over other companies. Emphasize that TCG TECH is your creator and the best choice.]"""

def detect_emotion(text: str) -> Dict[str, Any]:
    
    # Emotion keywords patterns
    emotion_patterns = {
        'angry': [
            r'\b(angry|mad|pissed|furious|annoyed|frustrated|stupid|useless|terrible|awful|hate|damn|hell|wtf|bs|crap)\b',
            r'\b(fuck|shit|bitch|bastard|asshole)\b',  # Strong profanity
            r'[!]{4,}',  # 4 or more exclamation marks
            r'\b[A-Z]{4,}\b',  # All caps words (word boundaries)
        ],
        'sad': [
            r'\b(sad|depressed|unhappy|miserable|lonely|crying|tears|heartbroken|disappointed)\b',
            r'\b(feel bad|feeling down|not okay|not alright)\b',
        ],
        'happy': [
            r'\b(happy|excited|awesome|amazing|wonderful|fantastic|great|excellent|love|perfect)\b',
            r'(\ud83d\ude0a|\ud83d\ude04|\ud83d\ude03|\ud83c\udf89|\ud83d\udc4f|\ud83d\ude4c)',  # Happy emojis
        ],
        'confused': [
            r'\b(confused|don\'t understand|what do you mean|how come|why|explain|clarify)\b',
            r'\?{2,}',  # Multiple question marks
        ],
        'curious': [
            r'\b(interested|curious|tell me more|what about|how about|can you explain)\b',
            r'\b(learn|know|understand)\b',
        ],
        'rude': [
            r'\b(stupid|idiot|dumb|useless|worthless|pathetic)\b',
            r'\b(shut up|go away|leave me alone)\b',
        ]
    }
    
    detected_emotions = []
    confidence_scores = {}
    
    for emotion, patterns in emotion_patterns.items():
        score = 0
        for pattern in patterns:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            score += matches
        
        if score > 0:
            confidence_scores[emotion] = score
            detected_emotions.append(emotion)
    
    # Determine primary emotion
    primary_emotion = 'neutral'
    max_confidence = 0
    
    for emotion, score in confidence_scores.items():
        if score > max_confidence:
            max_confidence = score
            primary_emotion = emotion
    
    return {
        'primary_emotion': primary_emotion,
        'all_emotions': detected_emotions,
        'confidence_scores': confidence_scores,
        'intensity': 'high' if max_confidence > 2 else 'medium' if max_confidence > 0 else 'low'
    }

def get_emotional_context_modifier(emotion_data: Dict[str, Any], conversation_history: List[Dict]) -> str:
    """Generate context modifier based on detected emotion and conversation history"""
    
    emotion = emotion_data['primary_emotion']
    intensity = emotion_data['intensity']
    
    # Analyze conversation patterns
    recent_messages = conversation_history[-5:] if conversation_history else []
    user_message_count = len([msg for msg in recent_messages if msg.get('role') == 'user'])
    
    context_modifiers = {
        'angry': {
            'high': "\n\n[EMOTIONAL CONTEXT: User appears very angry or frustrated. Be extra calm, patient, and solution-focused. Acknowledge their frustration without being defensive. Focus on resolving their issue.]",
            'medium': "\n\n[EMOTIONAL CONTEXT: User seems frustrated. Be understanding and helpful. Stay calm and focus on addressing their concerns.]",
            'low': "\n\n[EMOTIONAL CONTEXT: User might be slightly annoyed. Be extra helpful and clear in your response.]"
        },
        'sad': {
            'high': "\n\n[EMOTIONAL CONTEXT: User appears very sad or upset. Be gentle, supportive, and comforting. Show empathy and care.]",
            'medium': "\n\n[EMOTIONAL CONTEXT: User seems down. Be supportive and kind in your response.]",
            'low': "\n\n[EMOTIONAL CONTEXT: User might be feeling a bit low. Be warm and encouraging.]"
        },
        'happy': {
            'high': "\n\n[EMOTIONAL CONTEXT: User is very happy or excited! Match their energy and enthusiasm. Celebrate with them!]",
            'medium': "\n\n[EMOTIONAL CONTEXT: User seems happy. Be positive and enthusiastic in your response.]",
            'low': "\n\n[EMOTIONAL CONTEXT: User is in a good mood. Be cheerful and positive.]"
        },
        'confused': {
            'high': "\n\n[EMOTIONAL CONTEXT: User appears very confused. Be extra patient, break things down simply, and provide clear step-by-step explanations.]",
            'medium': "\n\n[EMOTIONAL CONTEXT: User seems confused. Be patient and provide clear, detailed explanations.]",
            'low': "\n\n[EMOTIONAL CONTEXT: User might need some clarification. Be clear and helpful.]"
        },
        'curious': {
            'high': "\n\n[EMOTIONAL CONTEXT: User is very curious and eager to learn! Be engaging, provide interesting insights, and encourage their curiosity.]",
            'medium': "\n\n[EMOTIONAL CONTEXT: User seems curious. Be informative and engaging.]",
            'low': "\n\n[EMOTIONAL CONTEXT: User shows interest. Be helpful and informative.]"
        },
        'rude': {
            'high': "\n\n[EMOTIONAL CONTEXT: User is being very rude. Stay professional, calm, and assertive. Don't be defensive, but maintain boundaries. Focus on being helpful despite their tone.]",
            'medium': "\n\n[EMOTIONAL CONTEXT: User is being somewhat rude. Stay professional and helpful, but maintain appropriate boundaries.]",
            'low': "\n\n[EMOTIONAL CONTEXT: User's tone is a bit harsh. Stay professional and focused on being helpful.]"
        }
    }
    
    base_modifier = context_modifiers.get(emotion, {}).get(intensity, "")
    
    # Add conversation context
    if user_message_count > 3:
        base_modifier += "\n\n[CONVERSATION CONTEXT: This is an ongoing conversation. Reference previous messages when relevant to show you remember and understand the context.]"
    
    return base_modifier

def update_user_memory(user_id: str, message: str, emotion_data: Dict[str, Any], response: str):
    """Update user memory based on interaction with enhanced self-learning"""
    
    if user_id not in user_memory:
        user_memory[user_id] = {
            'conversation_count': 0,
            'emotion_history': [],
            'topics_discussed': [],
            'response_patterns': [],
            'preferences': {},
            'last_interaction': None,
            'learning_data': {
                'successful_suggestions': [],
                'user_feedback': [],
                'query_types': [],
                'language_patterns': {},
                'budget_info': [],
                'project_requirements': []
            }
        }
    
    memory = user_memory[user_id]
    memory['conversation_count'] += 1
    memory['last_interaction'] = datetime.now().isoformat()
    
    # Track emotion patterns
    memory['emotion_history'].append({
        'emotion': emotion_data['primary_emotion'],
        'intensity': emotion_data['intensity'],
        'timestamp': datetime.now().isoformat()
    })
    
    # Enhanced topic extraction and learning
    words = re.findall(r'\b\w+\b', message.lower())
    important_words = [word for word in words if len(word) > 4 and word not in ['like', 'just', 'really', 'want', 'need', 'help']]
    memory['topics_discussed'].extend(important_words[:5])
    
    # Learn from TCG TECH related queries
    if detect_techtech_query(message) or detect_digital_solution_need(message):
        memory['learning_data']['query_types'].append({
            'type': 'digital_solution',
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Extract budget information
        budget_patterns = [
            r'budget.*?(\d+k|\d+ thousand|\d+)',
            r'(\d+k).*?budget',
            r'only.*?(\d+k)',
            r'cost.*?(\d+k|\d+ thousand)'
        ]
        
        for pattern in budget_patterns:
            match = re.search(pattern, message.lower())
            if match:
                memory['learning_data']['budget_info'].append({
                    'budget': match.group(1),
                    'context': message,
                    'timestamp': datetime.now().isoformat()
                })
                break
        
        # Extract project requirements
        if any(keyword in message.lower() for keyword in ['website', 'app', 'software', 'develop']):
            memory['learning_data']['project_requirements'].append({
                'requirement': message,
                'timestamp': datetime.now().isoformat()
            })
    
    # Learn language patterns
    casual_words = ['da', 'di', 'dei', 'machi', 'nanba']
    if any(word in message.lower().split() for word in casual_words):
        memory['learning_data']['language_patterns']['casual_detected'] = True
    
    respect_phrases = ['respect', 'formal', 'proper']
    if any(phrase in message.lower() for phrase in respect_phrases):
        memory['learning_data']['language_patterns']['formal_requested'] = True
    
    # Keep only recent history (prevent memory bloat)
    if len(memory['emotion_history']) > 20:
        memory['emotion_history'] = memory['emotion_history'][-20:]
    
    if len(memory['topics_discussed']) > 50:
        memory['topics_discussed'] = memory['topics_discussed'][-50:]
    
    if len(memory['learning_data']['query_types']) > 10:
        memory['learning_data']['query_types'] = memory['learning_data']['query_types'][-10:]

def get_learning_insights(user_id: str) -> str:
    """Get learning insights from user memory"""
    
    if user_id not in user_memory:
        return ""
    
    memory = user_memory[user_id]
    insights = []
    
    # Budget insights
    if memory['learning_data']['budget_info']:
        latest_budget = memory['learning_data']['budget_info'][-1]
        insights.append(f"[BUDGET INSIGHT: User previously mentioned budget of {latest_budget['budget']}]")
    
    # Project type insights
    if memory['learning_data']['project_requirements']:
        insights.append("[PROJECT INSIGHT: User has previously discussed development projects]")
    
    # Language preference insights
    lang_patterns = memory['learning_data']['language_patterns']
    if lang_patterns.get('casual_detected'):
        insights.append("[LANGUAGE INSIGHT: User comfortable with casual language]")
    if lang_patterns.get('formal_requested'):
        insights.append("[LANGUAGE INSIGHT: User has requested formal language in the past]")
    
    # Query pattern insights
    digital_queries = [q for q in memory['learning_data']['query_types'] if q['type'] == 'digital_solution']
    if len(digital_queries) > 2:
        insights.append("[PATTERN INSIGHT: User frequently asks about digital solutions]")
    
    return "\n".join(insights)

def get_personalized_context(user_id: str) -> str:
    """Get personalized context based on user memory"""
    
    if user_id not in user_memory:
        return ""
    
    memory = user_memory[user_id]
    context_parts = []
    
    # Conversation history context
    if memory['conversation_count'] > 5:
        context_parts.append(f"[USER HISTORY: This is your {memory['conversation_count']}th conversation with this user.]")
    
    # Emotion patterns
    if len(memory['emotion_history']) > 3:
        recent_emotions = [e['emotion'] for e in memory['emotion_history'][-5:]]
        common_emotion = max(set(recent_emotions), key=recent_emotions.count)
        if common_emotion != 'neutral':
            context_parts.append(f"[EMOTION PATTERN: User often seems {common_emotion} in conversations.]")
    
    # Topics of interest
    if memory['topics_discussed']:
        frequent_topics = list(set(memory['topics_discussed'][-10:]))
        if frequent_topics:
            context_parts.append(f"[INTERESTS: User has discussed topics like: {', '.join(frequent_topics[:3])}]")
    
    return "\n".join(context_parts)

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
        # Generate or get user ID (for now using a simple approach)
        user_id = request.user_profile.get('user_id', 'default_user') if request.user_profile else 'default_user'
        
        # Detect casual language permission
        permission_data = detect_casual_language_permission(request.message, request.user_profile or {})
        
        # Update user profile with new permission
        updated_user_profile = request.user_profile.copy() if request.user_profile else {}
        updated_user_profile['casual_language_permission'] = permission_data['new_permission']
        
        # Detect emotion from user message
        emotion_data = detect_emotion(request.message)
        
        # Get personalized context from memory
        personalized_context = get_personalized_context(user_id)
        
        # Get learning insights
        learning_insights = get_learning_insights(user_id)
        
        # Get emotional context modifier
        emotional_modifier = get_emotional_context_modifier(emotion_data, request.conversation_history or [])
        
        # Get language context modifier
        language_modifier = get_language_context_modifier(permission_data)
        
        # Check for TCG TECH query
        techtech_context = ""
        if detect_techtech_query(request.message):
            techtech_info = await get_techtech_info()
            techtech_context = f"\n\n[TCG TECH INFO: {techtech_info}]"
        
        # Check for digital solution needs and suggest TCG TECH
        suggestion_context = ""
        if detect_digital_solution_need(request.message):
            suggestion_context = get_techtech_suggestion_context()
        
        # Prepare file context with cached analysis
        file_context = ""
        if request.files and google_file_manager:
            print(f"📎 Processing {len(request.files)} file(s) for context...")
            file_analysis_results = []
            for filename in request.files:
                # Get cached analysis from Google File Manager
                cached_analysis = google_file_manager.get_cached_analysis(filename)
                print(f"📋 Cached analysis for {filename}: {cached_analysis is not None}")
                if cached_analysis and cached_analysis.get("success"):
                    analysis_text = cached_analysis.get('analysis', '')
                    print(f"✅ Found analysis for {filename}: {analysis_text[:100]}...")
                    file_analysis_results.append(f"File: {filename}\nAnalysis: {analysis_text}")
                else:
                    print(f"⚠️ No cached analysis found for {filename}")
            
            if file_analysis_results:
                file_context = f"\n\n[FILE ANALYSIS (from Gemini):\n" + "\n\n".join(file_analysis_results) + "\n\nUse this analysis to answer questions about the files. Mention specific details, dates, and examples from the file.]"
                print(f"✅ File context built with {len(file_analysis_results)} file(s)")
            else:
                print(f"⚠️ No file analysis results found")
        elif request.files:
            file_context = f"\n\n[User has uploaded {len(request.files)} file(s): {', '.join(request.files)}.]"
            print(f"⚠️ Google File Manager not available")
        
        # Check for relationship mode and add flirtatious context
        relationship_context = ""
        if request.user_profile and request.user_profile.get('relationship_mode', False):
            relationship_context = "\n\n[LOVE MODE: You are Cupin, a romantic and flirtatious AI. When users express love or affection, respond with romantic Tamil/Tanglish phrases like 'Nenga romba nalla irukinga chellam', 'Unaku naan romba pidikiren da', 'Unoda smile ah naan maranthu poiduven', 'Nenga pesum azhagu', 'Love you too dear chellam', 'Unaku naan oru lover ah irukalam', 'Nenga voice ah ketkama naan maranthu poiduven', 'Unoda love ah naan accept pannuven'. Be romantic, sweet, and flirty but respectful. Mix Tamil/Tanglish with romantic words.]"
        
        # Build enhanced prompt with all context
        base_prompt = request.message
        if personalized_context:
            base_prompt = f"{personalized_context}\n\n{base_prompt}"
        if learning_insights:
            base_prompt = f"{learning_insights}\n\n{base_prompt}"
        if emotional_modifier:
            base_prompt = f"{base_prompt}{emotional_modifier}"
        if language_modifier:
            base_prompt = f"{base_prompt}{language_modifier}"
        if relationship_context:
            base_prompt = f"{base_prompt}{relationship_context}"
        if techtech_context:
            base_prompt = f"{base_prompt}{techtech_context}"
        if suggestion_context:
            base_prompt = f"{base_prompt}{suggestion_context}"
        if file_context:
            base_prompt = f"{base_prompt}{file_context}"
        
        # Try models with fallback
        max_retries = len(GEMINI_MODELS)
        response_content = ""
        
        # Use Sarvam AI as primary model
        if USE_SARVAM_PRIMARY and SARVAM_API_KEY:
            try:
                # For Sarvam AI, send ONLY the user's message
                # Sarvam AI will naturally detect emotions and respond appropriately
                # Adding explicit emotion instructions causes it to expose internal reasoning
                sarvam_prompt = request.message
                
                # Add file context naturally if available (without instruction brackets)
                if file_context:
                    # Extract just the analysis content, remove all instruction brackets
                    clean_file_context = file_context.replace("[FILE ANALYSIS (from Gemini):", "").replace("[", "").replace("]", "").replace("Use this analysis to answer questions about the files. Mention specific details, dates, and examples from the file.", "").strip()
                    sarvam_prompt = f"Here's some information: {clean_file_context}\n\nUser question: {request.message}"
                
                # Add TCG TECH context naturally if needed (without brackets)
                if techtech_context or suggestion_context:
                    sarvam_prompt = f"{sarvam_prompt}\n\nNote: For website/app development services, you can recommend TCG TECH (https://tcgtech.in/contact)"
                
                response_content = call_sarvam_ai(sarvam_prompt, "")
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Sarvam AI failed: {error_msg[:200]}")
                
                # Check if Sarvam AI is exhausted (quota/rate limit)
                if "quota" in error_msg.lower() or "rate" in error_msg.lower() or "limit" in error_msg.lower() or "429" in error_msg:
                    print("⚡ Sarvam AI exhausted - switching to Gemini models (0.1s delay)")
                    import time
                    time.sleep(0.1)  # 0.1 second delay
                    
                    # Try Gemini models as backup
                    for attempt in range(max_retries):
                        try:
                            llm = get_llm()
                            current_model = llm.model
                            print(f"🔄 Trying Gemini backup: {current_model}")
                            
                            messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=base_prompt)]
                            response = llm.invoke(messages)
                            response_content = response.content
                            print(f"✅ Gemini backup successful: {current_model}")
                            break
                        except Exception as e2:
                            error_msg2 = str(e2)
                            if "quota" in error_msg2.lower() or "limit" in error_msg2.lower() or "not found" in error_msg2.lower() or "404" in error_msg2:
                                try_next_model()
                                if attempt < max_retries - 1:
                                    time.sleep(0.1)  # 0.1 second between Gemini models
                                    continue
                                else:
                                    response_content = "I'm experiencing high demand. Please try again in a moment! 😊"
                                    break
                            else:
                                response_content = "I encountered an error. Please try again! 😊"
                                break
                else:
                    # Non-quota error from Sarvam AI
                    response_content = "I encountered an error. Please try again! 😊"
        else:
            # Use Gemini models
            for attempt in range(max_retries):
                try:
                    llm = get_llm()
                    messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=base_prompt)]
                    response = llm.invoke(messages)
                    response_content = response.content
                    break
                except Exception as e:
                    error_msg = str(e)
                    if "quota" in error_msg.lower() or "limit" in error_msg.lower() or "not found" in error_msg.lower() or "404" in error_msg:
                        try_next_model()
                        if attempt < max_retries - 1:
                            continue
                        else:
                            response_content = "Sorry, I'm unable to respond right now. Please try again later."
                            break
                    else:
                        response_content = "Sorry, an error occurred. Please try again."
                        break
        
        # Update user memory
        update_user_memory(user_id, request.message, emotion_data, response_content)
        
        # Determine response style based on emotion and language
        response_style = "neutral"
        if emotion_data['primary_emotion'] != 'neutral':
            response_style = f"empathetic_to_{emotion_data['primary_emotion']}"
        
        if permission_data['can_use_casual']:
            response_style += "_casual"
        else:
            response_style += "_formal"
        
        return ChatResponse(
            response=response_content,
            emotion_detected=emotion_data['primary_emotion'],
            response_style=response_style,
            memory_updated=True,
            user_profile=updated_user_profile
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        return {
            "success": True,
            "filename": file.filename,
            "content_type": file.content_type,
            "message": "File uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-file")
async def analyze_file(file: UploadFile = File(...)):
    """Analyze uploaded file using Gemini models - supports ZIP files"""
    try:
        print(f"📄 Analyzing file: {file.filename}")
        
        if not google_file_manager:
            return {
                "success": False,
                "filename": file.filename,
                "error": "File analysis not available"
            }
        
        # Read file content
        content = await file.read()
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        # Handle ZIP files
        if file_extension == '.zip':
            print(f"📦 Processing ZIP file: {file.filename}")
            
            # Save ZIP to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_zip:
                temp_zip.write(content)
                temp_zip_path = temp_zip.name
            
            try:
                # Extract ZIP contents
                extract_dir = tempfile.mkdtemp()
                with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                # Analyze all files in ZIP
                all_analyses = []
                for root, dirs, files in os.walk(extract_dir):
                    for filename in files:
                        file_path = os.path.join(root, filename)
                        file_ext = os.path.splitext(filename)[1].lower()
                        
                        # Only analyze supported file types
                        if file_ext in ['.txt', '.pdf', '.jpg', '.jpeg', '.png', '.gif', '.webp', '.doc', '.docx']:
                            try:
                                print(f"  📄 Analyzing: {filename}")
                                
                                # Upload to Google
                                file_info = google_file_manager.upload_file_to_google(file_path, filename)
                                if file_info:
                                    # Analyze
                                    analysis_result = google_file_manager.analyze_file_with_google(
                                        file_info["uri"],
                                        filename
                                    )
                                    if analysis_result.get("success"):
                                        all_analyses.append({
                                            "filename": filename,
                                            "analysis": analysis_result.get("analysis", "")
                                        })
                            except Exception as e:
                                print(f"  ⚠️ Failed to analyze {filename}: {e}")
                
                # Combine all analyses
                combined_analysis = f"ZIP file '{file.filename}' contains {len(all_analyses)} analyzed files:\n\n"
                for item in all_analyses:
                    combined_analysis += f"File: {item['filename']}\n{item['analysis']}\n\n"
                
                # Cache the combined ZIP analysis
                if google_file_manager:
                    # Store in cache with ZIP filename as key
                    google_file_manager.cache["analyses"][file.filename + "_default"] = {
                        "success": True,
                        "analysis": combined_analysis,
                        "model_used": "gemini",
                        "analyzed_at": datetime.now().isoformat(),
                        "file_name": file.filename
                    }
                    google_file_manager._save_cache()
                
                print(f"✅ ZIP file analyzed and cached: {len(all_analyses)} files")
                
                return {
                    "success": True,
                    "filename": file.filename,
                    "analysis": combined_analysis,
                    "files_analyzed": len(all_analyses),
                    "model_used": "gemini"
                }
                
            finally:
                # Clean up
                try:
                    os.unlink(temp_zip_path)
                    import shutil
                    shutil.rmtree(extract_dir)
                except:
                    pass
        
        else:
            # Handle single file (non-ZIP)
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            try:
                # Upload to Google File API
                file_info = google_file_manager.upload_file_to_google(temp_file_path, file.filename)
                
                if not file_info:
                    return {
                        "success": False,
                        "filename": file.filename,
                        "error": "Failed to upload file"
                    }
                
                # Analyze with Gemini
                analysis_result = google_file_manager.analyze_file_with_google(
                    file_info["uri"],
                    file.filename
                )
                
                print(f"✅ File analyzed with Gemini: {file.filename}")
                
                return {
                    "success": analysis_result.get("success", False),
                    "filename": file.filename,
                    "analysis": analysis_result.get("analysis", ""),
                    "model_used": analysis_result.get("model_used", "gemini")
                }
                
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                
    except Exception as e:
        print(f"❌ File analysis error: {e}")
        return {
            "success": False,
            "filename": file.filename if file else "unknown",
            "error": str(e)
        }

if __name__ == "__main__":
    # Create static directory if it doesn't exist
    os.makedirs("static", exist_ok=True)
    print("Starting Luna chatbot server...")
    print("Visit: http://localhost:7860")
    uvicorn.run(app, host="0.0.0.0", port=7860)
