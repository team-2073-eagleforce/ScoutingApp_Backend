from flask import Blueprint

google_bp = Blueprint(
    'google_bp', __name__,
    template_folder='templates',
    static_folder='static'
)
