# =============================================================================
# app/models/portfolio.py
# =============================================================================
# WHY THIS EXISTS:
#   Defines the model for portfolio items displayed on the public website.
#   Allows administrators to dynamically add, edit, or hide past projects.
# =============================================================================

from datetime import datetime, timezone
from app.extensions import db

class PortfolioItem(db.Model):
    """
    Represents a past project or portfolio piece to showcase to clients.
    """
    __tablename__ = "sahal_portfolio_items"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    client_name = db.Column(db.String(150), nullable=True)
    category = db.Column(db.String(100), nullable=False) # e.g., 'Branding', 'Web Design'
    image_url = db.Column(db.String(500), nullable=False)
    
    # Soft deactivate support so we don't have to permanently delete items
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<PortfolioItem {self.title}>"
