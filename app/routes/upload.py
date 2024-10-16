from flask import Blueprint, request, jsonify, send_from_directory
import uuid
import os
from app.services.file_manager import allowed_file

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file"}), 400

    new_filename = uuid.uuid4().hex + os.path.splitext(file.filename)[1]
    file.save(os.path.join('public/uploads', new_filename))

    return jsonify({"message": "file uploaded", "filename": new_filename})

@upload_bp.route('/uploads/<filename>', methods=['GET'])
def get_upload(filename):
    return send_from_directory('public/uploads', filename)

