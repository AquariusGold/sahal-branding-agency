# =============================================================================
# app/__init__.py  —  Application Factory
# =============================================================================
# WHY THE APPLICATION FACTORY PATTERN?
#   A factory function (create_app) creates the Flask app instance on demand.
#   Benefits:
#     1. Multiple app instances can coexist (e.g. one for tests, one for prod).
#     2. Extensions are bound to an app instance, not imported globally, which
#        prevents circular imports.
#     3. Config can be swapped at call time: create_app("testing") vs
#        create_app("production").
#
# CALL ORDER (critical — changing this order introduces subtle bugs):
#   1. Create Flask instance
#   2. Load config
#   3. Initialize extensions (db, migrate, login_manager, mail)
#   4. Register blueprints
#   5. Register context processors (device detection for templates)
#   6. Seed database (insert dummy row on first boot)
# =============================================================================

import os
from flask import Flask, request as flask_request
from app.config import config_by_name
from app.extensions import db, migrate, login_manager, mail
from app.utils.device import is_mobile


def create_app(config_name: str = None) -> Flask:
    """
    Application factory.

    Args:
        config_name: One of "development", "testing", "production".
                     Defaults to the FLASK_ENV environment variable, or
                     "development" if that is also unset.

    Returns:
        A fully configured Flask application instance.
    """

    # -------------------------------------------------------------------------
    # 1. Resolve configuration name
    # -------------------------------------------------------------------------
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    # -------------------------------------------------------------------------
    # 2. Create the Flask app
    # -------------------------------------------------------------------------
    # template_folder is set to "templates" inside the app package so Jinja2
    # can find both app/templates/desktop/ and app/templates/mobile/.
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # -------------------------------------------------------------------------
    # 3. Load configuration
    # -------------------------------------------------------------------------
    # config_by_name maps config_name strings to BaseConfig subclasses.
    app.config.from_object(config_by_name[config_name])

    # -------------------------------------------------------------------------
    # 4. Initialize Flask extensions
    # -------------------------------------------------------------------------
    # Each extension's init_app() binds it to this specific app instance.
    # This is the deferred initialization pattern — extensions are created in
    # extensions.py without an app; they receive the app only here.
    db.init_app(app)
    migrate.init_app(app, db)          # Migrate needs both app AND db.

    login_manager.init_app(app)
    login_manager.login_view = app.config.get("LOGIN_VIEW", "auth.login")
    # Message shown to users who hit a @login_required route unauthenticated:
    login_manager.login_message      = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    # -------------------------------------------------------------------------
    # user_loader callback — REQUIRED by Flask-Login on every request.
    # Flask-Login calls this with a user_id (from the session cookie) to
    # reload the user object. Without this callback registered, Flask-Login
    # raises "Missing user_loader" on every request.
    #
    # Phase 1 stub: returns None (no User model yet).
    # Phase 2: replace `return None` with `return User.query.get(int(user_id))`
    # -------------------------------------------------------------------------
    # Phase 2: Real user loader
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    mail.init_app(app)

    # -------------------------------------------------------------------------
    # 5. Register blueprints
    # -------------------------------------------------------------------------
    # Import here (not at module top) to avoid circular imports — blueprints
    # import from extensions, which must already be initialized.
    from app.main       import main       as main_blueprint
    from app.auth       import auth       as auth_blueprint
    from app.services   import services   as services_blueprint
    from app.admin      import admin      as admin_blueprint
    from app.dashboards import dashboards as dashboards_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(services_blueprint)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(dashboards_blueprint)

    # -------------------------------------------------------------------------
    # 6. Context processor — inject device detection into ALL templates
    # -------------------------------------------------------------------------
    # A context processor returns a dict that is merged into the template
    # context for every render_template() call in the app.  By injecting
    # `is_mobile` (the result, not the function) here, any Jinja2 template
    # can branch on {% if is_mobile %} without the route needing to pass it.
    @app.context_processor
    def inject_device_context():
        """Make device detection result available in every template."""
        return {
            "is_mobile": is_mobile(flask_request),
            "device_type": "Mobile" if is_mobile(flask_request) else "Desktop",
        }

    # -------------------------------------------------------------------------
    # 7. Seed database with dummy row on first boot
    # -------------------------------------------------------------------------
    # We use app.app_context() so SQLAlchemy can resolve the database URI.
    # This block runs once every time the app starts; the INSERT is guarded
    # by a .first() check so it's idempotent (safe to call multiple times).
    with app.app_context():
        # Import all models here so Flask-Migrate finds them via MetaData.
        from app.models import TestConnection  # noqa: F401
        from app.models.user import User, UserRole  # noqa: F401

        try:
            # Create tables that don't exist yet.
            # In production, Flask-Migrate handles schema changes; this is a
            # safety net for the very first run before migrations are applied.
            db.create_all()

            # Seed: insert one row only if the table is empty.
            if TestConnection.query.count() == 0:
                seed_row = TestConnection(
                    message="✅ Database Connected Successfully — SAHAL Stack is Running!"
                )
                db.session.add(seed_row)
                db.session.commit()
                app.logger.info("Seeded TestConnection table with initial row.")

            # Phase 2: Admin Bootstrap
            if User.query.filter_by(email="admin@sahal.com").first() is None:
                admin_user = User(
                    full_name="System Administrator",
                    email="admin@sahal.com",
                    role=UserRole.admin
                )
                admin_user.set_password("Admin123!")
                db.session.add(admin_user)
                db.session.commit()
                app.logger.info("Default admin user created: admin@sahal.com")
                
        except Exception as exc:
            # Log but don't crash — the app can still start even if DB is
            # temporarily unreachable; the route will show the error message.
            app.logger.warning(f"DB seed skipped: {exc}")

    return app
