# =============================================================================
# app/services/routes.py
# =============================================================================
# WHY THIS EXISTS:
#   Service-listing routes.  Currently stubs; will be expanded in Phase 3
#   to show branding packages, accept booking forms, and trigger email
#   confirmation via Flask-Mail.
# =============================================================================

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.services import services
from app.extensions import db
from app.models.service import ServiceCategory, Service
from app.models.order import Order, OrderItem
from app.utils.device import is_mobile


@services.route("/", methods=["GET"])
def index():
    """
    Services landing page.
    Lists all available branding packages and design services.
    """
    categories = ServiceCategory.query.filter_by(is_active=True).all()
    
    if is_mobile(request):
        return render_template("mobile/services/index.html", categories=categories, title="Our Services")
    return render_template("desktop/services/index.html", categories=categories, title="Our Services")


@services.route("/category/<slug>", methods=["GET"])
def category_detail(slug):
    """
    Shows services under a specific category.
    """
    # Using 'id' for now until actual slug field exists
    category = ServiceCategory.query.filter_by(id=slug, is_active=True).first_or_404()
    
    if is_mobile(request):
        return render_template("mobile/services/category_detail.html", category=category, title=category.name)
    return render_template("desktop/services/category_detail.html", category=category, title=category.name)


@services.route("/booking", methods=["GET"])
def booking_wizard():
    """4-step booking wizard."""
    categories = ServiceCategory.query.filter_by(is_active=True).all()
    if is_mobile(request):
        return render_template("mobile/booking/wizard.html", categories=categories, title="Start a Project")
    return render_template("desktop/booking/wizard.html", categories=categories, title="Start a Project")


# =============================================================================
# CLIENT ORDER ROUTES
# =============================================================================

@services.route("/orders", methods=["GET"])
@login_required
def list_orders():
    """Lists all orders belonging to the currently logged in client."""
    # We enforce that clients only see their own orders.
    # Note: Admins manage all orders in the admin blueprint.
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    
    if is_mobile(request):
        return render_template("mobile/client/orders.html", orders=orders, title="My Orders")
    return render_template("desktop/client/orders.html", orders=orders, title="My Orders")


@services.route("/quotations/<int:id>", methods=["GET"])
@login_required
def view_quotation(id):
    """View details of a specific quotation."""
    order = Order.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    if is_mobile(request):
        return render_template("mobile/client/quotation.html", order=order, title=f"Quotation #{order.id}")
    return render_template("desktop/client/quotation.html", order=order, title=f"Quotation #{order.id}")


@services.route("/invoices/<int:id>", methods=["GET"])
@login_required
def view_invoice(id):
    """View details of a specific invoice."""
    order = Order.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    if is_mobile(request):
        return render_template("mobile/client/invoice.html", order=order, title=f"Invoice #{order.id}")
    return render_template("desktop/client/invoice.html", order=order, title=f"Invoice #{order.id}")


@services.route("/orders/<int:id>", methods=["GET"])
@login_required
def order_detail(id):
    """View details of a specific client order."""
    order = Order.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    if is_mobile(request):
        return render_template("mobile/client/order_detail.html", order=order, title=f"Order #{order.id}")
    return render_template("desktop/client/order_detail.html", order=order, title=f"Order #{order.id}")


@services.route("/orders/create", methods=["POST"])
@login_required
def create_order():
    """
    Handles the creation of a new order from a submitted service booking form.
    Snapshots the base_price into unit_price for historical integrity.
    """
    # Exposing the raw form processing logic. Let's assume the form submits a 'service_id' and 'quantity'
    service_id = request.form.get("service_id", type=int)
    quantity = request.form.get("quantity", type=int, default=1)
    
    if not service_id:
        flash("Invalid service selected.", "danger")
        return redirect(url_for("services.index"))
        
    service = Service.query.filter_by(id=service_id, is_active=True).first()
    if not service:
        flash("This service is currently unavailable.", "danger")
        return redirect(url_for("services.index"))
        
    if quantity < 1:
        flash("Quantity must be at least 1.", "danger")
        return redirect(url_for("services.index"))

    # Instantiate Order
    new_order = Order(user_id=current_user.id)
    
    # Instantiate OrderItem using snapshot base_price
    item = OrderItem(
        order=new_order,
        service_id=service.id,
        quantity=quantity,
        unit_price=service.base_price
    )
    
    # Calculate Line Totals before saving
    item.calculate_subtotal()
    
    # The new_order doesn't have an ID yet, but SQLAlchemy maps the relationship. 
    # Since item is appended automatically by the keyword arg `order=new_order`, 
    # calculate_total can iterate over self.items natively.
    new_order.calculate_total()
    
    # Save Transaction
    db.session.add(new_order)
    db.session.commit()
    
    flash("Your order has been placed successfully. A dedicated project manager will review it shortly.", "success")
    return redirect(url_for("services.order_detail", id=new_order.id))
