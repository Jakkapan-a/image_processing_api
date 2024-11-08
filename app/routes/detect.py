from flask import Blueprint, request, jsonify, current_app, send_from_directory
import uuid
import os
from app.services.model_loader import get_model, clean_model_cache
from app.services.file_manager import clean_up_folder
import json
detect_bp = Blueprint('detect', __name__)

# noinspection DuplicatedCode
@detect_bp.route('/detect', methods=['POST'])
def detect():
    clean_up_folder('public/detect')
    clean_up_folder('public/uploads')

    body = request.json
    file_name = body.get('file')
    model_name = body.get('model')

    clean_model_cache(max_age_hours=2)

    model = get_model(model_name,model_folder='models')
    if not model:
        return jsonify({"error": "Model not found"}), 404

    image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_name)
    if not os.path.exists(image_path):
        return jsonify({"error": "Image not found"}), 404

    results = model.predict(image_path)
    detection_speed = results[0].speed

    # unique_filename = f'detected_{uuid.uuid4().hex}_{file_name}'
    # output_image_path = os.path.join(current_app.config['DETECT_FOLDER'], unique_filename).replace('\\', '/')
    # for result in results:
    #     print("save path:" + output_image_path)
    #     result.save(filename=output_image_path)

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
                    "detection_speed": detection_speed})

@detect_bp.route('/detect/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory('../public/detect', filename)