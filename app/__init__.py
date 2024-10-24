from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from dotenv import load_dotenv
import os

db = SQLAlchemy()

def create_app():
    # Load environment variables
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(Config)

    print('SQLALCHEMY_DATABASE_URI:', app.config['SQLALCHEMY_DATABASE_URI'])

    # Initialize database
    db.init_app(app)

    # Register blueprints
    from .routes import upload_bp, detect_bp, classify_bp, index_app
    app.register_blueprint(index_app)
    app.register_blueprint(upload_bp, url_prefix='/api/file')
    app.register_blueprint(detect_bp, url_prefix='/api/detect')
    app.register_blueprint(classify_bp, url_prefix='/api/classify')

    return app
