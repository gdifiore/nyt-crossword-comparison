"""Pytest configuration and fixtures."""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set test environment variables before any imports
os.environ["DATABASE_HOST"] = "localhost"
os.environ["DATABASE_NAME"] = "test_db"
os.environ["DATABASE_USERNAME"] = "test_user"
os.environ["DATABASE_PASSWORD"] = "test_pass"
os.environ["TESTING"] = "true"


@pytest.fixture(scope="session", autouse=True)
def mock_database_connection():
    """Mock database connection for all tests."""
    mock_pool = MagicMock()
    mock_conn = MagicMock()
    mock_pool.getconn.return_value = mock_conn
    mock_pool.putconn.return_value = None

    with patch("psycopg2.pool.SimpleConnectionPool", return_value=mock_pool):
        yield mock_pool


@pytest.fixture
def app():
    """Create and configure a test Flask application."""
    # Clear sys.modules to force reimport
    if "src.app" in sys.modules:
        del sys.modules["src.app"]

    # Import app module
    import src.app as flask_app

    # Configure for testing
    flask_app.app.config["TESTING"] = True
    flask_app.app.config["WTF_CSRF_ENABLED"] = False

    # Disable rate limiting for tests
    flask_app.limiter.enabled = False

    yield flask_app.app


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()
