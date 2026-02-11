import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
import os

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

def get_llm():
    model_name = GEMINI_MODELS[st.session_state.current_model_index]
    return ChatGoogleGenerativeAI(model=model_name, temperature=0.7)

def try_next_model():
    """Switch to the next available model"""
    st.session_state.current_model_index = (st.session_state.current_model_index + 1) % len(GEMINI_MODELS)
    return GEMINI_MODELS[st.session_state.current_model_index]

# Streamlit UI
st.title("🌙 Luna")
current_model = GEMINI_MODELS[st.session_state.current_model_index]
st.caption(f"Powered by TCG TECH | Model: {current_model}")

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
    
    # Get AI response with fallback
    with st.chat_message("assistant"):
        max_retries = len(GEMINI_MODELS)
        response_content = None
        
        for attempt in range(max_retries):
            try:
                llm = get_llm()
                response = llm.invoke([HumanMessage(content=prompt)])
                response_content = response.content
                break
            except Exception as e:
                error_msg = str(e)
                if "quota" in error_msg.lower() or "limit" in error_msg.lower() or "not found" in error_msg.lower() or "404" in error_msg:
                    next_model = try_next_model()
                    if attempt < max_retries - 1:
                        st.warning(f"Switching to {next_model}...")
                        continue
                    else:
                        st.error("All models exhausted. Please try again later.")
                        response_content = "Sorry, I'm unable to respond right now. Please try again later."
                else:
                    st.error(f"Error: {error_msg}")
                    response_content = "Sorry, an error occurred. Please try again."
                break
        
        st.markdown(response_content)
    
    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": response_content})
