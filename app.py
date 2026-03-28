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
    app = Flask(__name__, static_folder=os.path.join(BASE_DIR, 'static'), static_url_path='/static')
    app.config.from_object(Config)
    CORS(app, supports_credentials=True)
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    app.register_blueprint(auth_bp,   url_prefix='/api/auth')
    app.register_blueprint(menu_bp,   url_prefix='/api/menu')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(vendor_bp, url_prefix='/api/vendor')
    app.register_blueprint(admin_bp,  url_prefix='/api/admin')

    # ── Page Routes ────────────────────────────────────────────
    @app.route('/')
    def index(): return send_from_directory(BASE_DIR, 'login.html')

    @app.route('/login')
    def login_page(): return send_from_directory(BASE_DIR, 'login.html')

    @app.route('/customer')
    def customer_page(): return send_from_directory(BASE_DIR, 'customer.html')

    @app.route('/vendor')
    def vendor_page(): return send_from_directory(BASE_DIR, 'vendor.html')

    @app.route('/admin')
    def admin_page(): return send_from_directory(BASE_DIR, 'admin.html')

    @app.route('/health')
    def health(): return {'status': 'ok'}, 200

    # ── Init DB ────────────────────────────────────────────────
    @app.route('/init-db')
    def init_db_route():
        try:
            from extensions import User, Vendor, MenuItem, TokenSequence
            db.create_all()
            if User.query.count() > 0:
                return 'Database already initialized!', 200
            pw = bcrypt.generate_password_hash('password123').decode('utf-8')
            users = [
                User(name='Admin User',    email='admin@foodcourt.com',  password=pw, role='admin'),
                User(name='Ravi Kumar',    email='ravi@spicegarden.com', password=pw, role='vendor'),
                User(name='Quick Bites',   email='priya@quickbites.com', password=pw, role='vendor'),
                User(name='Test Customer', email='customer@test.com',    password=pw, role='customer'),
                User(name='John Doe',      email='john@test.com',        password=pw, role='customer'),
            ]
            for u in users: db.session.add(u)
            db.session.flush()
            vendors = [
                Vendor(user_id=users[1].user_id, name='Spice Garden', emoji='🌶', description='North Indian cuisine'),
                Vendor(user_id=users[2].user_id, name='Quick Bites',  emoji='🍔', description='Fast food'),
            ]
            for v in vendors: db.session.add(v)
            db.session.flush()
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
            db.session.add(TokenSequence(id=1, last_token=0))
            db.session.commit()
            return 'Database initialized successfully!', 200
        except Exception as e:
            db.session.rollback()
            return f'Error: {str(e)}', 500

    # ── Fix Quick Bites → Slice Heaven ─────────────────────────
    @app.route('/fix-quickbites')
    def fix_quickbites():
        try:
            from extensions import User, Vendor, MenuItem
            vendor = Vendor.query.filter_by(name='Quick Bites').first()
            if not vendor:
                return 'Quick Bites not found — already fixed or does not exist.', 200
            vendor.name        = 'Slice Heaven'
            vendor.description = 'Wood-fired pizzas, pastas & garlic bread'
            vendor.emoji       = '🍕'
            user = User.query.get(vendor.user_id)
            if user:
                user.name  = 'Slice Heaven'
                user.email = 'slice@sliceheaven.com'
            MenuItem.query.filter_by(vendor_id=vendor.vendor_id).delete()
            db.session.flush()
            items = [
                MenuItem(vendor_id=vendor.vendor_id, name='Margherita Pizza',    price=200, emoji='🍕', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='BBQ Chicken Pizza',   price=250, emoji='🍕', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Pepperoni Pizza',     price=270, emoji='🍕', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Farmhouse Pizza',     price=230, emoji='🍕', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Garlic Bread',        price=80,  emoji='🥖', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Cheesy Garlic Bread', price=100, emoji='🧀', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Pasta Arrabbiata',    price=160, emoji='🍝', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Penne Alfredo',       price=170, emoji='🍝', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Bruschetta',          price=90,  emoji='🍞', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Tiramisu',            price=120, emoji='☕', is_available=True),
            ]
            for m in items: db.session.add(m)
            db.session.commit()
            return f'Done! Quick Bites renamed to Slice Heaven with {len(items)} items. Login: slice@sliceheaven.com / password123', 200
        except Exception as e:
            db.session.rollback()
            return f'Error: {str(e)}', 500

    # ── Add Burger Barn ────────────────────────────────────────
    @app.route('/add-burgerbarn')
    def add_burgerbarn():
        try:
            from extensions import User, Vendor, MenuItem
            if User.query.filter_by(email='burger@barnfood.com').first():
                return 'Burger Barn already exists! Login: burger@barnfood.com / password123', 200
            pw = bcrypt.generate_password_hash('password123').decode('utf-8')
            user = User(name='Burger Barn', email='burger@barnfood.com', password=pw, role='vendor')
            db.session.add(user)
            db.session.flush()
            vendor = Vendor(user_id=user.user_id, name='Burger Barn', emoji='🍔', description='Burgers and fast food')
            db.session.add(vendor)
            db.session.flush()
            items = [
                MenuItem(vendor_id=vendor.vendor_id, name='Classic Burger',   price=120, emoji='🍔', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Chicken Burger',   price=150, emoji='🍗', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Cheese Burger',    price=160, emoji='🍔', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Veggie Wrap',      price=100, emoji='🌮', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Loaded Fries',     price=80,  emoji='🍟', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Onion Rings',      price=70,  emoji='🧅', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Milkshake',        price=90,  emoji='🥤', is_available=True),
            ]
            for m in items: db.session.add(m)
            db.session.commit()
            return f'Burger Barn added with {len(items)} items! Login: burger@barnfood.com / password123', 200
        except Exception as e:
            db.session.rollback()
            return f'Error: {str(e)}', 500

    # ── Add Wok and Roll ───────────────────────────────────────
    @app.route('/add-wokandroll')
    def add_wokandroll():
        try:
            from extensions import User, Vendor, MenuItem
            if User.query.filter_by(email='wok@rollfood.com').first():
                return 'Wok and Roll already exists! Login: wok@rollfood.com / password123', 200
            pw = bcrypt.generate_password_hash('password123').decode('utf-8')
            user = User(name='Wok and Roll', email='wok@rollfood.com', password=pw, role='vendor')
            db.session.add(user)
            db.session.flush()
            vendor = Vendor(user_id=user.user_id, name='Wok and Roll', emoji='🍜', description='Chinese and Asian cuisine')
            db.session.add(vendor)
            db.session.flush()
            items = [
                MenuItem(vendor_id=vendor.vendor_id, name='Hakka Noodles',   price=100, emoji='🍜', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Chicken Noodles', price=130, emoji='🍝', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Fried Rice',      price=110, emoji='🥡', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Chilli Chicken',  price=160, emoji='🍗', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Momos',           price=80,  emoji='🥟', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Spring Rolls',    price=70,  emoji='🥢', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Manchurian',      price=90,  emoji='🍲', is_available=True),
            ]
            for m in items: db.session.add(m)
            db.session.commit()
            return f'Wok and Roll added with {len(items)} items! Login: wok@rollfood.com / password123', 200
        except Exception as e:
            db.session.rollback()
            return f'Error: {str(e)}', 500

    # ── Add Sweet Spot (Desserts) ──────────────────────────────
    @app.route('/add-sweetspot')
    def add_sweetspot():
        try:
            from extensions import User, Vendor, MenuItem
            if User.query.filter_by(email='sweet@sweetspot.com').first():
                return 'Sweet Spot already exists! Login: sweet@sweetspot.com / password123', 200
            pw = bcrypt.generate_password_hash('password123').decode('utf-8')
            user = User(name='Sweet Spot', email='sweet@sweetspot.com', password=pw, role='vendor')
            db.session.add(user)
            db.session.flush()
            vendor = Vendor(
                user_id=user.user_id,
                name='Sweet Spot',
                emoji='🍰',
                description='Desserts, sweets & frozen treats from around the world'
            )
            db.session.add(vendor)
            db.session.flush()
            items = [
                # ── Indian Classics ──────────────────────────────────
                MenuItem(vendor_id=vendor.vendor_id, name='Gulab Jamun',          price=60,  emoji='🟤', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Rasgulla',             price=60,  emoji='⚪', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Gajar Halwa',          price=80,  emoji='🥕', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Kheer',                price=70,  emoji='🍚', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Jalebi',               price=50,  emoji='🌀', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Kaju Katli',           price=90,  emoji='💎', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Rasmalai',             price=80,  emoji='🍮', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Ladoo',                price=55,  emoji='🟡', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Malpua',               price=70,  emoji='🥞', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Shahi Tukda',          price=85,  emoji='🍞', is_available=True),
                # ── Cakes & Bakes ────────────────────────────────────
                MenuItem(vendor_id=vendor.vendor_id, name='Chocolate Lava Cake',  price=110, emoji='🍫', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='New York Cheesecake',  price=120, emoji='🍰', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Red Velvet Cake',      price=100, emoji='❤️', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Tiramisu',             price=130, emoji='☕', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Brownie',              price=70,  emoji='🟫', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Pineapple Pastry',     price=80,  emoji='🍍', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Black Forest Cake',    price=100, emoji='🍒', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Blueberry Muffin',     price=60,  emoji='🫐', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Croissant',            price=55,  emoji='🥐', is_available=True),
                # ── Ice Creams & Frozen ───────────────────────────────
                MenuItem(vendor_id=vendor.vendor_id, name='Vanilla Ice Cream',    price=70,  emoji='🍦', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Chocolate Ice Cream',  price=70,  emoji='🍫', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Mango Ice Cream',      price=80,  emoji='🥭', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Butterscotch Sundae',  price=90,  emoji='🍨', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Kulfi',                price=60,  emoji='🍡', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Falooda',              price=90,  emoji='🥤', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Waffle Ice Cream',     price=100, emoji='🧇', is_available=True),
                # ── Mousse & Fine Desserts ────────────────────────────
                MenuItem(vendor_id=vendor.vendor_id, name='Chocolate Mousse',     price=90,  emoji='🍮', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Choco Fondue',         price=130, emoji='🍓', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Panna Cotta',          price=100, emoji='🍮', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Creme Brulee',         price=120, emoji='🔥', is_available=True),
                # ── Waffles & Crepes ─────────────────────────────────
                MenuItem(vendor_id=vendor.vendor_id, name='Nutella Waffle',        price=110, emoji='🧇', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Strawberry Crepe',      price=90,  emoji='🍓', is_available=True),
                MenuItem(vendor_id=vendor.vendor_id, name='Banana Nutella Crepe',  price=95,  emoji='🍌', is_available=True),
            ]
            for m in items:
                db.session.add(m)
            db.session.commit()
            return f'Sweet Spot added with {len(items)} desserts! Login: sweet@sweetspot.com / password123', 200
        except Exception as e:
            db.session.rollback()
            return f'Error: {str(e)}', 500

    # ── Fix Passwords ──────────────────────────────────────────
    @app.route('/fix-passwords')
    def fix_passwords():
        try:
            from extensions import User
            users = User.query.all()
            pw = bcrypt.generate_password_hash('password123').decode('utf-8')
            count = 0
            for u in users:
                u.password = pw
                count += 1
            db.session.commit()
            return f'Reset passwords for {count} users to password123', 200
        except Exception as e:
            db.session.rollback()
            return f'Error: {str(e)}', 500

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"\n Serving from: {BASE_DIR}")
    print(f" Open: http://localhost:{port}\n")
    app.run(debug=False, host='0.0.0.0', port=port)
