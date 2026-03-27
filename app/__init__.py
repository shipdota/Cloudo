from flask import Flask, render_template, session, g
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    secret_key = os.environ.get("FLASK_SECRET_KEY")
    if not secret_key:
        raise RuntimeError("FLASK_SECRET_KEY environment variable is not set")
    app.secret_key = secret_key

    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from .main import main_bp
    app.register_blueprint(main_bp)

    from .game import game_bp
    app.register_blueprint(game_bp)

    @app.route('/health')
    def health():
        return "OK", 200

    return app
