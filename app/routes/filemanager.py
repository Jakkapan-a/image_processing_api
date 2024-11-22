import os

from flask import Blueprint, jsonify, request

from app.routes.upload import merge_chunks

filemanager_bp = Blueprint('filemanager', __name__, url_prefix='/filemanager')

@filemanager_bp.route('/')
def filemanager():
    return jsonify({"message": "File Manager route"})

@filemanager_bp.route('/list')
def list_files():
    return jsonify({"message": "List files route"})

@filemanager_bp.route('/name-exists', methods=['GET'])
def name_exists():
    try:
        # get query params
        name = request.args.get('name')
        model_name = request.args.get('model_name')
        from app.models.file_management import FileManagement
        # Check name exists where name is not equal to model_name
        file = FileManagement.query.filter(FileManagement.name == name, FileManagement.filename != model_name).first()

        if file is None:
            return jsonify({"message": "Name is unique", "exists": False}), 200
        else:
            return jsonify({"message": "Name exists", "exists": True}), 200
    except Exception as e:
        print("Error checking if name exists", e)

    return jsonify({"message": "Name exists route"}), 400


@filemanager_bp.route('/upload-chunk-model', methods=['POST'])
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
        filename = filename.split('.')[0]

        temp_filename = f"{filename}_{chunk_number}{extension}"
        file.save(os.path.join(path_temp, temp_filename))

        if chunk_number == total_chunks - 1:
            path_models = os.path.join('models', file_type)
            new_filename_model = merge_chunks(filename, total_chunks, path_temp, path_models, extension)
            #
            from app import db
            from app.models.file_management import FileManagement

            file = FileManagement(name=name, filename=new_filename_model, filepath=path_models, file_type=file_type, description=description)
            db.session.add(file)
            db.session.commit()
            print("file_record", file.to_dict())

            return jsonify({"message": "File uploaded and merged successfully",
                            "filename": file.to_dict(), "type": "model"}), 201

        return jsonify({"message": "Chunk uploaded successfully",
                        "filename": temp_filename, "type": "chunk"}), 201

    except Exception as e:
        print('error upload_chunk_model', e)
        return jsonify({"error": str(e)}), 500

@filemanager_bp.route('/upload/<int:file_id> /image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    try:
        file = request.files['file']
        name = request.form.get('name')
        description = request.form.get('description', '')
        filename = request.form.get('filename', 'uploaded_file')

        extension = os.path.splitext(file.filename)[1]
        file_type = request.form.get('file_type', 'cls') # cls, detect

        path_models = os.path.join('models', file_type)
        if not os.path.exists(path_models):
            os.makedirs(path_models)

        new_filename = f"{filename}{extension}"
        file.save(os.path.join(path_models, new_filename))

        from app import db
        from app.models.file_management import FileManagement

        file = FileManagement(name=name, filename=new_filename, filepath=path_models, file_type=file_type, description=description)
        print("file_record", file.to_dict())
        db.session.add(file)
        db.session.commit()

        return jsonify({"message": "File uploaded successfully",
                        "filename": file.to_dict(), "type": "image"}), 201

    except Exception as e:
        print('error upload_image', e)
        return jsonify({"error": str(e)}), 500