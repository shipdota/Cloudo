import pytest
import sys
import os

# Ensure the app module can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app

@pytest.fixture
def app():
    # Clear cache before each test to ensure isolation
    import app.main
    app.main.leaderboard_cache = {
        'data': [],
        'timestamp': 0
    }

    app_instance = create_app()
    app_instance.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-key"
    })
    return app_instance

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
