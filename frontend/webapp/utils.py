

from functools import wraps
from flask import redirect, url_for
from flask_login import current_user

def admin_required(f):
    """
    Decorator to restrict access to admin users.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the current user is an admin
        if not current_user.is_authenticated or not current_user.is_admin():
            # Redirect to the login page or a forbidden page
            return redirect(url_for('auth.login'))  # Or 'auth.forbidden' if you want to show a 403 page
        return f(*args, **kwargs)

    return decorated_function

def recruiter_required(f):
    """
    Decorator to restrict access to recruiter users.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the current user is a recruiter
        if not current_user.is_authenticated or not current_user.is_recruiter():
            # Redirect to the login page or a forbidden page
            return redirect(url_for('auth.login'))  # Or 'auth.forbidden' if you want to show a 403 page
        return f(*args, **kwargs)

    return decorated_function

def candidate_required(f):
    """
    Decorator to restrict access to candidate users.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the current user is a candidate
        if not current_user.is_authenticated or not current_user.is_candidate():
            # Redirect to the login page or a forbidden page
            return redirect(url_for('auth.login'))  # Or 'auth.forbidden' if you want to show a 403 page
        return f(*args, **kwargs)

    return decorated_function