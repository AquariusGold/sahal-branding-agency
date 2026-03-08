# =============================================================================
# app/admin/routes.py
# =============================================================================
# WHY THIS EXISTS:
#   This blueprint handles the administrative interface.
#   Phase 3A implements CRUD operations for Service Categories and Services.
#
# ROLE PROTECTION:
#   Every route here is wrapped in @login_required and @role_required("admin").
#   This ensures absolute segregation of privileges; clients cannot access these.
#
# SOFT DEACTIVATION vs DELETION:
#   You will notice there are no "delete" routes. Instead we have "toggle" routes
#   that flip `is_active` between True and False. This preserves the relational
#   integrity of the database (e.g., if a client ordered a service that we later 
#   stop offering, their receipt won't break because the service row still exists).
# =============================================================================

from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.admin import admin
from app.extensions import db
from app.admin.forms import CategoryForm, ServiceForm, OrderStatusForm, PortfolioItemForm
from app.models.service import ServiceCategory, Service
from app.models.order import Order, OrderStatus
from app.models.portfolio import PortfolioItem
from app.auth.decorators import role_required
from app.utils.device import is_mobile
from app.extensions import db


# -----------------------------------------------------------------------------
# Service Category Management
# -----------------------------------------------------------------------------

@admin.route("/categories", methods=["GET"])
@login_required
@role_required("admin")
def list_categories():
    """Lists all service categories."""
    categories = ServiceCategory.query.order_by(ServiceCategory.name).all()
    if is_mobile(request):
        return render_template("mobile/admin/categories.html", categories=categories)
    return render_template("desktop/admin/categories.html", categories=categories)


@admin.route("/categories/create", methods=["GET", "POST"])
@login_required
@role_required("admin")
def create_category():
    """Form to create a new category."""
    form = CategoryForm()
    if form.validate_on_submit():
        if ServiceCategory.query.filter_by(name=form.name.data).first():
            flash("Category name already exists.", "danger")
            return redirect(url_for("admin.create_category"))
            
        category = ServiceCategory(
            name=form.name.data,
            description=form.description.data,
            is_active=form.is_active.data
        )
        db.session.add(category)
        db.session.commit()
        flash("Category created successfully.", "success")
        return redirect(url_for("admin.list_categories"))

    if is_mobile(request):
        return render_template("mobile/admin/category_form.html", form=form, title="New Category")
    return render_template("desktop/admin/category_form.html", form=form, title="New Category")


@admin.route("/categories/edit/<int:id>", methods=["GET", "POST"])
@login_required
@role_required("admin")
def edit_category(id):
    """Form to edit an existing category."""
    category = ServiceCategory.query.get_or_404(id)
    form = CategoryForm(obj=category)
    
    if form.validate_on_submit():
        # Check if they are renaming it to a name that already exists for ANOTHER category
        existing = ServiceCategory.query.filter_by(name=form.name.data).first()
        if existing and existing.id != category.id:
            flash("Another category already uses that name.", "danger")
            return redirect(url_for("admin.edit_category", id=category.id))
            
        category.name = form.name.data
        category.description = form.description.data
        category.is_active = form.is_active.data
        db.session.commit()
        flash("Category updated successfully.", "success")
        return redirect(url_for("admin.list_categories"))

    if is_mobile(request):
        return render_template("mobile/admin/category_form.html", form=form, title="Edit Category")
    return render_template("desktop/admin/category_form.html", form=form, title="Edit Category")


@admin.route("/categories/toggle/<int:id>", methods=["POST"])
@login_required
@role_required("admin")
def toggle_category(id):
    """
    Soft-deactivates/activates a category.
    Prevents deactivation if the category has active services.
    """
    category = ServiceCategory.query.get_or_404(id)
    
    # Business logic check: Don't allow deactivating a category that has active services
    if category.is_active: 
        active_services = Service.query.filter_by(category_id=category.id, is_active=True).count()
        if active_services > 0:
            flash(f"Cannot deactivate '{category.name}' because it contains {active_services} active service(s). Deactivate them first.", "danger")
            return redirect(url_for("admin.list_categories"))
            
    category.is_active = not category.is_active
    db.session.commit()
    
    status = "activated" if category.is_active else "deactivated"
    flash(f"Category '{category.name}' {status}.", "success")
    return redirect(url_for("admin.list_categories"))


