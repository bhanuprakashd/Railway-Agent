"""
Simple authentication module for Railway Agent.
For production use, consider using streamlit-authenticator or a proper auth system.
"""

import hashlib
import hmac
import streamlit as st
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def hash_password(password: str, salt: str = "railway-agent-salt") -> str:
    """
    Hash a password with salt.
    
    Args:
        password: Plain text password
        salt: Salt for hashing
        
    Returns:
        str: Hashed password
    """
    return hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    ).hex()


def verify_password(password: str, hashed: str, salt: str = "railway-agent-salt") -> bool:
    """
    Verify a password against its hash.
    
    Args:
        password: Plain text password to verify
        hashed: Hashed password to compare against
        salt: Salt used for hashing
        
    Returns:
        bool: True if password matches
    """
    return hmac.compare_digest(
        hash_password(password, salt),
        hashed
    )


def check_authentication(username: str, password: str) -> bool:
    """
    Check if username and password are correct.
    
    Args:
        username: Username to check
        password: Password to check
        
    Returns:
        bool: True if authenticated
    """
    try:
        from config import config
        
        if not config.AUTH_ENABLED:
            return True
        
        if not config.AUTH_USERNAME or not config.AUTH_PASSWORD:
            logger.warning("Authentication enabled but credentials not configured")
            return False
        
        # Simple username/password check
        # In production, use a proper user database
        username_match = hmac.compare_digest(username, config.AUTH_USERNAME)
        
        # Check if password is already hashed or plain text
        if len(config.AUTH_PASSWORD) == 64:  # Likely a hash
            password_match = verify_password(password, config.AUTH_PASSWORD)
        else:
            password_match = hmac.compare_digest(password, config.AUTH_PASSWORD)
        
        return username_match and password_match
        
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return False


def login_form() -> bool:
    """
    Display login form and return authentication status.
    
    Returns:
        bool: True if user is authenticated
    """
    # Check if already authenticated
    if st.session_state.get('authenticated', False):
        return True
    
    # Display login form
    st.markdown("## 🔐 Login Required")
    st.markdown("Please log in to access the Railway Assistant.")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if check_authentication(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                logger.info(f"User {username} logged in successfully")
                st.success("✅ Login successful!")
                st.rerun()
            else:
                logger.warning(f"Failed login attempt for username: {username}")
                st.error("❌ Invalid username or password")
    
    return False


def logout():
    """Logout the current user."""
    if 'username' in st.session_state:
        logger.info(f"User {st.session_state.username} logged out")
    
    st.session_state.authenticated = False
    st.session_state.username = None
    st.rerun()


def require_auth(func):
    """
    Decorator to require authentication for a function.
    
    Usage:
        @require_auth
        def my_protected_function():
            # This will only run if user is authenticated
            pass
    """
    def wrapper(*args, **kwargs):
        try:
            from config import config
            if not config.AUTH_ENABLED:
                return func(*args, **kwargs)
        except ImportError:
            return func(*args, **kwargs)
        
        if not login_form():
            st.stop()
        
        return func(*args, **kwargs)
    
    return wrapper


# Example usage in main app:
# if __name__ == "__main__":
#     from config import config
#     
#     if config.AUTH_ENABLED:
#         if not login_form():
#             st.stop()
#     
#     # Rest of your app code here

