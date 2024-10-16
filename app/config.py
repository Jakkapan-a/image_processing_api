import os

class Config:
    UPLOAD_FOLDER = 'public/uploads'
    MODEL_FOLDER = 'models'
    DETECT_FOLDER = 'public/detect'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 16MB
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    PORT = int(os.getenv("PORT", 10010))