# -----------------------------------------------------------------------------
# Service Management
# -----------------------------------------------------------------------------

@admin.route("/services", methods=["GET"])
@login_required
@role_required("admin")
def list_services():
    """Lists all services, JOINing the category for display purposes."""
    # We join with category so we can display the category name easily in the template
    services = Service.query.join(Service.category).order_by(ServiceCategory.name, Service.name).all()
    if is_mobile(request):
        return render_template("mobile/admin/services.html", services=services)
    return render_template("desktop/admin/services.html", services=services)


@admin.route("/services/create", methods=["GET", "POST"])
@login_required
@role_required("admin")
def create_service():
    """Form to create a new service."""
    form = ServiceForm()
    
    if form.validate_on_submit():
        service = Service(
            category_id=form.category.data.id,
            name=form.name.data,
            description=form.description.data,
            base_price=form.base_price.data,
            pricing_type=form.pricing_type.data,
            is_active=form.is_active.data
        )
        db.session.add(service)
        db.session.commit()
        flash("Service created successfully.", "success")
        return redirect(url_for("admin.list_services"))

    if is_mobile(request):
        return render_template("mobile/admin/service_form.html", form=form, title="New Service")
    return render_template("desktop/admin/service_form.html", form=form, title="New Service")


@admin.route("/services/edit/<int:id>", methods=["GET", "POST"])
@login_required
@role_required("admin")
def edit_service(id):
    """Form to edit an existing service."""
    service = Service.query.get_or_404(id)
    form = ServiceForm(obj=service)
    
    if form.validate_on_submit():
        service.category_id = form.category.data.id
        service.name = form.name.data
        service.description = form.description.data
        service.base_price = form.base_price.data
        service.pricing_type = form.pricing_type.data
        service.is_active = form.is_active.data
        db.session.commit()
        flash("Service updated successfully.", "success")
        return redirect(url_for("admin.list_services"))

    if is_mobile(request):
        return render_template("mobile/admin/service_form.html", form=form, title="Edit Service")
    return render_template("desktop/admin/service_form.html", form=form, title="Edit Service")


@admin.route("/services/toggle/<int:id>", methods=["POST"])
@login_required
@role_required("admin")
def toggle_service(id):
    """Soft-deactivates/activates a service."""
    service = Service.query.get_or_404(id)
    
    # We can always deactivate a service.
    # But if we try to activate it, we should ensure the parent category is also active.
    if not service.is_active:
        if not service.category.is_active:
            flash(f"Cannot activate '{service.name}' because its category '{service.category.name}' is deactivated.", "danger")
            return redirect(url_for("admin.list_services"))
            
    service.is_active = not service.is_active
    db.session.commit()
    
    status = "activated" if service.is_active else "deactivated"
    flash(f"Service '{service.name}' {status}.", "success")
    return redirect(url_for("admin.list_services"))


@admin.route("/", methods=["GET"])
@login_required
@role_required("admin")
def dashboard():
    """Admin dashboard stub."""
    return redirect(url_for("dashboards.admin"))


@admin.route("/jobs", methods=["GET"])
@login_required
@role_required("admin")
def jobs():
    """Admin Job List stub."""
    if is_mobile(request):
        return render_template("mobile/admin/jobs.html", title="Job List")
    return render_template("desktop/admin/jobs.html", title="Job List")


@admin.route("/quotations", methods=["GET"])
@login_required
@role_required("admin")
def quotations():
    """Admin Quotations Management stub."""
    if is_mobile(request):
        return render_template("mobile/admin/quotations.html", title="Quotations")
    return render_template("desktop/admin/quotations.html", title="Quotations")


@admin.route("/invoices", methods=["GET"])
@login_required
@role_required("admin")
def invoices():
    """Admin Invoice Management stub."""
    if is_mobile(request):
        return render_template("mobile/admin/invoices.html", title="Invoices")
    return render_template("desktop/admin/invoices.html", title="Invoices")


@admin.route("/reports", methods=["GET"])
@login_required
@role_required("admin")
def reports():
    """Admin Reports & Analytics stub."""
    if is_mobile(request):
        return render_template("mobile/admin/reports.html", title="Reports & Analytics")
    return render_template("desktop/admin/reports.html", title="Reports & Analytics")


# =============================================================================
# PORTFOLIO MANAGEMENT ROUTES
# =============================================================================

