import os
import uuid
from tkinter import image_names

from flask import Blueprint, jsonify, request
from sqlalchemy import or_

from app.routes.upload import merge_chunks

filemanager_bp = Blueprint('filemanager', __name__, url_prefix='/filemanager')

@filemanager_bp.route('/')
def filemanager():
    return jsonify({"message": "File Manager route"})


# noinspection DuplicatedCode
@filemanager_bp.route('/list')
def list_files():
    try:
        from app.models.file_management import FileManagement
        # http://domain.com/api/filemanager/list?page=1&per_page=20&search_name=filename
        current_page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search_name = request.args.get('search', "")

        _files = FileManagement.query.filter(
            or_(

                FileManagement.name.ilike(f"%{search_name}%"),
                FileManagement.model_name.ilike(f"%{search_name}%"),
                FileManagement.description.ilike(f"%{search_name}%"),
                FileManagement.file_type.ilike(f"%{search_name}%")
            )
        ).order_by(FileManagement.updated_at.desc()).paginate(page=current_page, per_page=per_page)

        return jsonify({
            "files": [file.to_dict() for file in _files.items],
            "total": _files.total,
            "pages": _files.pages,
            "current_page": _files.page,
        })
    except Exception as e:
        print("Error listing files", e)

    return jsonify({"message": "List files route"})

@filemanager_bp.route('/name-exists', methods=['GET'])
def name_exists():
    try:
        # get query params
        name = request.args.get('name')
        model_name = request.args.get('model_name')
        from app.models.file_management import FileManagement
        # Check name exists where name is not equal to model_name
        file = FileManagement.query.filter(FileManagement.name == name, FileManagement.model_name == model_name).first()

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
        model_name = request.form.get('model_name', '')

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

            image = request.files.get('image')
            new_filename_image = ""
            if image:
                extension_image = os.path.splitext(image.filename)[1]
                filename_image = filename.split('.')[0]
                new_filename_image = f"{filename_image}_{uuid.uuid4()}{extension_image}"
                if not os.path.exists(os.path.join('public', 'images')):
                    os.makedirs(os.path.join('public', 'images'))
                image.save(os.path.join('public', 'images', new_filename_image))




            # Save file record to database
            from app import db
            from app.models.file_management import FileManagement

            file = FileManagement(name=name, filename=new_filename_model, filepath=path_models, file_type=file_type, description=description, model_name=model_name,image_name=new_filename_image)
            db.session.add(file)
            db.session.commit()
            print("file_record", file.to_dict())

            return jsonify({"message": "File uploaded and merged successfully",
                            "filename": file.to_dict(), "type": "model",
                            "image_url": f"/images/{new_filename_image}"}), 201

        return jsonify({"message": "Chunk uploaded successfully",
                        "filename": temp_filename, "type": "chunk"}), 201

    except Exception as e:
        print('error upload_chunk_model', e)
        return jsonify({"error": str(e)}), 500

