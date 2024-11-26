import os

from PIL import Image
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from six import print_

index_app = Blueprint('index', __name__)
from app.services.file_manager import clean_up_folder, clean_up_temp_folder


@index_app.route('/', methods=['GET'])
def index():
    clean_up_temp_folder()
    return jsonify({"message": "server is running"}), 200
@index_app.route('/api', methods=['GET'])
def api():
    return jsonify({"message": "api is running"}), 200


@index_app.route('/clean', methods=['GET'])
def clean():
    clean_up_folder('public/detect',0)
    clean_up_folder('public/uploads',0)
    return jsonify({"message": "cleaned"}), 200


@index_app.route('/images/<filename>', methods=['GET'])
def images(filename):
    print(f"path: ../public/images/{filename}")
    return send_from_directory('../public/images', filename)

# Base image directory
IMAGE_DIR = "public/images/"

@index_app.route('/images/<size>/<filename>', methods=['GET'])
def sizeImages(size, filename):
    """Serve resized images based on the requested size."""
    size_map = {
        'thumbnail': (150, 100),
        'small': (300, 200),
        'large': (600, 400),
    }
    if size not in size_map:
        return jsonify({'error': 'Invalid size requested'}), 400

    # Check if the resized image already exists
    target_dir = os.path.join(IMAGE_DIR, size)
    target_path = os.path.join(target_dir, filename)
    if not os.path.exists(target_path):
        # Create the resized image if it doesn't exist
        original_path = IMAGE_DIR + filename
        if not os.path.exists(original_path):
            return jsonify({'error': 'Original image not found'}), 404
        create_resized_image(filename, size_map[size], size)
    # Serve the resized image
    return send_from_directory("../"+target_dir, filename)

def create_resized_image(filename, size, folder):
    """Create resized image and save it in the target folder."""
    original_path = IMAGE_DIR + filename
    target_dir = os.path.join(IMAGE_DIR, folder)
    target_path = os.path.join(target_dir, filename)

    # Create target directory if it doesn't exist
    os.makedirs(target_dir, exist_ok=True)
    # Resize and save image
    try:
        # Open and resize the image
        with Image.open(original_path) as img:
            img.thumbnail(size)  # Resize the image
            img.save(target_path)  # Save the resized image
    except Exception as e:
        raise RuntimeError(f"Error processing image {filename}: {e}")

    return target_path