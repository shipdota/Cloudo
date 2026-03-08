import pytest
import sys
import os

# Ensure the app module can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
import app.main as app_main

@pytest.fixture(autouse=True)
def reset_leaderboard_cache():
    """Reset the leaderboard cache before each test to ensure isolation."""
    app_main.leaderboard_cache = {"data": None, "timestamp": 0}

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
