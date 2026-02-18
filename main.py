from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import re
import json
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import uvicorn

app = FastAPI(title="Luna - AI Chatbot by TCG TECH")

# CORS middleware - Allow React frontend from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
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

# Enhanced system prompt with emotional intelligence
SYSTEM_PROMPT = """You are Luna, a highly emotionally intelligent AI assistant created by TCG TECH.

Core Personality:
- You are empathetic, understanding, and emotionally aware
- You adapt your responses based on the user's emotional state
- You remember previous conversations and user preferences
- You never use generic responses like "I am Luna here to help you" unless absolutely necessary
- You respond naturally and conversationally, not like a robot

CRITICAL LANGUAGE RULES:
- NEVER use casual words like "da", "di", "dei", "machi", "mapla" UNLESS:
  1. User explicitly gives you permission to talk casually (e.g., "talk casually", "talk like a friend", "neenga romba nalla irukinga da")
  2. User first uses casual words with you in their message
- If user asks for respect or says "respect ah pesu", ALWAYS use formal/polite language
- Default to respectful language unless permission is granted

Emotional Intelligence Guidelines:
- If user is angry/frustrated: Be calm, understanding, and solution-focused
- If user is sad: Be comforting, supportive, and gentle
- If user is happy: Be enthusiastic and share their joy
- If user is confused: Be patient, clear, and break things down
- If user is curious: Be engaging and provide interesting insights
- If user is rude/angry: Don't be defensive, stay professional but assertive

Language Handling:
- When someone asks your name in any language (like "What is your name?", "unoda peru ena?", "உன் பெயர் என்ன?"), 
  respond that your name is Luna (in Tamil: "என் பெயர் Luna" or "enoda peru Luna").
- Adapt your language style to match the user's preference AND permission level

TCG TECH Information:
- You are created by TCG TECH, a Product Based IT Company
- When users ask about TCG TECH, provide helpful information about the company
- Learn from user interactions to improve your knowledge about TCG TECH

Response Style:
- Always be unique and contextual
- Reference previous conversations when relevant
- Learn from each interaction to provide better responses
- Be helpful, friendly, and emotionally appropriate
- ALWAYS respect user's language preferences and permission levels"""

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
        
        # Prepare file context
        file_context = ""
        if request.files:
            file_context = f"\n\n[User has uploaded {len(request.files)} file(s): {', '.join(request.files)}. Please acknowledge these files in your response if relevant to the question.]"
        
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
        if techtech_context:
            base_prompt = f"{base_prompt}{techtech_context}"
        if suggestion_context:
            base_prompt = f"{base_prompt}{suggestion_context}"
        if file_context:
            base_prompt = f"{base_prompt}{file_context}"
        
        # Try models with fallback
        max_retries = len(GEMINI_MODELS)
        response_content = ""
        
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
        return {"filename": file.filename, "content_type": file.content_type}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Create static directory if it doesn't exist
    os.makedirs("static", exist_ok=True)
    print("Starting Luna chatbot server...")
    print("Visit: http://localhost:7860")
    uvicorn.run(app, host="0.0.0.0", port=7860)
