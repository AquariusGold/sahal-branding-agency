# =============================================================================
# app/services/__init__.py
# =============================================================================
# WHY THIS EXISTS:
#   The Services module represents SAHAL's public service catalog:
#   branding packages, design services, consultation booking, etc.
#   Future routes will live under /services (/services/, /services/<slug>).
# =============================================================================

from flask import Blueprint

services = Blueprint("services", __name__, url_prefix="/services")

from app.services import routes  # noqa: F401, E402
