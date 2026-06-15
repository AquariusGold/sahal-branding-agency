from flask import render_template, request
from flask_login import login_required, current_user
from app.user_dashboard import user_dashboard
from app.auth.decorators import role_required
from app.utils.device import is_mobile

@user_dashboard.route("/")
@user_dashboard.route("/home")
@login_required
@role_required("client")
def dashboard():
    """User Dashboard Home"""
    template_path = "mobile/user/dashboard.html" if is_mobile(request) else "desktop/user/dashboard.html"
    return render_template(template_path, user=current_user, title="My Dashboard")

@user_dashboard.route("/orders")
@login_required
@role_required("client")
def orders():
    """User Orders History Skeleton"""
    template_path = "mobile/user/orders.html" if is_mobile(request) else "desktop/user/orders.html"
    return render_template(template_path, user=current_user, title="My Orders")
