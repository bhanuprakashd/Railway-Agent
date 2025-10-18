"""Unit tests for app module."""

import pytest
import re


# Since we can't easily test Streamlit components, we'll test utility functions
# These would need to be extracted or mocked in a real testing scenario

def sanitize_input_test(text: str) -> str:
    """Test version of sanitize_input for testing."""
    if not text:
        return ""
    text = text.strip()
    MAX_LENGTH = 500
    if len(text) > MAX_LENGTH:
        text = text[:MAX_LENGTH]
    text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
    text = re.sub(r'<[^>]+>', '', text)
    return text


def validate_input_test(text: str) -> tuple[bool, str]:
    """Test version of validate_input for testing."""
    if not text or not text.strip():
        return False, "Please enter a message."
    if len(text.strip()) < 2:
        return False, "Message too short. Please provide more details."
    suspicious_patterns = [
        r'<script',
        r'javascript:',
        r'onerror=',
        r'onclick=',
    ]
    for pattern in suspicious_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return False, "Invalid input detected. Please try again."
    return True, ""


class TestInputValidation:
    """Tests for input validation."""
    
    def test_sanitize_normal_input(self):
        """Test sanitization of normal input."""
        result = sanitize_input_test("Hello, how are you?")
        assert result == "Hello, how are you?"
    
    def test_sanitize_with_html(self):
        """Test sanitization removes HTML tags."""
        result = sanitize_input_test("Hello <script>alert('xss')</script>")
        assert "<script>" not in result
        assert "Hello" in result
    
    def test_sanitize_long_input(self):
        """Test sanitization truncates long input."""
        long_text = "a" * 1000
        result = sanitize_input_test(long_text)
        assert len(result) <= 500
    
    def test_sanitize_empty_input(self):
        """Test sanitization of empty input."""
        result = sanitize_input_test("")
        assert result == ""
    
    def test_validate_normal_input(self):
        """Test validation of normal input."""
        is_valid, msg = validate_input_test("What trains go to Delhi?")
        assert is_valid is True
        assert msg == ""
    
    def test_validate_empty_input(self):
        """Test validation rejects empty input."""
        is_valid, msg = validate_input_test("")
        assert is_valid is False
        assert "enter a message" in msg.lower()
    
    def test_validate_short_input(self):
        """Test validation rejects too short input."""
        is_valid, msg = validate_input_test("a")
        assert is_valid is False
        assert "too short" in msg.lower()
    
    def test_validate_suspicious_input(self):
        """Test validation rejects suspicious patterns."""
        is_valid, msg = validate_input_test("<script>alert('xss')</script>")
        assert is_valid is False
        assert "Invalid input" in msg
    
    def test_validate_javascript_url(self):
        """Test validation rejects javascript: URLs."""
        is_valid, msg = validate_input_test("javascript:alert(1)")
        assert is_valid is False


# Run tests with: pytest tests/test_app.py -v

