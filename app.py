"""
Smart Food Court Management System
Flask + MySQL Backend
Run:  python app.py
Open: http://localhost:5000
"""

from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config
from extensions import db, jwt, bcrypt
from api.auth   import auth_bp
from api.menu   import menu_bp
from api.orders import orders_bp
from api.vendor import vendor_bp
from api.admin  import admin_bp
import os

# Absolute path to the folder where app.py lives
# This works no matter where you run `python app.py` from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def create_app():
    app = Flask(
        __name__,
        static_folder=os.path.join(BASE_DIR, 'static'),
        static_url_path='/static'
    )
    app.config.from_object(Config)

    # Extensions
    CORS(app, supports_credentials=True)
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)

    # ── API Blueprints ─────────────────────────────────────
    app.register_blueprint(auth_bp,   url_prefix='/api/auth')
    app.register_blueprint(menu_bp,   url_prefix='/api/menu')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(vendor_bp, url_prefix='/api/vendor')
    app.register_blueprint(admin_bp,  url_prefix='/api/admin')

    # ── Serve HTML Pages (always from BASE_DIR) ────────────
    @app.route('/')
    def index():
        return send_from_directory(BASE_DIR, 'login.html')

    @app.route('/login')
    def login_page():
        return send_from_directory(BASE_DIR, 'login.html')

    @app.route('/customer')
    def customer_page():
        return send_from_directory(BASE_DIR, 'customer.html')

    @app.route('/vendor')
    def vendor_page():
        return send_from_directory(BASE_DIR, 'vendor.html')

    @app.route('/admin')
    def admin_page():
        return send_from_directory(BASE_DIR, 'admin.html')

    return app


if __name__ == '__main__':
    app = create_app()
    print(f"\n✅ Serving files from: {BASE_DIR}")
    print(f"🌐 Open: http://localhost:5000\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
