#****************************************************************************
#    Application:   Anerkennung AI Cockpit
#    Module:        frontend.webapp.__init__
#    Author:        Heiko Matamaru, IGS
#    Version:       0.0.1
#****************************************************************************

from flask import Flask, render_template
from flask_login import LoginManager
from backend.config import HerokuConfig as Config

# create the LoginManager once, at module level
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
#    print("SECRET_KEY present?", 'SECRET_KEY' in app.config, "| Value:", app.config.get('SECRET_KEY'))


    # === Security headers
    @app.after_request
    def add_security_header(resp):
        resp.headers['X-Content-Type-Options'] = 'nosniff'
        resp.headers['X-Frame-Options'] = 'DENY'
        resp.headers['X-XSS-Protection'] = '1; mode=block'
        return resp

    # === Login Manager setup ===
    login_manager.init_app(app)
    # endpoint name of your login page (GET route)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.session_protection = "basic"

    # === Blueprints
    from frontend.webapp.main.routes import main_bp
    from frontend.webapp.auth.routes import auth_bp
    from frontend.webapp.recruiter.routes import recruiter_bp
    from frontend.webapp.admin.routes import admin_bp
    from frontend.webapp.candidate.routes import candidate_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(recruiter_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(candidate_bp)

    return app


# === User loader for Flask-Login ===
from backend.datamodule.models.user import User  # adjust path to your User model


@login_manager.user_loader
def load_user(user_id: str):
    """
    Given a user_id (stored in the session), return a User object
    or None if not found.
    Flask-Login calls this automatically.
    """
    try:
        # if your primary key is int, cast here
        user_tuple = User.get_by_id(user_id)
    except (ValueError, TypeError):
        return None

    if user_tuple is None:
        return None

    return User.from_tuple(user_tuple)
