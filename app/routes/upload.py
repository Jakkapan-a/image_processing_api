from importlib.metadata import files
from re import search

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

@upload_bp.route('', methods=['GET'])
def get_uploads():
    from app.models.file_management import FileManagement

    current_page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search_name = request.args.get('search_name', "")

    _files = FileManagement.query.filter(FileManagement.name.ilike(f"%{search_name}%")).paginate(page=current_page, per_page=per_page)

    return jsonify({
        "files": [file.to_dict() for file in _files.items],
        "total": _files.total,
        "pages": _files.pages,
        "current_page": _files.page
    })
@upload_bp.route('/upload-chunk-model', methods=['POST'])
def upload_chunk_model():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    name = request.form.get('name')
    chunk_number = int(request.form.get('chunk_number'))
    total_chunks = int(request.form.get('total_chunks'))
    extension = os.path.splitext(file.filename)[1]
    description = request.form.get('description')


    file_type = "cls" # detect, cls
    path_temp = os.path.join('public', 'temp', file_type)
    if not os.path.exists(path_temp):
        os.makedirs(path_temp)

    new_filename = request.form.get('filename')
    new_filename = new_filename.replace(' ', '_').replace('(', '').replace(')', '')
    new_filename = f"{new_filename}_{chunk_number}"

    file.save(os.path.join(path_temp, new_filename))

    if chunk_number == total_chunks:
        path_models = os.path.join('models', file_type)
        if not os.path.exists(path_models):
            os.makedirs(path_models)
        new_filename_model = f"{new_filename}_{uuid.uuid4()}.{extension}"
        with open(os.path.join(path_models, new_filename_model), 'wb') as f:
            for i in range(1, total_chunks + 1):
                with open(os.path.join(path_temp, f"{new_filename}_{i}"), 'rb') as chunk:
                    f.write(chunk.read())
                os.remove(os.path.join(path_temp, f"{new_filename}_{i}"))

        from app.models.file_management import FileManagement

        file = FileManagement(name=name, filename=new_filename_model, filepath=path_models, file_type=file_type,description=description)
        file.session.add(file)
        file.session.commit()

        return jsonify({"message": "file uploaded", "filename": new_filename_model,"type": "model"}), 201

    return jsonify({"message": "file uploaded", "filename": new_filename, "type": "chunk"}), 201

