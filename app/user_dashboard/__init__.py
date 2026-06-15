from flask import Blueprint

user_dashboard = Blueprint('user_dashboard', __name__, url_prefix='/dashboard')

from app.user_dashboard import routes
