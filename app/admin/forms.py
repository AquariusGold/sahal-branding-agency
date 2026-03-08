# =============================================================================
# app/admin/forms.py
# =============================================================================
# WHY THIS EXISTS:
#   Validates incoming POST data when creating or editing categories and services.
#
# DYNAMIC QUERY SELECT FIELD:
#   WTForms' QuerySelectField is used to dynamically populate the HTML <select> 
#   drop-down with `ServiceCategory` objects directly from the database. It asks:
#   "What categories exist right now?" instead of hardcoding choices.
# =============================================================================

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, DecimalField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange
# QuerySelectField is an extension of WTForms specifically for SQLAlchemy
from wtforms_sqlalchemy.fields import QuerySelectField

from app.models.service import ServiceCategory, PricingType

def active_categories_query():
    """
    Returns a SQLAlchemy query object used by QuerySelectField.
    We only want admins to attach new services to ACTIVE categories.
    """
    return ServiceCategory.query.filter_by(is_active=True).order_by(ServiceCategory.name)

class CategoryForm(FlaskForm):
    """Validates creation/editing of a ServiceCategory."""
    name = StringField("Category Name", validators=[DataRequired(), Length(max=120)])
    description = TextAreaField("Description", validators=[Length(max=500)])
    is_active = BooleanField("Active Status", default=True)
    submit = SubmitField("Save Category")


class ServiceForm(FlaskForm):
    """Validates creation/editing of a Service."""
    
    # Dynamically loads categories. get_label dictates what text shows in the drop-down.
    category = QuerySelectField(
        "Parent Category", 
        query_factory=active_categories_query, 
        get_label="name", 
        allow_blank=False,
        validators=[DataRequired(message="You must select a valid active category.")]
    )
    
    name = StringField("Service Name", validators=[DataRequired(), Length(max=150)])
    description = TextAreaField("Description", validators=[DataRequired()])
    
    # DecimalField ensures the input is parsed as a Decimal, preventing float errors.
    base_price = DecimalField("Base Price (USD)", places=2, validators=[DataRequired(), NumberRange(min=0)])
    
    # Choices map to the PricingType enum created in models/service.py
    pricing_type = SelectField(
        "Pricing Type",
        choices=[("fixed", "Fixed Price"), ("per_unit", "Per Unit / Hourly"), ("custom", "Custom Quote")],
        validators=[DataRequired()]
    )
    
    is_active = BooleanField("Active Status", default=True)
    submit = SubmitField("Save Service")


class OrderStatusForm(FlaskForm):
    """Form to allow Admins to update an Order's status."""
    status = SelectField(
        "Order Status",
        choices=[
            ("pending", "Pending"), 
            ("confirmed", "Confirmed"), 
            ("in_progress", "In Progress"), 
            ("quality_check", "Quality Check"), 
            ("completed", "Completed"), 
            ("cancelled", "Cancelled")
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField("Update Status")

class PortfolioItemForm(FlaskForm):
    """Validates creation/editing of a PortfolioItem."""
    title = StringField("Project Title", validators=[DataRequired(), Length(max=150)])
    client_name = StringField("Client Name", validators=[Length(max=150)])
    category = StringField("Category (e.g., Branding, Web Design)", validators=[DataRequired(), Length(max=100)])
    description = TextAreaField("Description", validators=[DataRequired()])
    image_url = StringField("Image URL", validators=[DataRequired(), Length(max=500)])
    is_active = BooleanField("Visible on Public Portfolio?", default=True)
    submit = SubmitField("Save Portfolio Item")
