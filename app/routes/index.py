from flask import Blueprint, request, jsonify, current_app, send_from_directory

index_app = Blueprint('index', __name__)
from app.services.file_manager import clean_up_folder,clean_up_temp_folder
@index_app.route('/', methods=['GET'])
def index():
    clean_up_folder('public/detect',1)
    clean_up_folder('public/uploads',1)

    clean_up_temp_folder()
    return jsonify({"message": "server is running"}), 200