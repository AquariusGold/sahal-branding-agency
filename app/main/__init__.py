# =============================================================================
# app/main/__init__.py
# =============================================================================
# WHY BLUEPRINTS?
#   Flask Blueprints are the standard way to split a large application into
#   independently maintainable components. Each blueprint owns its own routes,
#   templates, and static files. They are registered in create_app() and
#   can carry a url_prefix ("/", "/auth", "/admin", etc.).
#
# This is the "main" blueprint — it handles public-facing pages:
#   GET /          → homepage (device-aware)
#   (future) GET /about, /contact, etc.
# =============================================================================

from flask import Blueprint

# Blueprint name: "main" — used in url_for("main.index"), etc.
# template_folder is relative to this package; Flask resolves it automatically.
main = Blueprint("main", __name__)

# Import routes AFTER creating the Blueprint to avoid circular imports.
# The routes module registers view functions onto `main`.
from app.main import routes  # noqa: F401, E402
