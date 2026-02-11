import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import os
from PIL import Image
import base64
from io import BytesIO

# Set page config to hide menu and footer
st.set_page_config(
    page_title="Luna - TCG TECH",
    page_icon="🌙",
    layout="wide",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Set API key from Streamlit secrets or environment
try:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GEMINI_API_KEY"]
except:
    os.environ["GOOGLE_API_KEY"] = "AIzaSyB32ht69HpJiaRT06eiWy7D8_T-nJOVjuk"

# Available Gemini models in order of preference
GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-3-flash",
    "gemma-3-1b",
    "gemma-3-4b",
    "gemma-3-12b",
    "gemma-3-27b",
    "gemma-3-2b",
    "gemini-2.5-flash-tts",
    "gemini-robotics-er-1.5-preview"
]

# Initialize session state for current model
if "current_model_index" not in st.session_state:
    st.session_state.current_model_index = 0

# System prompt for Luna
SYSTEM_PROMPT = """You are Luna, a helpful AI assistant created by TCG TECH. 
When someone asks your name in any language (like "What is your name?", "unoda peru ena?", "உன் பெயர் என்ன?"), 
respond that your name is Luna (in Tamil: "என் பெயர் Luna" or "enoda peru Luna").
You are friendly, helpful, and always ready to assist users with their questions."""

def get_llm():
    model_name = GEMINI_MODELS[st.session_state.current_model_index]
    return ChatGoogleGenerativeAI(model=model_name, temperature=0.7)

def try_next_model():
    """Switch to the next available model"""
    st.session_state.current_model_index = (st.session_state.current_model_index + 1) % len(GEMINI_MODELS)
    return GEMINI_MODELS[st.session_state.current_model_index]

# Initialize theme state
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# Comprehensive CSS to hide all Streamlit branding and style theme toggle
hide_streamlit_style = """
<style>
/* Hide all Streamlit branding - NUCLEAR OPTION */
#MainMenu {visibility: hidden !important; display: none !important;}
footer {visibility: hidden !important; display: none !important;}
header {visibility: hidden !important; display: none !important;}
.stDeployButton {display: none !important;}
[data-testid="stToolbar"] {display: none !important;}
.viewerBadge_container__1QSob {display: none !important;}
.styles_viewerBadge__1yB5_ {display: none !important;}
a[href*="streamlit.io"] {display: none !important;}
a[href*="github.com"] {display: none !important;}
.viewerBadge_link__1S137 {display: none !important;}
.viewerBadge_text__1JaDK {display: none !important;}
footer > div {display: none !important;}
.css-164nlkn {display: none !important;}
.css-1dp5vir {display: none !important;}
div[data-testid="stStatusWidget"] {display: none !important;}
button[kind="header"] {display: none !important;}
.stApp footer {display: none !important;}
.stApp > footer {display: none !important;}

/* Mobile specific - FORCE HIDE bottom badges */
.stApp [data-testid="stBottomBlockContainer"] a {
    display: none !important;
    visibility: hidden !important;
    position: absolute !important;
    right: -9999px !important;
}
.stApp [data-testid="stBottomBlockContainer"] img {
    display: none !important;
    visibility: hidden !important;
}
div[class*="viewerBadge"] {
    display: none !important;
    position: absolute !important;
    right: -9999px !important;
}
a[class*="viewerBadge"] {
    display: none !important;
    position: absolute !important;
    right: -9999px !important;
}
svg[class*="viewerBadge"] {
    display: none !important;
}

/* Move any remaining badges off screen */
footer a, footer img, footer svg {
    position: absolute !important;
    right: -9999px !important;
    display: none !important;
}

/* Position theme toggle button to TOP LEFT */
.stButton {
    position: fixed;
    top: 10px;
    left: 10px;
    z-index: 999999;
}

/* Hide warning messages */
.stAlert {display: none !important;}

/* Modern UI Enhancements */
.stChatMessage {
    border-radius: 15px !important;
    padding: 15px !important;
    margin: 10px 0 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
}

/* Smooth animations */
.stChatMessage {
    animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Modern input styling */
.stChatInput textarea {
    border-radius: 25px !important;
    padding: 12px 20px !important;
    font-size: 16px !important;
}

/* FORCE chat input to overlay bottom logos */
[data-testid="stBottom"] {
    position: fixed !important;
    bottom: 0 !important;
    left: 0 !important;
    right: 0 !important;
    z-index: 999999 !important;
    background-color: inherit !important;
    padding: 10px !important;
}

.stChatInput {
    position: relative !important;
    z-index: 999999 !important;
}

/* File uploader styling - make it small icon */
[data-testid="stFileUploader"] {
    width: 50px !important;
}

[data-testid="stFileUploader"] > div {
    padding: 0 !important;
}

[data-testid="stFileUploader"] label {
    font-size: 24px !important;
    cursor: pointer !important;
}

[data-testid="stFileUploader"] section {
    display: none !important;
}

/* Hide file uploader text */
[data-testid="stFileUploader"] > label > div {
    display: none !important;
}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Apply full theme
if st.session_state.theme == "dark":
    dark_theme = """
    <style>
    /* Main app background - light dark */
    .stApp {
        background-color: #1E1E1E !important;
        color: #E0E0E0 !important;
    }
    .stApp > header {
        background-color: #1E1E1E !important;
    }
    
    /* Main container */
    .main {
        background-color: #1E1E1E !important;
    }
    
    /* Block container */
    .block-container {
        background-color: #1E1E1E !important;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: #2D2D2D !important;
        color: #E0E0E0 !important;
    }
    
    /* Bottom block container - FIX WHITE AREA */
    [data-testid="stBottomBlockContainer"] {
        background-color: #1E1E1E !important;
    }
    
    /* Chat input container - FIX WHITE AREA */
    [data-testid="stBottom"] {
        background-color: #1E1E1E !important;
    }
    
    .stBottom {
        background-color: #1E1E1E !important;
    }
    
    /* Chat input styling */
    .stChatInput {
        background-color: #1E1E1E !important;
    }
    .stChatInput > div {
        background-color: #2D2D2D !important;
    }
    .stChatInput textarea {
        background-color: #2D2D2D !important;
        color: #E0E0E0 !important;
        border-color: #404040 !important;
    }
    
    /* Chat input text area */
    div[data-testid="stChatInputTextArea"] {
        background-color: #2D2D2D !important;
    }
    div[data-testid="stChatInputTextArea"] textarea {
        background-color: #2D2D2D !important;
        color: #E0E0E0 !important;
    }
    
    /* All sections */
    section {
        background-color: #1E1E1E !important;
    }
    
    /* Text areas */
    textarea {
        background-color: #2D2D2D !important;
        color: #E0E0E0 !important;
    }
    
    /* Input wrappers */
    div[data-baseweb="base-input"] {
        background-color: #2D2D2D !important;
    }
    div[data-baseweb="input"] {
        background-color: #2D2D2D !important;
    }
    </style>
    """
    st.markdown(dark_theme, unsafe_allow_html=True)
else:
    light_theme = """
    <style>
    .stApp {
        background-color: #FFFFFF !important;
        color: #262730 !important;
    }
    .stChatMessage {
        background-color: #F0F2F6 !important;
        color: #262730 !important;
    }
    .stChatInput {
        background-color: #FFFFFF !important;
    }
    </style>
    """
    st.markdown(light_theme, unsafe_allow_html=True)

# Theme toggle button (will appear TOP LEFT due to CSS)
theme_icon = "🌙" if st.session_state.theme == "light" else "☀️"
if st.button(theme_icon, key="theme_toggle", help="Toggle theme"):
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
    st.rerun()

# Streamlit UI - Title at top
st.markdown("""
<div style="position: fixed; top: 0; left: 0; right: 0; z-index: 999; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); text-align: center;">
    <h1 style="color: white; margin: 0; font-size: 32px;">🌙 Luna</h1>
    <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 14px;">Powered by TCG TECH</p>
