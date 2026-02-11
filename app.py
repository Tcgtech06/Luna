import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import os

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
    os.environ["GOOGLE_API_KEY"] = "AIzaSyBc9nlbPfYzGFIVeDz8hOcU61Ig4R7NxYc"

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
/* Hide all Streamlit branding */
#MainMenu {visibility: hidden !important;}
footer {visibility: hidden !important;}
header {visibility: hidden !important;}
.stDeployButton {display: none !important;}
[data-testid="stToolbar"] {display: none !important;}
.viewerBadge_container__1QSob {display: none !important;}
.styles_viewerBadge__1yB5_ {display: none !important;}
a[href*="streamlit.io"] {display: none !important;}
.viewerBadge_link__1S137 {display: none !important;}
.viewerBadge_text__1JaDK {display: none !important;}
footer > div {display: none !important;}
.css-164nlkn {display: none !important;}
.css-1dp5vir {display: none !important;}
div[data-testid="stStatusWidget"] {display: none !important;}
#MainMenu {display: none !important;}
footer {display: none !important;}
.stApp footer {display: none !important;}
.stApp > footer {display: none !important;}
button[kind="header"] {display: none !important;}

/* Position theme toggle button to top right */
.stButton {
    position: fixed;
    top: 10px;
    right: 10px;
    z-index: 999999;
}

/* Hide warning messages */
.stAlert {display: none !important;}
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
    
    /* Chat messages */
    .stChatMessage {
        background-color: #2D2D2D !important;
        color: #E0E0E0 !important;
    }
    
    /* Chat input container and all its children */
    .stChatInput {
        background-color: #2D2D2D !important;
    }
    .stChatInput > div {
        background-color: #2D2D2D !important;
    }
    .stChatInput textarea {
        background-color: #2D2D2D !important;
        color: #E0E0E0 !important;
        border-color: #404040 !important;
    }
    .stChatInput input {
        background-color: #2D2D2D !important;
        color: #E0E0E0 !important;
    }
    
    /* Text input styling */
    .stTextInput > div > div > input {
        background-color: #2D2D2D !important;
        color: #E0E0E0 !important;
        border-color: #404040 !important;
    }
    div[data-baseweb="base-input"] {
        background-color: #2D2D2D !important;
    }
    div[data-baseweb="input"] {
        background-color: #2D2D2D !important;
    }
    
    /* Chat input bottom section */
    section[data-testid="stChatInput"] {
        background-color: #2D2D2D !important;
    }
    section[data-testid="stChatInput"] > div {
        background-color: #2D2D2D !important;
    }
    
    /* Input field wrapper */
    div[data-testid="stChatInputTextArea"] {
        background-color: #2D2D2D !important;
    }
    div[data-testid="stChatInputTextArea"] textarea {
        background-color: #2D2D2D !important;
        color: #E0E0E0 !important;
    }
    
    /* Bottom container */
    .stBottom {
        background-color: #2D2D2D !important;
    }
    
    /* All text areas */
    textarea {
        background-color: #2D2D2D !important;
        color: #E0E0E0 !important;
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

# Theme toggle button (will appear top right due to CSS)
theme_icon = "🌙" if st.session_state.theme == "light" else "☀️"
if st.button(theme_icon, key="theme_toggle", help="Toggle theme"):
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
    st.rerun()

# Streamlit UI
st.title("🌙 Luna")
st.caption("Powered by TCG TECH")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response with fallback (silent switching)
    with st.chat_message("assistant"):
        max_retries = len(GEMINI_MODELS)
        response_content = None
        
        for attempt in range(max_retries):
            try:
                llm = get_llm()
                # Include system prompt with user message
                messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)]
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
        
        st.markdown(response_content)
    
    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": response_content})
