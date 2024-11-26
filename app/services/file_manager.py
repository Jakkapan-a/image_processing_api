import os
from datetime import datetime, timedelta

from PIL import Image
from flask import current_app

def clean_up_folder(folder, max_age_days=15):
    try:
        now = datetime.now()
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if now - file_time >= timedelta(days=max_age_days):
                    os.remove(file_path)
                    current_app.logger.info(f"Removed old file: {file_path}")
                    print(f"Removed old file: {file_path}")
    except Exception as e:
        print(f"Error cleaning up folder {folder}: {e}")

ALLOWED_EXTENSIONS = { 'jpg', 'png', 'pt'} # set of allowed file extensions


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clean_up_temp_folder():
    clean_up_folder('public/temp',1)

def clean_up_width_db(folder):
    try:
        from app import db
        from app.models.file_management import FileManagement

        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                file_query = FileManagement.query.filter_by(filename=filename).first()
                if not file_query:
                    os.remove(file_path)
                    print(f"Removed file: {file_path}")
    except Exception as e:
        print(f"Error cleaning up folder {folder}: {e}")