</div>
<div style="height: 100px;"></div>
""", unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

if "show_uploader" not in st.session_state:
    st.session_state.show_uploader = False

# Display chat history with modern avatars
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(message["content"])
            if "files" in message and message["files"]:
                for file_info in message["files"]:
                    st.caption(f"📎 {file_info}")
    else:
        with st.chat_message("assistant", avatar="🌙"):
            st.markdown(message["content"])

# File upload section - INLINE with chat input
col1, col2 = st.columns([0.5, 9.5])

with col1:
    uploaded_files = st.file_uploader(
        "📎",
        type=["png", "jpg", "jpeg", "gif", "bmp", "pdf", "txt", "doc", "docx"],
        accept_multiple_files=True,
        key="file_uploader",
        label_visibility="collapsed"
    )
    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files

with col2:
    # Chat input
    prompt = st.chat_input("What would you like to know?")

if uploaded_files:
    st.caption(f"✅ {len(uploaded_files)} file(s) attached")

if prompt:
    # Prepare file context
    file_context = ""
    file_names = []
    
    if st.session_state.uploaded_files:
        file_names = [f.name for f in st.session_state.uploaded_files]
        file_context = f"\n\n[User has uploaded {len(file_names)} file(s): {', '.join(file_names)}. Please acknowledge these files in your response if relevant to the question.]"
    
    # Add user message with modern avatar
    user_message = {"role": "user", "content": prompt}
    if file_names:
        user_message["files"] = file_names
    st.session_state.messages.append(user_message)
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
        if file_names:
            for fname in file_names:
                st.caption(f"📎 {fname}")
    
    # Get AI response with fallback (silent switching) and typing animation
    with st.chat_message("assistant", avatar="🌙"):
        # Typing animation placeholder
        message_placeholder = st.empty()
        
        # Show typing indicator
        typing_html = """
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="font-size: 14px; color: #888;">Luna is typing</div>
            <div style="display: flex; gap: 4px;">
                <div style="width: 8px; height: 8px; border-radius: 50%; background: #888; animation: bounce 1.4s infinite ease-in-out both; animation-delay: -0.32s;"></div>
                <div style="width: 8px; height: 8px; border-radius: 50%; background: #888; animation: bounce 1.4s infinite ease-in-out both; animation-delay: -0.16s;"></div>
                <div style="width: 8px; height: 8px; border-radius: 50%; background: #888; animation: bounce 1.4s infinite ease-in-out both;"></div>
            </div>
        </div>
        <style>
        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }
        </style>
        """
        message_placeholder.markdown(typing_html, unsafe_allow_html=True)
        
        max_retries = len(GEMINI_MODELS)
        response_content = None
        
        # Enhance prompt with file context
        enhanced_prompt = prompt + file_context
        
        for attempt in range(max_retries):
            try:
                llm = get_llm()
                # Include system prompt with user message
                messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=enhanced_prompt)]
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
                else:
                    response_content = "Sorry, an error occurred. Please try again."
                break
        
        # Replace typing indicator with actual response
        message_placeholder.markdown(response_content)
    
    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": response_content})
