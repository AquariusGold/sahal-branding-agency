from flask import render_template, request
from flask_login import login_required, current_user
from app.staff_dashboard import staff_dashboard
from app.auth.decorators import role_required
from app.utils.device import is_mobile

@staff_dashboard.route("/")
@staff_dashboard.route("/dashboard")
@login_required
@role_required("staff")
def dashboard():
    """Staff Dashboard Home"""
    template_path = "mobile/staff/dashboard.html" if is_mobile(request) else "desktop/staff/dashboard.html"
    return render_template(template_path, user=current_user, title="Staff Dashboard")

@staff_dashboard.route("/tasks")
@login_required
@role_required("staff")
def tasks():
    """Tasks Management Skeleton"""
    template_path = "mobile/staff/tasks.html" if is_mobile(request) else "desktop/staff/tasks.html"
    return render_template(template_path, user=current_user, title="My Tasks")
