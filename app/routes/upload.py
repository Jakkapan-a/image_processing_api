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


def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def merge_chunks(filename, total_chunks, path_temp, path_models, extension):
    if not os.path.exists(path_models):
        os.makedirs(path_models)

    new_filename_model = f"{filename}_{uuid.uuid4()}{extension}"
    new_filename_model = new_filename_model.replace(" ", "_").replace("-", "_")
    with open(os.path.join(path_models, new_filename_model), 'wb') as final_file:
        for i in range(total_chunks):
            temp_chunk_path = os.path.join(path_temp, f"{filename}_{i}{extension}")
            print("temp_chunk_path", temp_chunk_path)
            with open(temp_chunk_path, 'rb') as chunk_file:
                final_file.write(chunk_file.read())
            os.remove(temp_chunk_path)
    return new_filename_model

# ----------------- File Management ----------------- //
@upload_bp.route('', methods=['GET'])
def get_uploads():
    try:
        from app.models.file_management import FileManagement
        # http://domain.com/api/file?page=1&per_page=20&search_name=filename
        current_page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search_name = request.args.get('search_name', "")

        _files = FileManagement.query.filter(FileManagement.name.ilike(f"%{search_name}%")).order_by(FileManagement.updated_at.desc()).paginate(page=current_page, per_page=per_page)

        return jsonify({
            "files": [file.to_dict() for file in _files.items],
            "total": _files.total,
            "pages": _files.pages,
            "current_page": _files.page
        })
    except Exception as e:
        print('error get_uploads', e)
        return jsonify({"error": str(e)}), 500


@upload_bp.route('/upload-chunk-model', methods=['POST'])
def upload_chunk_model():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    try:
        file = request.files['file']
        name = request.form.get('name')
        chunk_number = int(request.form.get('chunk_number', 0))
        total_chunks = int(request.form.get('total_chunks', 1))
        description = request.form.get('description', '')
        filename = request.form.get('filename', 'uploaded_file')

        extension = os.path.splitext(file.filename)[1]
        file_type = request.form.get('file_type', 'cls') # cls, detect

        path_temp = os.path.join('public', 'temp', file_type)
        if not os.path.exists(path_temp):
            os.makedirs(path_temp)

        temp_filename = f"{filename}_{chunk_number}{extension}"
        file.save(os.path.join(path_temp, temp_filename))

        if chunk_number == total_chunks - 1:
            path_models = os.path.join('models', file_type)
            new_filename_model = merge_chunks(filename, total_chunks, path_temp, path_models, extension)
            #
            from app import db
            from app.models.file_management import FileManagement

            file = FileManagement(name=name, filename=new_filename_model, filepath=path_models,
                                  file_type=file_type, description=description)
            print("file_record", file.to_dict())
            db.session.add(file)
            db.session.commit()

            return jsonify({"message": "File uploaded and merged successfully",
                            "filename": file.to_dict(), "type": "model"}), 201

        return jsonify({"message": "Chunk uploaded successfully",
                        "filename": temp_filename, "type": "chunk"}), 201

    except Exception as e:
        print('error upload_chunk_model', e)
        return jsonify({"error": str(e)}), 500

@upload_bp.route('/update-chunk-model', methods=['POST'])
def update_chunk_model():
    try:
        from app import db
        from app.models.file_management import FileManagement

        _id = int(request.form.get('id'))
        name = request.form.get('name')
        description = request.form.get('description')

        if not _id:
            return jsonify({"error": "ID is required"}), 400

        if not name:
            return jsonify({"error": "Name is required"}), 400

        if not description:
            return jsonify({"error": "Description is required"}), 400

        file_query = FileManagement.query.get(_id)
        if not file_query:
            return jsonify({"error": "File not found"}), 404
        new_filename = ""
        if 'file' not in request.files:
            new_filename = ""
        else:
            file = request.files['file']
            if file.filename == '' or not allowed_file(file.filename):
                return jsonify({"error": "Invalid file"}), 400

            chunk_number = int(request.form.get('chunk_number', 0))
            total_chunks = int(request.form.get('total_chunks', 1))

            filename = request.form.get('filename', 'uploaded_file')
            extension = os.path.splitext(file.filename)[1]

            file_type = request.form.get('file_type', 'cls') # cls, detect
            path_temp = os.path.join('public', 'temp')
            path_temp = os.path.join('public', 'temp', file_type)
            if not os.path.exists(path_temp):
                os.makedirs(path_temp)

            temp_filename = f"{filename}_{chunk_number}{extension}"
            file.save(os.path.join(path_temp, temp_filename))


            if chunk_number == total_chunks - 1:
                path_models = os.path.join('models', file_type)
                new_filename = merge_chunks(filename, total_chunks, path_temp, path_models, extension)
            else:
                return jsonify({"message": "Chunk uploaded successfully",
                                "filename": temp_filename, "type": "chunk"}), 201

        # Check has new filename or not and update the record and remove the old file
        if new_filename:
            if os.path.exists(os.path.join(file_query.filepath, file_query.filename)):
                os.remove(os.path.join(file_query.filepath, file_query.filename))

            file_query.filename = new_filename
        else:
            new_filename = file_query.filename

        file_query.filename = new_filename
        file_query.name = name
        file_query.description = description
        db.session.commit()

        return jsonify({"message": "File updated successfully", "data": file_query.to_dict()}), 200
    except Exception as e:
        print('error update_chunk_model', e)
        return jsonify({"error": str(e)}), 500

