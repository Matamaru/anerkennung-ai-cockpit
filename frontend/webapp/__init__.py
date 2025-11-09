#****************************************************************************
#    Application:   Anerkennung AI Cockpit
#    Module:        frontend.webapp.__init__
#    Author:        Heiko Matamaru, IGS
#    Version:       0.0.1
#****************************************************************************

from flask import Flask, render_template
from backend.config import StrictConfig as Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # === Security headers
    @app.after_request
    def add_security_header(resp):
        resp.headers['X-Content-Type-Options'] = 'nosniff'
        resp.headers['X-Frame-Options'] = 'DENY'
        resp.headers['X-XSS-Protection'] = '1; mode=block'
        return resp

    # === Blueprints
    from frontend.webapp.main.routes import main_bp
    from frontend.webapp.auth.routes import auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    return app
