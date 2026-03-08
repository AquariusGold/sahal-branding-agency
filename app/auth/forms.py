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
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
    """Form for existing users to authenticate."""
    email    = StringField("Email",    validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit   = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    """Form for new users to create an account."""
    full_name       = StringField("Full Name",       validators=[DataRequired(), Length(2, 120)])
    email           = StringField("Email",           validators=[DataRequired(), Email()])
    password        = PasswordField("Password",      validators=[DataRequired(), Length(8)])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")]
    )
    submit          = SubmitField("Create Account")


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
