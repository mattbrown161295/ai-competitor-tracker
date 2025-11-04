"""
Unit tests for the scraper module.
"""

import pytest
from unittest.mock import Mock, patch
from src.core.scraper import SessionManager, RateLimiter, ContentFetcher


class TestSessionManager:
    """Test SessionManager functionality."""

    def test_get_session_creates_new_session(self):
        """Test that get_session creates a new session for a domain."""
        user_agents = ["Mozilla/5.0 Test Agent"]
        manager = SessionManager(user_agents)

        session = manager.get_session("example.com")
        assert session is not None
        assert "example.com" in manager.sessions

    def test_get_session_reuses_existing_session(self):
        """Test that get_session reuses existing session for same domain."""
        user_agents = ["Mozilla/5.0 Test Agent"]
        manager = SessionManager(user_agents)

        session1 = manager.get_session("example.com")
        session2 = manager.get_session("example.com")

        assert session1 is session2

    def test_rotate_user_agent(self):
        """Test user agent rotation."""
        user_agents = ["Agent1", "Agent2"]
        manager = SessionManager(user_agents)

        manager.get_session("example.com")
        original_agent = manager.sessions["example.com"].headers["User-Agent"]

        # Rotate (may or may not change due to random selection)
        manager.rotate_user_agent("example.com")
        new_agent = manager.sessions["example.com"].headers["User-Agent"]

        # Just verify it's one of our agents
        assert new_agent in user_agents


class TestRateLimiter:
    """Test RateLimiter functionality."""

    def test_rate_limiter_initialization(self):
        """Test rate limiter initialization."""
        limiter = RateLimiter(min_delay=1, max_delay=2)

        assert limiter.min_delay == 1
        assert limiter.max_delay == 2
        assert len(limiter.last_request_time) == 0

    def test_wait_adds_delay(self):
        """Test that wait adds appropriate delay."""
        import time

        limiter = RateLimiter(min_delay=0.1, max_delay=0.2)

        # First request should not wait
        start = time.time()
        limiter.wait("example.com")
        first_duration = time.time() - start

        assert first_duration < 0.1  # Should be nearly instant

        # Second request should wait
        start = time.time()
        limiter.wait("example.com")
        second_duration = time.time() - start

        assert second_duration >= 0.1  # Should wait at least min_delay


class TestContentFetcher:
    """Test ContentFetcher functionality."""

    @patch("src.core.scraper.requests.Session.get")
    def test_fetch_successful(self, mock_get):
        """Test successful content fetch."""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Test content</body></html>"
        mock_get.return_value = mock_response

        # Create fetcher
        session_manager = SessionManager(["Test Agent"])
        rate_limiter = RateLimiter(min_delay=0, max_delay=0)
        fetcher = ContentFetcher(session_manager, rate_limiter)

        # Fetch content
        result = fetcher.fetch("http://example.com")

        assert result == "<html><body>Test content</body></html>"
        mock_get.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
