# =============================================================================
# app/dashboards/__init__.py
# =============================================================================
from flask import Blueprint

dashboards = Blueprint("dashboards", __name__, url_prefix="/dashboard")

from app.dashboards import routes
