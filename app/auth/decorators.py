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

def role_required(allowed_roles):
    """
    Decorator to restrict access to specific user roles.
    Must be placed AFTER @login_required.
    
    Admins are ALWAYS allowed access regardless of the allowed_roles list.
    
    Args:
        allowed_roles (str or list): A single role string or a list of role strings.
                                     e.g., "staff" or ["staff", "client"].
    """
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return abort(401)
                
            # Admins have global access
            if current_user.role.value == "admin":
                return func(*args, **kwargs)

            # Check if their role is in the allowed list
            if current_user.role.value not in allowed_roles:
                return abort(403)
                
            return func(*args, **kwargs)
        return wrapper
    return decorator
