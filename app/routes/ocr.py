# Desc: OCR route
from flask import Blueprint, jsonify,request
from PIL import Image
import pytesseract
import io


ocr_bp = Blueprint('ocr', __name__)

@ocr_bp.route('', methods=['POST'])
def ocr():
    if 'image' not in request.files:
        return jsonify({"error": "No image part"}), 400

    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({"error": "Invalid image"}), 400
    # OCR code here
    try:
        image = Image.open(io.BytesIO(image_file.read()))

        text = pytesseract.image_to_string(image, lang='eng')

        print({"text": text})
        return jsonify({"text": text, "message": "OCR successful"}), 200
    except Exception as e:
        print("Error: ", str(e))
        return jsonify({"error": str(e)}), 500