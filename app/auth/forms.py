# =============================================================================
# app/auth/forms.py
# =============================================================================
# WHY THIS EXISTS:
#   WTForms + Flask-WTF provide server-side form validation and CSRF protection.
#   Defining form classes separately from routes keeps validation logic clean
#   and reusable across different routes/views.
#
# The forms here are stubs ready to be activated in Phase 2.
# =============================================================================

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, ValidationError


class LoginForm(FlaskForm):
    """Form for existing users to authenticate."""
    email    = StringField("Email",    validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit   = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    """Form for new users to create an account."""
    account_type    = RadioField(
        "Account Type",
        choices=[("personal", "Personal Account"), ("business", "Business Account")],
        default="personal",
        validators=[DataRequired()]
    )
    full_name       = StringField("Full Name",       validators=[DataRequired(), Length(2, 120)])
    email           = StringField("Email",           validators=[DataRequired(), Email()])
    
    # Optional fields based on account type
    phone_number    = StringField("Phone Number",    validators=[Optional(), Length(max=20)])
    
    # Business-specific fields
    company_name    = StringField("Company Name",    validators=[Optional(), Length(max=120)])
    company_website = StringField("Company Website", validators=[Optional(), Length(max=255)])
    industry        = StringField("Industry",        validators=[Optional(), Length(max=120)])

    password        = PasswordField("Password",      validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")]
    )
    submit          = SubmitField("Create Account")

    def validate(self, extra_validators=None):
        """
        Custom form-level validation.
        We cannot use validate_company_name because the Optional() validator stops
        the validation chain if the field is empty.
        """
        # First let the default WTForms validation run (DataRequired, Length, etc.)
        initial_validation = super(RegistrationForm, self).validate(extra_validators)
        
        # Now check our custom account_type cross-field logic
        if self.account_type.data == "business" and not self.company_name.data:
            self.company_name.errors.append("Company name is required for Business accounts.")
            return False
            
        return initial_validation


class PasswordResetRequestForm(FlaskForm):
    """Form to request a password-reset email."""
    email  = StringField("Email",  validators=[DataRequired(), Email()])
    submit = SubmitField("Reset Password")


class PasswordResetForm(FlaskForm):
    """Form to set a new password after receiving a reset token."""
    password        = PasswordField("New Password",     validators=[DataRequired(), Length(8)])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password")]
    )
    submit          = SubmitField("Save New Password")
