import os

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from dotenv import load_dotenv
import logging
from logging.handlers import TimedRotatingFileHandler
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    from app.models.file_management import FileManagement  #
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
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    app.logger.addHandler(handler)

    app.logger.info('Starting server...')

    # Initialize database
    db.init_app(app)
    migrate.init_app(app, db)
    app.logger.info('Initialized app successfully!')


    # Register blueprints
    from .routes import upload_bp, detect_bp, classify_bp, index_app ,filemanager_bp
    app.register_blueprint(detect_bp, url_prefix='/api/detect')
    app.register_blueprint(classify_bp, url_prefix='/api/classify')
    app.register_blueprint(upload_bp, url_prefix='/api/file')
    app.register_blueprint(filemanager_bp, url_prefix='/api/filemanager')
    app.register_blueprint(index_app, url_prefix='')

    @app.cli.command('test')
    def test():
       print("Test command executed successfully!")

    @app.cli.command('init-db')
    def init_db():
        # migrations

        """Initialize the database."""
        with app.app_context():
            db.create_all()
            print("Database tables created successfully!")
        if not os.path.exists('migrations'):
            os.mkdir('migrations')

    @app.cli.command('drop-db')
    def drop_db():
        """Drop the database."""
        with app.app_context():
            db.drop_all()
            print("Database tables dropped successfully!")

    @app.cli.command('seed-db')
    def seed_db():
        """Seed the database."""
        with app.app_context():
            from app.models.file_management import FileManagement
            db.session.add(FileManagement(name='test', filename='test.jpg', filepath='public/uploads/test.jpg', type_file='cls'))
            db.session.commit()
            print("Database seeded successfully!")

    @app.cli.command('clean-db')
    def clean_up():
        """Clean up the clean-db folder."""
        with app.app_context():
            from app.services.file_manager import clean_up_width_db
            clean_up_width_db('models/cls')
            # clean_up_width_db('models/cls')
            print("Cls folder cleaned up successfully!")

    from app.services.model_loader import clean_model_cache
    # schedule clean up
    scheduler = BackgroundScheduler()
    if not any(job.name == "clean_model_cache_job" for job in scheduler.get_jobs()):
        scheduler.add_job(clean_model_cache, 'interval', minutes=15, id="clean_model_cache_job")

    scheduler.start()

    return app
