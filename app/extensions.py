# =============================================================================
# app/extensions.py
# =============================================================================
# WHY THIS FILE EXISTS:
#   Flask extensions (SQLAlchemy, Migrate, LoginManager, Mail) must be
#   instantiated ONCE as module-level singletons. They are created here WITHOUT
#   being bound to any Flask app instance — that binding happens later inside
#   create_app() via extension.init_app(app).
#
# WHY NOT IN app/__init__.py?
#   Defining extensions in __init__.py causes circular imports: your models
#   need `db`, your app factory imports models, models import from __init__,
#   creating a loop. Placing extensions in a dedicated file breaks the cycle.
#
# HOW IT WORKS:
#   1. Instantiate extension objects here (no app context yet).
#   2. In create_app(), call db.init_app(app), migrate.init_app(app, db), etc.
#   3. Any other module that needs `db` simply imports it from here:
#        from app.extensions import db
# =============================================================================

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail

# SQLAlchemy ORM — provides db.Model, db.session, db.Column, etc.
db = SQLAlchemy()

# Alembic-based database migration manager — tracks schema changes over time.
migrate = Migrate()

# Flask-Login manager — handles user session tracking and @login_required guard.
login_manager = LoginManager()

# Flask-Mail — sends transactional emails (welcome, password reset, etc.).
mail = Mail()
