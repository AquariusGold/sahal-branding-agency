# =============================================================================
# app/auth/__init__.py
# =============================================================================
# WHY THIS EXISTS:
#   Authentication (login, logout, registration, password reset) is a distinct
#   concern from public content. Isolating it in its own blueprint lets us:
#     - Apply auth-specific middleware/decorators in one place.
#     - Prefix all auth routes with /auth (e.g. /auth/login, /auth/logout).
#     - Easily swap or upgrade the auth strategy without touching other modules.
# =============================================================================

from flask import Blueprint

auth = Blueprint("auth", __name__, url_prefix="/auth")

# Import routes after Blueprint creation to avoid circular imports.
from app.auth import routes  # noqa: F401, E402
