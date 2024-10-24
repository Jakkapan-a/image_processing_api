# Route initialization

from flask import Blueprint
from .upload import upload_bp
from .detect import detect_bp
from .classify import classify_bp
from .index import index_app

# # Blueprint Configuration
# routes_bp = Blueprint('routes', __name__)

