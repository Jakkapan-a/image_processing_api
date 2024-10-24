import os

class Config:
    UPLOAD_FOLDER = 'public/uploads'
    MODEL_FOLDER = 'models'
    DETECT_FOLDER = 'public/detect'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 16MB
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    PORT = int(os.getenv("PORT", 10010))
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class DevelopmentConfig(Config):
    DEBUG = True
    FLASK_ENV = 'development'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')

class ProductionConfig(Config):
    DEBUG = False
    FLASK_ENV = 'production'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecretkey')