"""Unit tests for train_agent module."""

import pytest
from train_agent.agent import greeting


class TestGreeting:
    """Tests for greeting function."""
    
    def test_greeting_hello(self):
        """Test greeting with 'hello'."""
        response = greeting("hello")
        assert "Train_Agent" in response
        assert "Indian Railway" in response
        assert "Train schedules" in response
    
    def test_greeting_hi(self):
        """Test greeting with 'hi'."""
        response = greeting("hi")
        assert "Train_Agent" in response
        assert "Indian Railway" in response
    
    def test_greeting_bye(self):
        """Test goodbye message."""
        response = greeting("bye")
        assert "Goodbye" in response
        assert "Safe travels" in response
    
    def test_greeting_goodbye(self):
        """Test goodbye with 'goodbye'."""
        response = greeting("goodbye")
        assert "Goodbye" in response
    
    def test_greeting_random(self):
        """Test greeting with random text."""
        response = greeting("random text")
        assert "Welcome" in response or "Indian Railway" in response
    
    def test_greeting_empty(self):
        """Test greeting with empty string."""
        response = greeting("")
        assert isinstance(response, str)
        assert len(response) > 0


class TestWorkflow:
    """Tests for workflow function (requires mocking)."""
    
    @pytest.mark.asyncio
    async def test_workflow_returns_string(self):
        """Test that workflow returns a string."""
        # This would require mocking the LLM and MCP toolset
        # Skipping for now, but structure is here
        pass


# Run tests with: pytest tests/test_agent.py -v

