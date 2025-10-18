"""
Configuration management for Railway Agent.
Loads configuration from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from typing import Optional

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    # python-dotenv not installed, will use environment variables directly
    pass


class Config:
    """Application configuration."""
    
    # ════════════════════════════════════════════════════════
    # LLM Configuration
    # ════════════════════════════════════════════════════════
    OLLAMA_API_BASE: str = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "ollama/glm-4.6:cloud")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.1"))
    
    # ════════════════════════════════════════════════════════
    # MCP Configuration
    # ════════════════════════════════════════════════════════
    MCP_ENDPOINT: str = os.getenv("MCP_ENDPOINT", "https://railway-mcp.amithv.xyz/mcp")
    MCP_TIMEOUT: int = int(os.getenv("MCP_TIMEOUT", "360"))
    
    # ════════════════════════════════════════════════════════
    # Application Configuration
    # ════════════════════════════════════════════════════════
    APP_NAME: str = os.getenv("APP_NAME", "train_agent_app")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    MAX_INPUT_LENGTH: int = int(os.getenv("MAX_INPUT_LENGTH", "500"))
    
    # ════════════════════════════════════════════════════════
    # Session Configuration
    # ════════════════════════════════════════════════════════
    SESSION_TIMEOUT: int = int(os.getenv("SESSION_TIMEOUT", "3600"))
    MAX_CONVERSATION_HISTORY: int = int(os.getenv("MAX_CONVERSATION_HISTORY", "50"))
    
    # ════════════════════════════════════════════════════════
    # Rate Limiting
    # ════════════════════════════════════════════════════════
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    
    # ════════════════════════════════════════════════════════
    # Authentication (Optional)
    # ════════════════════════════════════════════════════════
    AUTH_ENABLED: bool = os.getenv("AUTH_ENABLED", "false").lower() == "true"
    AUTH_USERNAME: Optional[str] = os.getenv("AUTH_USERNAME")
    AUTH_PASSWORD: Optional[str] = os.getenv("AUTH_PASSWORD")
    AUTH_COOKIE_NAME: str = os.getenv("AUTH_COOKIE_NAME", "railway_agent_auth")
    AUTH_COOKIE_KEY: str = os.getenv("AUTH_COOKIE_KEY", "railway-agent-secret-key-change-in-production")
    AUTH_COOKIE_EXPIRY_DAYS: int = int(os.getenv("AUTH_COOKIE_EXPIRY_DAYS", "30"))
    
    @classmethod
    def validate(cls) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        if cls.TEMPERATURE < 0 or cls.TEMPERATURE > 1:
            errors.append("TEMPERATURE must be between 0 and 1")
        
        if cls.MCP_TIMEOUT < 10:
            errors.append("MCP_TIMEOUT must be at least 10 seconds")
        
        if cls.MAX_INPUT_LENGTH < 10:
            errors.append("MAX_INPUT_LENGTH must be at least 10 characters")
        
        if cls.AUTH_ENABLED and not (cls.AUTH_USERNAME and cls.AUTH_PASSWORD):
            errors.append("AUTH_USERNAME and AUTH_PASSWORD required when AUTH_ENABLED=true")
        
        return errors
    
    @classmethod
    def display(cls) -> str:
        """Return configuration as formatted string (hiding sensitive values)."""
        lines = [
            "=" * 60,
            "Railway Agent Configuration",
            "=" * 60,
            f"LLM Model: {cls.MODEL_NAME}",
            f"Ollama Base: {cls.OLLAMA_API_BASE}",
            f"Temperature: {cls.TEMPERATURE}",
            f"MCP Endpoint: {cls.MCP_ENDPOINT}",
            f"MCP Timeout: {cls.MCP_TIMEOUT}s",
            f"Log Level: {cls.LOG_LEVEL}",
            f"Rate Limiting: {'Enabled' if cls.RATE_LIMIT_ENABLED else 'Disabled'}",
            f"Authentication: {'Enabled' if cls.AUTH_ENABLED else 'Disabled'}",
            "=" * 60,
        ]
        return "\n".join(lines)


# Singleton instance
config = Config()

# Validate on import
validation_errors = config.validate()
if validation_errors:
    import warnings
    for error in validation_errors:
        warnings.warn(f"Configuration error: {error}")


if __name__ == "__main__":
    # Print configuration when run directly
    print(config.display())
    
    # Check for validation errors
    errors = config.validate()
    if errors:
        print("\n⚠️  Configuration Errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\n✅ Configuration is valid")

