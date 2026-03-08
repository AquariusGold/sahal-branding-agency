# =============================================================================
# app/admin/__init__.py
# =============================================================================
# WHY THIS EXISTS:
#   The Admin module is the back-office dashboard. It will manage:
#   - Order/project tracking
#   - Client management
#   - Email campaign controls
#   - System configuration
#   All admin routes live under /admin and will require superuser privileges.
# =============================================================================

from flask import Blueprint

admin = Blueprint("admin", __name__, url_prefix="/admin")

from app.admin import routes  # noqa: F401, E402
