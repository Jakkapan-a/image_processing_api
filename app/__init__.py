from flask import Flask
from .config import Config
from .routes import upload_bp, detect_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register blueprints
    app.register_blueprint(upload_bp)
    app.register_blueprint(detect_bp)

    return app
