import os

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from dotenv import load_dotenv
import logging
from logging.handlers import TimedRotatingFileHandler
from flask_cors import CORS

db = SQLAlchemy()
def create_app():
    # Load environment variables
    load_dotenv()
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.config.from_object(Config)
    # logs
    if not os.path.exists('logs'):
        os.mkdir('logs')

    # Logging
    handler = TimedRotatingFileHandler(app.config['LOG_FILE'], when="midnight", interval=1)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    app.logger.info('Starting server...')

    print('SQLALCHEMY_DATABASE_URI:', app.config['SQLALCHEMY_DATABASE_URI'])

    # Initialize database
    db.init_app(app)

    # Register blueprints
    from .routes import upload_bp, detect_bp, classify_bp, index_app
    app.register_blueprint(index_app)
    app.register_blueprint(upload_bp, url_prefix='/api/file')
    app.register_blueprint(detect_bp, url_prefix='/api/detect')
    app.register_blueprint(classify_bp, url_prefix='/api/classify')



    from app.services.model_loader import clean_model_cache
    # schedule clean up
    scheduler = BackgroundScheduler()
    if not any(job.name == "clean_model_cache_job" for job in scheduler.get_jobs()):
        scheduler.add_job(clean_model_cache, 'interval', minutes=15, id="clean_model_cache_job")

    scheduler.start()

    return app
