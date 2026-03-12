"""
Orders API  (Customer-facing)
POST /api/orders/place          — place a new order, returns token number
GET  /api/orders/my             — get current user's orders
GET  /api/orders/<order_id>     — single order with tracking status
GET  /api/orders/token/<token>  — look up order by token number
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from extensions import Order, OrderItem, MenuItem, Vendor, TokenSequence
from config import Config

orders_bp = Blueprint('orders', __name__)


def _next_token():
    """Thread-safe token number generator."""
    seq = TokenSequence.query.get(1)
    if not seq:
        seq = TokenSequence(id=1, last_token=0)
        db.session.add(seq)
    seq.last_token += 1
    db.session.flush()
    return seq.last_token


def _calculate_billing(subtotal):
    tax      = round(subtotal * Config.TAX_RATE, 2)
    discount = round(subtotal * Config.DISCOUNT_RATE, 2) if subtotal >= Config.DISCOUNT_THRESHOLD else 0.0
    total    = round(subtotal + tax - discount, 2)
    return tax, discount, total


@orders_bp.route('/place', methods=['POST'])
@jwt_required()
def place_order():
    """
    Request body:
    {
      "items": [
        {"item_id": 1, "quantity": 2},
        {"item_id": 6, "quantity": 1}
      ]
    }
    """
    user_id = int(get_jwt_identity())
    data    = request.get_json()
    items   = data.get('items', [])

    if not items:
        return jsonify({'error': 'Cart is empty'}), 400

    subtotal = 0.0
    order_items_data = []

    for entry in items:
        item_id  = entry.get('item_id')
        quantity = entry.get('quantity', 1)

        menu_item = MenuItem.query.filter_by(item_id=item_id, is_available=True).first()
        if not menu_item:
            return jsonify({'error': f'Item {item_id} not available'}), 400

        line_total = float(menu_item.price) * quantity
        subtotal  += line_total
        order_items_data.append({
            'item_id':   item_id,
            'vendor_id': menu_item.vendor_id,
            'quantity':  quantity,
            'unit_price': float(menu_item.price)
        })

    tax, discount, total = _calculate_billing(subtotal)
    token_num = _next_token()

    order = Order(
        user_id      = user_id,
        token_number = token_num,
        subtotal     = subtotal,
        tax          = tax,
        discount     = discount,
        total        = total,
        status       = 'placed'
    )
    db.session.add(order)
    db.session.flush()   # get order_id

    for oi in order_items_data:
        db.session.add(OrderItem(
            order_id   = order.order_id,
            item_id    = oi['item_id'],
            vendor_id  = oi['vendor_id'],
            quantity   = oi['quantity'],
            unit_price = oi['unit_price'],
            item_status = 'pending'
        ))

    db.session.commit()

    return jsonify({
        'message':      'Order placed successfully',
        'token_number': token_num,
        'order':        order.to_dict()
    }), 201


@orders_bp.route('/my', methods=['GET'])
@jwt_required()
def my_orders():
    user_id = int(get_jwt_identity())
    orders  = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    return jsonify({'orders': [o.to_dict() for o in orders]}), 200


@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    user_id = int(get_jwt_identity())
    order   = Order.query.filter_by(order_id=order_id, user_id=user_id).first_or_404()
    return jsonify({'order': order.to_dict()}), 200


@orders_bp.route('/token/<int:token_num>', methods=['GET'])
@jwt_required()
def get_by_token(token_num):
    order = Order.query.filter_by(token_number=token_num).order_by(Order.created_at.desc()).first_or_404()
    return jsonify({'order': order.to_dict()}), 200


@orders_bp.route('/<int:order_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_order(order_id):
    user_id = int(get_jwt_identity())
    order   = Order.query.filter_by(order_id=order_id, user_id=user_id).first_or_404()

    if order.status not in ('placed', 'confirmed'):
        return jsonify({'error': 'Order cannot be cancelled at this stage'}), 400

    order.status = 'cancelled'
    db.session.commit()
    return jsonify({'message': 'Order cancelled', 'order': order.to_dict()}), 200
