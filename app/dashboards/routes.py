# =============================================================================
# app/dashboards/routes.py
# =============================================================================
from flask import render_template, request
from flask_login import login_required, current_user
from app.dashboards import dashboards
from app.auth.decorators import role_required
from app.utils.device import is_mobile


@dashboards.route("/client")
@login_required
@role_required("client")
def client():
    """
    Client dashboard.
    Shows the user's active projects, proposals, etc.
    """
    # Let device detection handle nested pathing (this requires template naming consistency)
    # The factory context processor already passes `is_mobile` to all templates,
    # but since Jinja2 expects an exact file path, we'll route it here directly
    # for simplicity exactly as requested in Phase 2 specs.
    if is_mobile(request):
        return render_template("mobile/dashboards/client_dashboard.html", user=current_user)
    return render_template("desktop/dashboards/client_dashboard.html", user=current_user)


@dashboards.route("/admin")
@login_required
@role_required("admin")
def admin():
    """
    Admin dashboard.
    High-level metrics, user management, and global system configuration.
    """
    if is_mobile(request):
        return render_template("mobile/dashboards/admin_dashboard.html", user=current_user)
    return render_template("desktop/dashboards/admin_dashboard.html", user=current_user)
