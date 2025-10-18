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

# Import configuration
try:
    from config import config
except ImportError:
    # Fallback if config not available
    class config:
        LOG_LEVEL = "INFO"
        MAX_INPUT_LENGTH = 500
        RATE_LIMIT_ENABLED = False
        RATE_LIMIT_REQUESTS = 10
        RATE_LIMIT_WINDOW = 60

# Import utilities
try:
    from utils import RateLimiter, SimpleCache
except ImportError:
    # Fallback if utils not available
    RateLimiter = None
    SimpleCache = None

# Import authentication
try:
    from auth import login_form, logout
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

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
        background: #ffffff;
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
        background: #ffffff;
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
    
    # Add logout button if authenticated
    if hasattr(config, 'AUTH_ENABLED') and config.AUTH_ENABLED and AUTH_AVAILABLE:
        if st.session_state.get('authenticated', False):
            st.markdown("---")
            st.markdown(f"**User:** {st.session_state.get('username', 'Unknown')}")
            if st.button("🚪 Logout"):
                logout()

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

# Initialize rate limiter
if 'rate_limiter' not in st.session_state and RateLimiter and config.RATE_LIMIT_ENABLED:
    st.session_state.rate_limiter = RateLimiter(
        max_requests=config.RATE_LIMIT_REQUESTS,
        window=config.RATE_LIMIT_WINDOW
    )

# Initialize cache
if 'cache' not in st.session_state and SimpleCache:
    st.session_state.cache = SimpleCache(ttl=3600)  # 1 hour cache

# Generate a simple user ID (in production, use actual authentication)
if 'user_id' not in st.session_state:
    import uuid
    st.session_state.user_id = str(uuid.uuid4())[:8]

# ════
# UTILITY FUNCTIONS
# ════

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection and limit length.
    
    Args:
        text: Raw user input
        
    Returns:
        str: Sanitized input
    """
    if not text:
        return ""
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Limit maximum length to prevent abuse
    if len(text) > config.MAX_INPUT_LENGTH:
        text = text[:config.MAX_INPUT_LENGTH]
        logger.warning(f"Input truncated to {config.MAX_INPUT_LENGTH} characters")
    
    # Remove control characters except newlines and tabs
    text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
    
    # Basic XSS prevention (remove HTML/script tags)
    import re
    text = re.sub(r'<[^>]+>', '', text)
    
    return text

def validate_input(text: str) -> tuple[bool, str]:
    """Validate user input.
    
    Args:
        text: User input to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not text or not text.strip():
        return False, "Please enter a message."
    
    if len(text.strip()) < 2:
        return False, "Message too short. Please provide more details."
    
    # Check for suspicious patterns
    suspicious_patterns = [
        r'<script',
        r'javascript:',
        r'onerror=',
        r'onclick=',
    ]
    
    import re
    for pattern in suspicious_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return False, "Invalid input detected. Please try again."
    
    return True, ""

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
# AUTHENTICATION CHECK
# ════

# Check if authentication is required and enabled
if hasattr(config, 'AUTH_ENABLED') and config.AUTH_ENABLED and AUTH_AVAILABLE:
    if not login_form():
        st.stop()

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
    # Check rate limit
    if config.RATE_LIMIT_ENABLED and 'rate_limiter' in st.session_state:
        is_allowed, seconds = st.session_state.rate_limiter.is_allowed(st.session_state.user_id)
        if not is_allowed:
            st.error(f"⏱️ Too many requests. Please wait {seconds} seconds before trying again.")
            st.stop()
    
    # Validate and sanitize input
    is_valid, error_msg = validate_input(prompt)
    
    if not is_valid:
        st.error(error_msg)
        st.stop()
    
    # Sanitize the input
    prompt = sanitize_input(prompt)
    
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
        except TimeoutError:
            logger.error("Request timeout")
            response = "⏱️ Request timed out. The server took too long to respond. Please try again."
        except ConnectionError as e:
            logger.error(f"Connection error: {str(e)}")
            response = "🔌 Connection error. Please check your internet connection and try again."
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            response = "❌ An error occurred while processing your request. Please try again or rephrase your question."
        
        # Clear animation and show response
        loading_placeholder.empty()
        st.markdown(response)
        
        # Add assistant message to session state
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.conversation_history.append({"role": "assistant", "content": response})