# =============================================================================
# app/models/service.py
# =============================================================================
# WHY THIS EXISTS:
#   This file defines the core data structures for SAHAL's service catalog.
#   It establishes exactly what a "Service" is (e.g., "Full Brand Identity") 
#   and how it relates to a "Category" (e.g., "Design Services").
#
# DECIMAL FIELDS:
#   base_price uses `db.Numeric(10, 2)` (a Decimal type under the hood).
#   We NEVER use standard floats for money because 0.1 + 0.2 in floating point
#   is 0.30000000000000004. Decimals ensure exact precision required for billing.
#
# SOFT DEACTIVATION:
#   is_active is used instead of deleting rows. If a client book a service,
#   and we later delete that service row, the client's past order breaks. By 
#   toggling is_active=False instead, we preserve historical relational integrity.
# =============================================================================

import enum
from datetime import datetime, timezone
from app.extensions import db


class PricingType(enum.Enum):
    """
    Enum defining how a service is billed. Limits the column to known strings.
    - fixed    : A set price (e.g., $1000 for a logo).
    - per_unit : Hourly rate or per-item rate (e.g., $150/hour consulting).
    - custom   : Price is determined after consultation (base_price might be 0).
    """
    fixed = "fixed"
    per_unit = "per_unit"
    custom = "custom"


class ServiceCategory(db.Model):
    """
    Groups related services together.
    Relationships:
      - Has many Services (One-to-Many).
    """
    __tablename__ = "sahal_service_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship to Service
    # back_populates ensures that modifying categorized.services updates service.category implicitly
    # cascade="all, delete-orphan" means if a category is forcefully deleted, its services go with it 
    # (though our app logic will try to prevent this via soft deactivate).
    services = db.relationship("Service", back_populates="category", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ServiceCategory {self.name}>"


class Service(db.Model):
    """
    An individual bookable offering.
    Relationships:
      - Belongs to one ServiceCategory (Many-to-One).
    """
    __tablename__ = "sahal_services"

    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Key linking this service to its parent category
    category_id = db.Column(db.Integer, db.ForeignKey("sahal_service_categories.id"), nullable=False)
    
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Numeric(10, 2) means up to 10 digits total, 2 of which are after the decimal (e.g., 99999999.99)
    base_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    pricing_type = db.Column(db.Enum(PricingType), default=PricingType.fixed, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship back to ServiceCategory
    category = db.relationship("ServiceCategory", back_populates="services")

    def __repr__(self):
        return f"<Service {self.name} (${self.base_price})>"
