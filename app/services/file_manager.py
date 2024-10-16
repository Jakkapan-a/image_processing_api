import os
from datetime import datetime, timedelta

def clean_up_folder(folder, max_age_days=30):
    try:
        now = datetime.now()
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if now - file_time > timedelta(days=max_age_days):
                    os.remove(file_path)
                    print(f"Removed old file: {file_path}")
    except Exception as e:
        print(f"Error cleaning up folder {folder}: {e}")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}