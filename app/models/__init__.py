# =============================================================================
# app/models/__init__.py
# =============================================================================
# WHY THIS FILE EXISTS:
#   All database models (ORM table definitions) live in the models package.
#   Keeping them here — separate from routes and views — enforces the
#   Single Responsibility Principle and makes migrations predictable.
#
# HOW DB INITIALIZATION WORKS:
#   Flask-Migrate tracks every change to these model classes and generates
#   SQL migration scripts automatically via `flask db migrate` + `flask db upgrade`.
#   On the very first run we also insert a dummy row so the homepage can
#   confirm the DB connection is live.
# =============================================================================

from app.extensions import db


class TestConnection(db.Model):
    """
    TestConnection — a lightweight smoke-test model.

    Purpose  : Verify that the ORM can communicate with MySQL.
    Lifecycle : Created once during `flask db upgrade`, seeded once on first
                app startup (see create_app in app/__init__.py), then queried
                by the root route (GET /) to confirm connectivity.

    In production this model stays in the DB and serves as a baseline health
    reference. Future modules (Portfolio, Services, Admin) will add their own
    models in separate files inside this package.
    """

    __tablename__ = "test_connection"

    # Primary key — auto-incremented by MySQL.
    id = db.Column(db.Integer, primary_key=True)

    # Arbitrary status message inserted on first boot.
    message = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<TestConnection id={self.id} message='{self.message}'>"


# =============================================================================
# Future models — import them here once created so Flask-Migrate picks them up:
#
from .user import User, UserRole
from .service import ServiceCategory, Service, PricingType
from .order import Order, OrderItem
from .portfolio import PortfolioItem
#   from app.models.admin_log   import AdminLog
# =============================================================================
