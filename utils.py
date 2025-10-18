"""
Utility functions for Railway Agent.
Includes rate limiting, caching, and other helper functions.
"""

import time
import hashlib
from functools import wraps
from typing import Optional, Callable, Any
import logging

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════
# RATE LIMITING
# ════════════════════════════════════════════════════════

class RateLimiter:
    """Simple rate limiter using sliding window."""
    
    def __init__(self, max_requests: int = 10, window: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed in the window
            window: Time window in seconds
        """
        self.max_requests = max_requests
        self.window = window
        self.requests = {}
    
    def is_allowed(self, user_id: str) -> tuple[bool, Optional[int]]:
        """
        Check if a request is allowed for the given user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            tuple: (is_allowed, seconds_until_reset)
        """
        current_time = time.time()
        
        # Initialize user if not exists
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        # Remove old requests outside the window
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if current_time - req_time < self.window
        ]
        
        # Check if limit exceeded
        if len(self.requests[user_id]) >= self.max_requests:
            oldest_request = min(self.requests[user_id])
            seconds_until_reset = int(self.window - (current_time - oldest_request))
            logger.warning(f"Rate limit exceeded for user {user_id}")
            return False, seconds_until_reset
        
        # Add current request
        self.requests[user_id].append(current_time)
        return True, None
    
    def reset(self, user_id: str):
        """Reset rate limit for a user."""
        if user_id in self.requests:
            self.requests[user_id] = []
            logger.info(f"Rate limit reset for user {user_id}")


def rate_limit(limiter: RateLimiter, user_id_func: Callable[[], str]):
    """
    Decorator for rate limiting functions.
    
    Args:
        limiter: RateLimiter instance
        user_id_func: Function that returns the current user ID
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = user_id_func()
            is_allowed, seconds = limiter.is_allowed(user_id)
            
            if not is_allowed:
                raise Exception(f"Rate limit exceeded. Try again in {seconds} seconds.")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# ════════════════════════════════════════════════════════
# CACHING
# ════════════════════════════════════════════════════════

class SimpleCache:
    """Simple in-memory cache with TTL."""
    
    def __init__(self, ttl: int = 3600):
        """
        Initialize cache.
        
        Args:
            ttl: Time to live in seconds (default: 1 hour)
        """
        self.ttl = ttl
        self.cache = {}
        self.timestamps = {}
    
    def _make_key(self, *args, **kwargs) -> str:
        """Create cache key from arguments."""
        key_str = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key not in self.cache:
            return None
        
        # Check if expired
        if time.time() - self.timestamps[key] > self.ttl:
            del self.cache[key]
            del self.timestamps[key]
            logger.debug(f"Cache expired for key: {key[:8]}...")
            return None
        
        logger.debug(f"Cache hit for key: {key[:8]}...")
        return self.cache[key]
    
    def set(self, key: str, value: Any):
        """Set value in cache."""
        self.cache[key] = value
        self.timestamps[key] = time.time()
        logger.debug(f"Cache set for key: {key[:8]}...")
    
    def clear(self):
        """Clear all cache."""
        self.cache.clear()
        self.timestamps.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        current_time = time.time()
        active_entries = sum(
            1 for ts in self.timestamps.values()
            if current_time - ts < self.ttl
        )
        
        return {
            "total_entries": len(self.cache),
            "active_entries": active_entries,
            "ttl": self.ttl
        }


def cached(cache: SimpleCache):
    """
    Decorator for caching function results.
    
    Args:
        cache: SimpleCache instance
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            key = cache._make_key(*args, **kwargs)
            
            # Try to get from cache
            cached_result = cache.get(key)
            if cached_result is not None:
                return cached_result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(key, result)
            
            return result
        return wrapper
    return decorator


# ════════════════════════════════════════════════════════
# PERFORMANCE MONITORING
# ════════════════════════════════════════════════════════

def timed(func):
    """Decorator to measure function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        duration = end_time - start_time
        logger.info(f"{func.__name__} took {duration:.2f}s")
        
        return result
    return wrapper


# ════════════════════════════════════════════════════════
# INPUT SANITIZATION HELPERS
# ════════════════════════════════════════════════════════

def clean_train_number(train_no: str) -> str:
    """Clean and validate train number."""
    # Remove non-digits
    train_no = ''.join(c for c in train_no if c.isdigit())
    
    # Train numbers are typically 5 digits
    if len(train_no) > 5:
        train_no = train_no[:5]
    
    return train_no


def clean_pnr_number(pnr: str) -> str:
    """Clean and validate PNR number."""
    # Remove non-digits
    pnr = ''.join(c for c in pnr if c.isdigit())
    
    # PNR is exactly 10 digits
    if len(pnr) > 10:
        pnr = pnr[:10]
    
    return pnr


def clean_station_code(code: str) -> str:
    """Clean and validate station code."""
    # Station codes are typically 2-4 uppercase letters
    code = code.upper().strip()
    code = ''.join(c for c in code if c.isalpha())
    
    if len(code) > 4:
        code = code[:4]
    
    return code


# ════════════════════════════════════════════════════════
# HEALTH CHECK
# ════════════════════════════════════════════════════════

def health_check() -> dict:
    """Perform basic health check."""
    try:
        import requests
        
        # Check MCP endpoint
        from config import config
        response = requests.get(config.MCP_ENDPOINT, timeout=5)
        mcp_status = response.status_code == 200
    except Exception as e:
        logger.error(f"MCP health check failed: {e}")
        mcp_status = False
    
    return {
        "status": "healthy" if mcp_status else "degraded",
        "mcp_available": mcp_status,
        "timestamp": time.time()
    }

