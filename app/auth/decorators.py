# =============================================================================
# app/auth/decorators.py
# =============================================================================
# WHY THIS EXISTS:
#   Custom decorators for route protection. While Flask-Login's @login_required
#   ensures a user is logged in, it doesn't check WHO they are.
#   These decorators extend functionality to enforce Role-Based Access Control
#   (RBAC).
# =============================================================================

from functools import wraps
from flask import abort
from flask_login import current_user, login_required

def role_required(required_role: str):
    """
    Decorator to restrict access to a specific user role.
    Must be placed AFTER @login_required.
    
    Example:
        @app.route("/admin")
        @login_required
        @role_required("admin")
        def admin_panel():
            pass
            
    Args:
        required_role (str): The string value of the UserRole enum required.
                             e.g., "admin", "client", "staff".
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # If the user is somehow not logged in (e.g., they didn't use 
            # @login_required, or accessed it directly), deny access.
            if not current_user.is_authenticated:
                return abort(401)
                
            # Check if their role enum value matches the required string
            if current_user.role.value != required_role:
                # 403 Forbidden: Server understands the request, but refuses 
                # to authorize it (they are logged in, but lack permissions).
                return abort(403)
                
            return func(*args, **kwargs)
        return wrapper
    return decorator
