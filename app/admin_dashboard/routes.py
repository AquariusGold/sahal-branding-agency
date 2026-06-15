from flask import render_template, request
from flask_login import login_required, current_user
from app.admin_dashboard import admin_dashboard
from app.auth.decorators import role_required
from app.utils.device import is_mobile

@admin_dashboard.route("/")
@admin_dashboard.route("/dashboard")
@login_required
@role_required("admin")
def dashboard():
    """Admin Dashboard Home"""
    template_path = "mobile/admin/dashboard.html" if is_mobile(request) else "desktop/admin/dashboard.html"
    return render_template(template_path, user=current_user, title="Admin Dashboard")

@admin_dashboard.route("/users")
@login_required
@role_required("admin")
def users():
    """User Management Skeleton"""
    template_path = "mobile/admin/users.html" if is_mobile(request) else "desktop/admin/users.html"
    return render_template(template_path, user=current_user, title="User Management")

@admin_dashboard.route("/orders")
@login_required
@role_required("admin")
def orders():
    """Order Management Skeleton"""
    template_path = "mobile/admin/orders.html" if is_mobile(request) else "desktop/admin/orders.html"
    return render_template(template_path, user=current_user, title="Order Management")
