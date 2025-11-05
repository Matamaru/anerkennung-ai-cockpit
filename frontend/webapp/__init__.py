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

    # === Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', code=404, message='Page not found'), 404

    @app.errorhandler(413)
    def too_large(e):
        return render_template('error.html', code=413, message='Upload too large. Reduce file size or count.'), 413
 
    @app.errorhandler(500)
    def server_error(e):
        return render_template('error.html', code=500, message='Unexpected server error.'), 500

    # === Blueprints
    from frontend.webapp.main.routes import main_bp
    from frontend.webapp.auth.routes import auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    return app
