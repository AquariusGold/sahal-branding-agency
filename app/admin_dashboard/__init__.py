from flask import Blueprint

admin_dashboard = Blueprint('admin_dashboard', __name__, url_prefix='/admin')

from app.admin_dashboard import routes
