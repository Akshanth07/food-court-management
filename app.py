"""
Smart Food Court Management System
Flask + MySQL Backend

Local:    python app.py  →  http://localhost:5000
Railway:  Auto-deployed via GitHub
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

    # ── Serve HTML Pages ───────────────────────────────────
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

    # ── Health check for Railway ───────────────────────────
    @app.route('/health')
    def health():
        return {'status': 'ok'}, 200

    # ── One-time DB init (visit /init-db to set up tables) ─
    @app.route('/init-db')
    def init_db_route():
        try:
            from extensions import User, Vendor, MenuItem, TokenSequence, Order, OrderItem
            db.create_all()
            # Check if already seeded
            if User.query.count() > 0:
                return 'Database already initialized! Tables exist.', 200
            # Seed users
            from extensions import bcrypt as bc
            pw = bc.generate_password_hash('password123').decode('utf-8')
            users = [
                User(name='Admin User',    email='admin@foodcourt.com',    password=pw, role='admin'),
                User(name='Ravi Kumar',    email='ravi@spicegarden.com',   password=pw, role='vendor'),
                User(name='Priya Sharma',  email='priya@quickbites.com',   password=pw, role='vendor'),
                User(name='Test Customer', email='customer@test.com',      password=pw, role='customer'),
                User(name='John Doe',      email='john@test.com',          password=pw, role='customer'),
            ]
            for u in users: db.session.add(u)
            db.session.flush()
            # Seed vendors
            vendors = [
                Vendor(user_id=users[1].user_id, name='Spice Garden',  emoji='🍛', description='North Indian cuisine'),
                Vendor(user_id=users[2].user_id, name='Quick Bites',   emoji='🍔', description='Fast food'),
            ]
            for v in vendors: db.session.add(v)
            db.session.flush()
            # Seed menu items
            items = [
                MenuItem(vendor_id=vendors[0].vendor_id, name='Butter Chicken',  price=180, emoji='🍗', is_available=True),
                MenuItem(vendor_id=vendors[0].vendor_id, name='Paneer Tikka',    price=140, emoji='🧀', is_available=True),
                MenuItem(vendor_id=vendors[0].vendor_id, name='Dal Makhani',     price=120, emoji='🫘', is_available=True),
                MenuItem(vendor_id=vendors[0].vendor_id, name='Chicken Biryani', price=200, emoji='🍚', is_available=True),
                MenuItem(vendor_id=vendors[1].vendor_id, name='Veg Burger',      price=80,  emoji='🍔', is_available=True),
                MenuItem(vendor_id=vendors[1].vendor_id, name='French Fries',    price=60,  emoji='🍟', is_available=True),
                MenuItem(vendor_id=vendors[1].vendor_id, name='Cold Coffee',     price=90,  emoji='☕', is_available=True),
            ]
            for m in items: db.session.add(m)
            # Seed token sequence
            db.session.add(TokenSequence(id=1, last_token=0))
            db.session.commit()
            return 'Database initialized successfully! All tables and demo data created.', 200
        except Exception as e:
            db.session.rollback()
            return f'Error: {str(e)}', 500

    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    print(f"\n✅ Serving from: {BASE_DIR}")
    print(f"🌐 Open: http://localhost:{port}\n")
    app.run(debug=False, host='0.0.0.0', port=port)
