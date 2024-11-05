from flask import Blueprint, jsonify

appOCR = Blueprint('ocr', __name__)

@appOCR.route('/ocr', methods=['POST'])
def ocr():
    return jsonify({"message": "ocr"}), 200