@admin.route("/portfolio", methods=["GET"])
@login_required
@role_required("admin")
def list_portfolio():
    """Lists all portfolio items."""
    items = PortfolioItem.query.order_by(PortfolioItem.created_at.desc()).all()
    if is_mobile(request):
        return render_template("mobile/admin/portfolio.html", items=items, title="Manage Portfolio")
    return render_template("desktop/admin/portfolio.html", items=items, title="Manage Portfolio")

@admin.route("/portfolio/create", methods=["GET", "POST"])
@login_required
@role_required("admin")
def create_portfolio():
    """Form to create a new portfolio item."""
    form = PortfolioItemForm()
    if form.validate_on_submit():
        item = PortfolioItem(
            title=form.title.data,
            client_name=form.client_name.data,
            category=form.category.data,
            description=form.description.data,
            image_url=form.image_url.data,
            is_active=form.is_active.data
        )
        db.session.add(item)
        db.session.commit()
        flash("Portfolio item created successfully.", "success")
        return redirect(url_for("admin.list_portfolio"))

    if is_mobile(request):
        return render_template("mobile/admin/portfolio_form.html", form=form, title="New Portfolio Item")
    return render_template("desktop/admin/portfolio_form.html", form=form, title="New Portfolio Item")

@admin.route("/portfolio/edit/<int:id>", methods=["GET", "POST"])
@login_required
@role_required("admin")
def edit_portfolio(id):
    """Form to edit an existing portfolio item."""
    item = PortfolioItem.query.get_or_404(id)
    form = PortfolioItemForm(obj=item)
    
    if form.validate_on_submit():
        item.title = form.title.data
        item.client_name = form.client_name.data
        item.category = form.category.data
        item.description = form.description.data
        item.image_url = form.image_url.data
        item.is_active = form.is_active.data
        db.session.commit()
        flash("Portfolio item updated successfully.", "success")
        return redirect(url_for("admin.list_portfolio"))

    if is_mobile(request):
        return render_template("mobile/admin/portfolio_form.html", form=form, title="Edit Portfolio Item")
    return render_template("desktop/admin/portfolio_form.html", form=form, title="Edit Portfolio Item")

@admin.route("/portfolio/toggle/<int:id>", methods=["POST"])
@login_required
@role_required("admin")
def toggle_portfolio(id):
    """Soft-deactivates/activates a portfolio item."""
    item = PortfolioItem.query.get_or_404(id)
    item.is_active = not item.is_active
    db.session.commit()
    
    status = "activated" if item.is_active else "deactivated"
    flash(f"Portfolio item '{item.title}' {status}.", "success")
    return redirect(url_for("admin.list_portfolio"))

# =============================================================================
# ORDER MANAGEMENT ROUTES
# =============================================================================

@admin.route("/orders", methods=["GET"])
@login_required
@role_required("admin")
def list_orders():
    """Lists all orders in the system."""
    orders = Order.query.order_by(Order.created_at.desc()).all()
    
    if is_mobile(request):
        return render_template("mobile/admin/orders.html", orders=orders, title="Manage Orders")
    return render_template("desktop/admin/orders.html", orders=orders, title="Manage Orders")


@admin.route("/orders/<int:id>", methods=["GET"])
@login_required
@role_required("admin")
def order_detail(id):
    """View details of a specific order."""
    order = Order.query.get_or_404(id)
    form = OrderStatusForm(status=order.status.name)
    
    if is_mobile(request):
        return render_template("mobile/admin/order_detail.html", order=order, form=form, title=f"Order #{order.id}")
    return render_template("desktop/admin/order_detail.html", order=order, form=form, title=f"Order #{order.id}")


@admin.route("/orders/<int:id>/update-status", methods=["POST"])
@login_required
@role_required("admin")
def update_order_status(id):
    """Updates the status of an order."""
    order = Order.query.get_or_404(id)
    form = OrderStatusForm()
    
    if form.validate_on_submit():
        new_status = form.status.data
        
        # In a real system, we might validate state transitions here
        # E.g., preventing going from 'completed' back to 'pending'.
        
        # update Status enum
        order.status = OrderStatus[new_status]
        db.session.commit()
        
        flash(f"Order #{order.id} status updated to {new_status.replace('_', ' ').title()}.", "success")
    else:
        flash("Invalid status selected.", "danger")
        
    return redirect(url_for("admin.order_detail", id=order.id))
