import io

from PIL import Image
from flask import Blueprint, request, jsonify, current_app, send_from_directory
import uuid
import os

from app.services.model_loader import get_model, clean_model_cache
from app.services.file_manager import allowed_file


classify_bp = Blueprint('classify', __name__)
# noinspection DuplicatedCode
@classify_bp.route('', methods=['POST'])
def classify():
    # from app import db
    data = request.json
    # _id = 16
    _id = data.get('id')
    filename = data.get('filename')
    current_app.logger.info(f'cls filename: {filename}, id: {_id}')

    from app.models.file_management import FileManagement
    # Get the file name from the database
    file = FileManagement.query.get(_id)
    if file is None:
        current_app.logger.error(f'File not found: {filename}')
        return jsonify({"error": "File not found"}), 404

    path_cls = 'models/cls'
    current_app.logger.info(f'path_cls: {path_cls}')
    # Load the model
    model = get_model(model_name=file.filename, model_folder=path_cls)
    if model is None:
        return jsonify({"error": "Model not found"}), 404
    path_filename =   os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    # Get the image path
    results = model.predict(path_filename)
    #
    detection_speed = results[0].speed
    # get file name from url image
    #
    print('detection_speed', detection_speed)
    # # Get the class name
    unique_filename = f'cls_{uuid.uuid4().hex}_{filename}'
    # output_image_path = os.path.join(current_app.config['DETECT_FOLDER'], unique_filename).replace('\\', '/')
    # for result in results:
    #     print("save path:" + output_image_path)
    #     result.save(filename=output_image_path)

    clean_model_cache(max_age_hours=2)
    # remove file
    os.remove(path_filename)
    print('results', results[0].to_json())
    return jsonify({"message": "classify", "results": results[0].to_json(), "filename": unique_filename})

# Compare this snippet from app/services/model_loader.py:
@classify_bp.route('/image', methods=['POST'])
def classifyUp():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    image_file = request.files['file']
    if image_file.filename == '' or not allowed_file(image_file.filename):
        return jsonify({"error": "Invalid file"}), 400

    try:
        data = request.form
        print('data', data)
        _id = data.get('id')
        _id = 15
        print('id', _id)
        image = Image.open(io.BytesIO(image_file.read()))
        # Load the model
        from app.models.file_management import FileManagement
        # Get the file name from the database
        fileYolo = FileManagement.query.get(_id)
        if fileYolo is None:
            current_app.logger.error(f'File not found: {fileYolo}')
            return jsonify({"error": "File not found"}), 404

        path_cls = 'models/cls'
        current_app.logger.info(f'path_cls: {path_cls}')
        # Load the model
        model = get_model(model_name=fileYolo.filename, model_folder=path_cls)
        if model is None:
            return jsonify({"error": "Model not found"}), 404

        results = model.predict(image)

        detection_speed = results[0].speed
        # Get the class name
        unique_filename = f'cls_{uuid.uuid4().hex}_{image_file.filename}'

        return jsonify({"message": "classify", "results": results[0].to_json(), "filename": unique_filename})

    except Exception as e:
        print("Error: ", str(e))
        return jsonify({"error": str(e)}), 500
