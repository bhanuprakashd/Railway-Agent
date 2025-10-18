"""
Railway Chatbot - ChatGPT-style Interface
"""

import streamlit as st
from train_agent.agent import workflow, reset_session
import asyncio
import logging
from datetime import datetime
import os
from pathlib import Path

# ════
# CONFIGURATION
# ════

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(LOG_DIR / f'chat_{datetime.now().strftime("%Y%m%d")}.log')]
)
logger = logging.getLogger(__name__)

# ════
# PAGE CONFIG
# ════

st.set_page_config(
    page_title="Railway Assistant",
    page_icon="🚂",
    layout="centered",
    initial_sidebar_state="auto"
)

# ════
# MINIMAL CHATGPT-STYLE THEME
# ════

st.markdown("""
<style>
    /* Clean white background */
    .main {
        background: #ffff;
    }

    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Chat messages - minimal style */
    .stChatMessage {
        border: none;
        padding: 1.5rem 1rem;
        margin: 0;
        background: transparent;
    }

    /* User messages - light gray background */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: #f7f7f8;
    }

    /* Assistant messages - white */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background: #ffff;
    }

    /* Input box */
    .stChatInputContainer {
        border: 1px solid #d9d9e3;
        border-radius: 12px;
        background: white;
    }

    /* Button styling */
    .stButton > button {
        border-radius: 6px;
        border: 1px solid #d9d9e3;
        background: white;
        color: #000;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }

    .stButton > button:hover {
        background: #f7f7f8;
    }

    /* Heading style */
    h1 {
        text-align: center;
        color: #202123;
        font-weight: 600;
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }

    .subtitle {
        text-align: center;
        color: #6e6e80;
        font-size: 0.95rem;
        margin-bottom: 2rem;
    }

    /* Train animation - left to right with flipped train */
    @keyframes trainMove {
        0% { transform: translateX(-100%) scaleX(-1); }
        100% { transform: translateX(100vw) scaleX(-1); }
    }

    .train-loader {
        font-size: 2rem;
        animation: trainMove 4s linear infinite;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# ════
# SIDEBAR - ABOUT
# ════

with st.sidebar:
    st.title("About")
    st.markdown("""
    ### 🚂 Railway Assistant
    
    Your AI-powered Indian Railway information assistant.
    
    **Features:**
    - Train schedules and information
    - PNR status checking
    - Live train tracking
    - Seat availability
    - Station details
    
    Get real-time information about Indian Railways with ease!
    """)
    
    # Add reset button
    if st.button("🔄 Reset Conversation"):
        st.session_state.messages = []
        st.session_state.conversation_history = []
        reset_session()
        st.rerun()

# ════
# SESSION STATE
# ════

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

if 'event_loop' not in st.session_state:
    # Create a persistent event loop for the session
    st.session_state.event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(st.session_state.event_loop)

# ════
# UTILITY FUNCTIONS
# ════

def extract_response(result) -> str:
    try:
        if isinstance(result, str):
            return result
        if isinstance(result, list):
            return "\n\n".join([str(item) for item in result])
        if hasattr(result, 'text'):
            return result.text
        if hasattr(result, 'content'):
            return result.content
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

# ════
# MAIN INTERFACE
# ════

# Header
st.title("🚂 Railway Assistant")
st.markdown('<p class="subtitle">Your AI-powered Indian Railway information assistant</p>', unsafe_allow_html=True)
st.markdown("---")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Message Railway Assistant"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.conversation_history.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Get assistant response
    with st.chat_message("assistant"):
        # Show train animation while loading
        loading_placeholder = st.empty()
        loading_placeholder.markdown('<div class="train-loader">🚂💨</div>', unsafe_allow_html=True)
        
        # Use the persistent event loop
        loop = st.session_state.event_loop
        
        try:
            response = loop.run_until_complete(workflow(prompt))
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            response = f"❌ An error occurred: {str(e)}"
        
        # Clear animation and show response
        loading_placeholder.empty()
        st.markdown(response)

    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.conversation_history.append({"role": "assistant", "content": response})
    st.rerun()