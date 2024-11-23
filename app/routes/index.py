import os

from flask import Blueprint, request, jsonify, current_app, send_from_directory

index_app = Blueprint('index', __name__)
from app.services.file_manager import clean_up_folder,clean_up_temp_folder
@index_app.route('/', methods=['GET'])
def index():
    clean_up_temp_folder()
    return jsonify({"message": "server is running"}), 200
@index_app.route('/api', methods=['GET'])
def api():
    return jsonify({"message": "api is running"}), 200

@index_app.route('/images/<filename>', methods=['GET'])
def images(filename):
    print("filename", filename)
    # path = os.path.join('public/uploads', filename)
    # if not os.path.exists(path):
    #     print("File not found")
    #     return jsonify({"error": "File not found"}), 404
    # else:
    #     print("File found")

    return send_from_directory('../public/images', filename)

@index_app.route('/clean', methods=['GET'])
def clean():
    clean_up_folder('public/detect',0)
    clean_up_folder('public/uploads',0)
    return jsonify({"message": "cleaned"}), 200