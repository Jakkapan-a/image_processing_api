from flask import Blueprint, request, jsonify, current_app, send_from_directory

index_app = Blueprint('index', __name__)

@index_app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "server is running"}), 200