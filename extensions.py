from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from datetime import datetime

db     = SQLAlchemy()
jwt    = JWTManager()
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = 'users'
    user_id    = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(150), unique=True, nullable=False)
    password   = db.Column(db.String(255), nullable=False)
    role       = db.Column(db.String(20), default='customer')
    phone      = db.Column(db.String(15))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {'user_id': self.user_id, 'name': self.name,
                'email': self.email, 'role': self.role, 'phone': self.phone}


class Vendor(db.Model):
    __tablename__ = 'vendors'
    vendor_id   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    name        = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    emoji       = db.Column(db.String(10), default='🍽')
    is_open     = db.Column(db.Boolean, default=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    menu_items  = db.relationship('MenuItem', backref='vendor', lazy=True)

    def to_dict(self):
        return {'vendor_id': self.vendor_id, 'name': self.name,
                'description': self.description, 'emoji': self.emoji,
                'is_open': self.is_open}


class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    item_id      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vendor_id    = db.Column(db.Integer, db.ForeignKey('vendors.vendor_id'), nullable=False)
    name         = db.Column(db.String(100), nullable=False)
    description  = db.Column(db.Text)
    price        = db.Column(db.Numeric(8,2), nullable=False)
    emoji        = db.Column(db.String(10), default='🍱')
    is_veg       = db.Column(db.Boolean, default=False)
    is_spicy     = db.Column(db.Boolean, default=False)
    is_available = db.Column(db.Boolean, default=True)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'item_id': self.item_id, 'vendor_id': self.vendor_id,
            'vendor_name': self.vendor.name if self.vendor else '',
            'name': self.name, 'description': self.description,
            'price': float(self.price), 'emoji': self.emoji,
            'is_veg': self.is_veg, 'is_spicy': self.is_spicy,
            'is_available': self.is_available
        }


class TokenSequence(db.Model):
    __tablename__ = 'token_sequence'
    id         = db.Column(db.Integer, primary_key=True, default=1)
    last_token = db.Column(db.Integer, default=0)


class Order(db.Model):
    __tablename__ = 'orders'
    order_id     = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    token_number = db.Column(db.Integer, nullable=False)
    subtotal     = db.Column(db.Numeric(8,2), nullable=False)
    tax          = db.Column(db.Numeric(8,2), default=0)
    discount     = db.Column(db.Numeric(8,2), default=0)
    total        = db.Column(db.Numeric(8,2), nullable=False)
    status       = db.Column(db.String(20), default='placed')
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at   = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    items        = db.relationship('OrderItem', backref='order', lazy=True)

    def to_dict(self):
        return {
            'order_id': self.order_id, 'token_number': self.token_number,
            'subtotal': float(self.subtotal), 'tax': float(self.tax),
            'discount': float(self.discount), 'total': float(self.total),
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'items': [i.to_dict() for i in self.items]
        }


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    order_item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id      = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    item_id       = db.Column(db.Integer, db.ForeignKey('menu_items.item_id'), nullable=False)
    vendor_id     = db.Column(db.Integer, db.ForeignKey('vendors.vendor_id'), nullable=False)
    quantity      = db.Column(db.Integer, nullable=False, default=1)
    unit_price    = db.Column(db.Numeric(8,2), nullable=False)
    item_status   = db.Column(db.String(20), default='pending')
    menu_item     = db.relationship('MenuItem')
    vendor        = db.relationship('Vendor')

    def to_dict(self):
        return {
            'order_item_id': self.order_item_id,
            'item_id': self.item_id,
            'item_name': self.menu_item.name if self.menu_item else '',
            'emoji': self.menu_item.emoji if self.menu_item else '🍱',
            'vendor_id': self.vendor_id,
            'vendor_name': self.vendor.name if self.vendor else '',
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'subtotal': float(self.unit_price) * self.quantity,
            'item_status': self.item_status
        }
