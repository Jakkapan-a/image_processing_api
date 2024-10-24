from flask import Blueprint, request, jsonify, current_app, send_from_directory
import uuid
import os
from app.models.file_management import FileManagement
classify_bp = Blueprint('classify', __name__)

# noinspection DuplicatedCode
@classify_bp.route('/', methods=['POST'])
def classify():
    from app import db
    data = request.json
    name = data.get('name')
    filename = data.get('filename')
    filepath = data.get('filepath')
    file_type = data.get('file_type') #
    filename = filename +"_"+uuid.uuid4().hex + os.path.splitext(filename)[1]
    file = FileManagement(name=name, filename=filename, filepath=filepath, file_type=file_type)

    db.session.add(file)
    db.session.commit()


    return jsonify({"message": "classify", "data": file.to_dict()}), 201

# Compare this snippet from app/services/model_loader.py:

@classify_bp.route('/test', methods=['GET'])
def classify_test():
    return jsonify({"message": "classify-test"})
