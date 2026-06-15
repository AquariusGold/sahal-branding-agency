from flask import Blueprint

staff_dashboard = Blueprint('staff_dashboard', __name__, url_prefix='/staff')

from app.staff_dashboard import routes
