# =============================================================================
# app/config.py
# =============================================================================
# WHY THIS FILE EXISTS:
#   Flask supports multiple environments (development, testing, production).
#   Instead of scattering configuration across the codebase, we centralize
#   it here using Python classes with inheritance.
#
# HOW IT WORKS:
#   - BaseConfig holds shared settings loaded from environment variables.
#   - DevelopmentConfig, TestingConfig, ProductionConfig extend BaseConfig
#     with environment-specific overrides.
#   - create_app() (in app/__init__.py) selects the right config class at
#     startup based on the FLASK_ENV environment variable.
# =============================================================================

import os
from dotenv import load_dotenv

# Load values from the .env file into os.environ so they're accessible here.
# This must be called before any os.getenv() calls.
load_dotenv()


class BaseConfig:
    """
    BaseConfig: Shared settings across all environments.
    All environment-specific configs inherit from this class.
    """

    # -------------------------------------------------------------------------
    # Flask Core
    # -------------------------------------------------------------------------
    # SECRET_KEY is used by Flask to cryptographically sign session cookies,
    # CSRF tokens, and anything Flask-Login stores. It must be kept secret in
    # production and should be a long random string.
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-dev-secret-key")

    # -------------------------------------------------------------------------
    # Database (SQLAlchemy)
    # -------------------------------------------------------------------------
    # Build the MySQL connection URI from .env variables.
    # Format: mysql+pymysql://<user>:<password>@<host>/<dbname>
    # PyMySQL is a pure-Python MySQL driver — no native MySQL client needed.
    DB_USER     = os.getenv("DB_USER",     "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
    DB_HOST     = os.getenv("DB_HOST",     "localhost")
    DB_NAME     = os.getenv("DB_NAME",     "sahal_db")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    )

    # Disable modification tracking to reduce overhead; SQLAlchemy tracks
    # changes internally anyway.
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # -------------------------------------------------------------------------
    # Flask-Mail
    # -------------------------------------------------------------------------
    MAIL_SERVER   = os.getenv("MAIL_SERVER",   "smtp.example.com")
    MAIL_PORT     = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS  = os.getenv("MAIL_USE_TLS",  "True").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_USERNAME", "noreply@sahal.agency")

    # -------------------------------------------------------------------------
    # Flask-Login
    # -------------------------------------------------------------------------
    # The endpoint name (blueprint.view_function) that unauthenticated users
    # are redirected to. We'll define 'auth.login' in our auth blueprint.
    LOGIN_VIEW = "auth.login"


class DevelopmentConfig(BaseConfig):
    """
    DevelopmentConfig: Used during local development.
    DEBUG=True enables the Werkzeug debugger and auto-reloader.
    """
    DEBUG   = True
    TESTING = False


class TestingConfig(BaseConfig):
    """
    TestingConfig: Used during automated testing.
    Uses a separate in-memory SQLite DB so tests don't touch MySQL.
    """
    DEBUG   = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False  # Disable CSRF in tests for simplicity


class ProductionConfig(BaseConfig):
    """
    ProductionConfig: Used in the live environment.
    DEBUG and TESTING must always be False in production.
    """
    DEBUG   = False
    TESTING = False


# -------------------------------------------------------------------------
# Config selector
# -------------------------------------------------------------------------
# Map string names to config classes. create_app() uses this dict so callers
# can pass a string like "development" instead of importing the class directly.
config_by_name = {
    "development": DevelopmentConfig,
    "testing":     TestingConfig,
    "production":  ProductionConfig,
}
