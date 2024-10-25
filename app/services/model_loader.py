import os
from ultralytics import YOLO
from datetime import datetime, timedelta

model_cache = {}
model_access_time = {}

def clean_model_cache(max_age_hours=2):
    current_time = datetime.now()
    to_delete = []

    for model_name, access_time in model_access_time.items():
        if current_time - access_time > timedelta(hours=max_age_hours):
            to_delete.append(model_name)

    for model_name in to_delete:
        del model_cache[model_name]
        del model_access_time[model_name]
        print(f"Removed model from cache: {model_name}")

# noinspection PyTypeChecker
def get_model(model_name, model_folder):
    # Check if model is in cache and update last accessed time
    if model_name in model_cache:
        model_access_time[model_name] = datetime.now()
        return model_cache[model_name]

    # Load the model and store it in the cache
    model_path = os.path.join(model_folder, model_name)
    if not os.path.exists(model_path):
        return None

    model = YOLO(model_path)
    model_cache[model_name] = model
    model_access_time[model_name] = datetime.now()  # Set access time
    return model
