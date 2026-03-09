# =============================================================================
# app/auth/routes.py
# =============================================================================
# WHY THIS EXISTS:
#   Stub routes for the authentication blueprint.
#   Full implementation (login, register, logout, password reset) will be
#   added in Phase 2.  Having these stubs now means url_for("auth.login")
#   already resolves and Flask-Login can redirect to it correctly.
# =============================================================================

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import auth
from app.auth.forms import LoginForm, RegistrationForm
from app.models.user import User, UserRole, AccountType
from app.extensions import db
from app.utils.device import is_mobile


@auth.route("/login", methods=["GET", "POST"])
def login():
    # If already logged in, send them to their dashboard
    if current_user.is_authenticated:
        if current_user.role == UserRole.admin:
            return redirect(url_for("dashboards.admin"))
        elif current_user.role == UserRole.client:
            return redirect(url_for("dashboards.client"))
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth.login"))
            
        if not user.is_active:
            flash("This account has been deactivated.", "danger")
            return redirect(url_for("auth.login"))

        login_user(user, remember=form.remember.data)
        
        # After login, redirect to next page or their dashboard
        next_page = request.args.get("next")
        if not next_page or not next_page.startswith("/"):
            if user.role == UserRole.admin:
                next_page = url_for("dashboards.admin")
            elif user.role == UserRole.client:
                next_page = url_for("dashboards.client")
            else:
                next_page = url_for("main.index")
                
        return redirect(next_page)

    if is_mobile(request):
        return render_template("mobile/auth/login.html", form=form)
    return render_template("desktop/auth/login.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("main.index"))


@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if email already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Email already registered. Please log in.", "warning")
            return redirect(url_for("auth.register"))

        # Determine AccountType enum from form data
        acc_type = AccountType.business if form.account_type.data == "business" else AccountType.personal

        user = User(
            full_name=form.full_name.data,
            email=form.email.data,
            role=UserRole.client, # By default, new registrations are clients
            account_type=acc_type,
            phone_number=form.phone_number.data if form.phone_number.data else None
        )
        
        # Add business specific fields if it's a business account
        if acc_type == AccountType.business:
            user.company_name = form.company_name.data
            user.company_website = form.company_website.data if form.company_website.data else None
            user.industry = form.industry.data if form.industry.data else None

        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash("Registration successful! Welcome to SAHAL.", "success")
        
        # Automatically log them in
        login_user(user)
        return redirect(url_for("dashboards.client"))

    if is_mobile(request):
        return render_template("mobile/auth/register.html", form=form)
    return render_template("desktop/auth/register.html", form=form)
