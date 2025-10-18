"""Unit tests for configuration module."""

import pytest
from config import Config


class TestConfig:
    """Tests for Config class."""
    
    def test_config_defaults(self):
        """Test that config has default values."""
        assert Config.OLLAMA_API_BASE is not None
        assert Config.MODEL_NAME is not None
        assert Config.TEMPERATURE >= 0
        assert Config.TEMPERATURE <= 1
    
    def test_config_mcp_settings(self):
        """Test MCP configuration."""
        assert Config.MCP_ENDPOINT is not None
        assert Config.MCP_TIMEOUT > 0
    
    def test_config_app_settings(self):
        """Test application settings."""
        assert Config.APP_NAME is not None
        assert Config.LOG_LEVEL in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        assert Config.MAX_INPUT_LENGTH > 0
    
    def test_config_validation(self):
        """Test configuration validation."""
        errors = Config.validate()
        # Should return empty list if all valid
        assert isinstance(errors, list)
    
    def test_config_display(self):
        """Test configuration display string."""
        display = Config.display()
        assert isinstance(display, str)
        assert "Railway Agent Configuration" in display
        assert len(display) > 0


# Run tests with: pytest tests/test_config.py -v

