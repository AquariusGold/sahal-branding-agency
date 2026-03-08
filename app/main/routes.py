# =============================================================================
# app/main/routes.py
# =============================================================================
# WHY THIS FILE EXISTS:
#   Route handlers for the "main" blueprint.  By keeping route logic here
#   (not in __init__.py) we maintain clean package structure and prevent
#   circular import issues.
#
# THE ROOT ROUTE — GET /
#   This is the single most important verification route for Phase 1.
#   It:
#     1. Detects the visitor's device type (mobile vs desktop).
#     2. Queries the TestConnection table to confirm MySQL is reachable.
#     3. Renders the correct template (mobile/home.html or desktop/home.html).
# =============================================================================

from flask import render_template, request, flash
from app.main import main
from app.models import TestConnection
from app.utils.device import is_mobile


@main.route("/", methods=["GET"])
def index():
    """
    Root route — entry point for all visitors.

    Device detection selects the template directory.
    The TestConnection record is passed to the template to prove DB connectivity.
    """

    # ------------------------------------------------------------------
    # 1. Device Detection
    # ------------------------------------------------------------------
    # is_mobile() inspects the User-Agent header.  The return value drives
    # which template subtree is used — no duplication of business logic.
    mobile = is_mobile(request)
    template_prefix = "mobile" if mobile else "desktop"

    # ------------------------------------------------------------------
    # 2. Database Health Check
    # ------------------------------------------------------------------
    # We query the first row of TestConnection.  If the DB is unreachable,
    # SQLAlchemy will raise an OperationalError; we catch it gracefully.
    db_record = None
    db_error  = None

    try:
        db_record = TestConnection.query.first()
    except Exception as exc:
        # Surface the error in the template rather than crashing with 500.
        db_error = str(exc)

    # ------------------------------------------------------------------
    # 3. Render the device-appropriate template
    # ------------------------------------------------------------------
    return render_template(
        f"{template_prefix}/public/home.html",
        db_record=db_record,
        db_error=db_error,
        device_type="Mobile" if mobile else "Desktop",
    )


@main.route("/about", methods=["GET"])
def about():
    """About us page"""
    if is_mobile(request):
        return render_template("mobile/public/about.html", title="About Us")
    return render_template("desktop/public/about.html", title="About Us")


from app.models.portfolio import PortfolioItem

@main.route("/portfolio", methods=["GET"])
def portfolio():
    """Portfolio grid page"""
    items = PortfolioItem.query.filter_by(is_active=True).order_by(PortfolioItem.created_at.desc()).all()
    if is_mobile(request):
        return render_template("mobile/public/portfolio.html", items=items, title="Our Work")
    return render_template("desktop/public/portfolio.html", items=items, title="Our Work")


@main.route("/contact", methods=["GET"])
def contact():
    """Contact form page"""
    if is_mobile(request):
        return render_template("mobile/public/contact.html", title="Contact Us")
    return render_template("desktop/public/contact.html", title="Contact Us")
