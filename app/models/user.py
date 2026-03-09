# =============================================================================
# app/models/user.py
# =============================================================================
# WHY THIS EXISTS:
#   Defines the core User entity for authentication, sessions, and access control.
#   Uses Flask-Login's UserMixin to automatically provide property implementations
#   like `is_authenticated`, `is_active`, `is_anonymous`, and `get_id()`.
#
# ROLE-BASED ACCESS CONTROL (RBAC):
#   The `role` field dictates what the user can see and do.
#     - admin : full access to backend dashboards and settings
#     - staff : limited backend access (e.g. processing orders)
#     - client : frontend portal access only
# =============================================================================

import enum
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db


class UserRole(enum.Enum):
    """
    Enum for User Roles.
    Using enums prevents typos ("admin" vs "Admin") and restricts the DB column
    to valid values only.
    """
    admin = "admin"
    staff = "staff"
    client = "client"

class AccountType(enum.Enum):
    """
    Enum for Account Types during registration.
    """
    personal = "personal"
    business = "business"


class User(db.Model, UserMixin):
    """
    User model for authentication and identity.
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    
    # Email is unique and indexed for fast login lookups
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    
    # We never store plain text passwords; this holds the bcrypt/scrypt hash
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Role dictates permissions. Default is 'client' for self-registered users.
    role = db.Column(db.Enum(UserRole), default=UserRole.client, nullable=False)

    # -------------------------------------------------------------------------
    # Account Type & Registration Fields
    # -------------------------------------------------------------------------
    account_type = db.Column(db.Enum(AccountType), default=AccountType.personal, nullable=False)
    
    # Personal & Business Shared Optional
    phone_number = db.Column(db.String(20), nullable=True)
    
    # Business Specific Optional
    company_name = db.Column(db.String(120), nullable=True)
    company_website = db.Column(db.String(255), nullable=True)
    industry = db.Column(db.String(120), nullable=True)
    
    # Soft delete or suspension support
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Audit trail
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def set_password(self, password: str) -> None:
        """
        Hashes the provided plain-text password and stores it.
        Uses Werkzeug's secure hashing algorithm defaults.
        """
        self.password_hash = generate_password_hash(password)

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.admin

    @property
    def is_staff(self) -> bool:
        return self.role == UserRole.staff or self.role == UserRole.admin

    @property
    def is_client(self) -> bool:
        return self.role == UserRole.client

    def check_password(self, password: str) -> bool:
        """
        Verifies a plain-text password against the stored hash.
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email} (Role: {self.role.value})>"
