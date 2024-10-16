import uuid
from flask import Flask, request, jsonify, send_from_directory
import os
from datetime import datetime, timedelta
from ultralytics import YOLO
import json
app = Flask(__name__, static_url_path='/public', static_folder='/public')
app.config['UPLOAD_FOLDER'] = 'public/uploads'
app.config['MODEL_FOLDER'] = 'models'
app.config['DETECT_FOLDER'] = 'public/detect'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16MB


DEBUG = os.getenv("DEBUG", "false").lower() == "true" # Set to true to enable debug logging
PORT = os.getenv("PORT", 10010)  # Port to run the server on

# Cache to store models and last accessed times
model_cache = {}
model_access_time = {}


# noinspection PyTypeChecker
def get_model(model_name):
    # Check if model is in cache and update last accessed time
    if model_name in model_cache:
        model_access_time[model_name] = datetime.now()
        return model_cache[model_name]

    # Load the model and store it in the cache
    model_path = os.path.join(app.config['MODEL_FOLDER'], 'detect', model_name + '.pt')
    if not os.path.exists(model_path):
        return None

    model = YOLO(model_path)
    model_cache[model_name] = model
    model_access_time[model_name] = datetime.now()  # Set access time
    return model

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
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

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
@app.route("/")
def index():
    return jsonify({"message": "server is running"})

@app.route("/upload", methods=['POST'])
def upload():
    print(request.files)
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"})
    newFileName = uuid.uuid4().hex + os.path.splitext(file.filename)[1]
    print({newFileName})
    file.save(app.config['UPLOAD_FOLDER'] + '/' + newFileName)
    return jsonify({"message": "file uploaded", "filename": newFileName})

# noinspection PyTypeChecker
@app.route("/detect", methods=['POST'])
def detect():
    clean_up_folder(app.config['DETECT_FOLDER'])
    clean_up_folder(app.config['UPLOAD_FOLDER'])
    body = request.json
    file_name = body['file']
    model_name = body['model']

    # Clean up cache for models not used in the past max_age_hours
    clean_model_cache(max_age_hours=2)

    model = get_model(model_name)
    if model is None:
        return jsonify({"error": "Model not found"}), 404

    image_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    if not os.path.exists(image_path):
        return jsonify({"error": "Image not found"}), 404

    results = model.predict(image_path)
    detection_speed = results[0].speed

    unique_filename = f'detected_{uuid.uuid4().hex}_{file_name}'
    output_image_path = os.path.join(app.config['DETECT_FOLDER'], unique_filename).replace('\\', '/')
    for result in results:
        print("save path:" + output_image_path)
        result.save(filename=output_image_path)

    # Get Rectangles and Classes to json for response
    respJson = []
    # get boxes and classes from results
    for detection in results[0].boxes:
        x, y, w, h = detection.xywh.tolist()[0]
        confidence = detection.conf.tolist()[0]
        class_id = int(detection.cls.tolist()[0])
        class_name = model.names[class_id]

        # Add the bounding box data and class to the response
        respJson.append({
            "bbox": {"x": x, "y": y, "w": w, "h": h},
            "confidence": confidence,
            "class_id": class_id,
            "class_name": class_name
        })
    boxes_json_string = results[0].to_json()
    boxes_json = json.loads(boxes_json_string)

    return jsonify({"message": "detecting",
                    "results": respJson,
                    "boxes": boxes_json,
                    "output_image": output_image_path,
                    "detection_speed": detection_speed})

@app.route("/uploads/<filename>", methods=['GET'])
def get_image(filename):
    print(filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=DEBUG, host='0.0.0.0', port=PORT)