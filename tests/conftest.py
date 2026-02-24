import pytest
import sys
import os

# Ensure the app module can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-key"
    })
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture(autouse=True)
def clear_cache():
    """Clear the leaderboard cache before each test to ensure test isolation."""
    from app.main import leaderboard_cache
    leaderboard_cache.clear()
    yield
