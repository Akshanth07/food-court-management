"""
Vendor API  (Vendor dashboard — requires vendor role)
GET  /api/vendor/orders             — live incoming orders for this vendor
POST /api/vendor/orders/<id>/status — advance order item status
GET  /api/vendor/menu               — vendor's menu items
POST /api/vendor/menu               — add new menu item
PUT  /api/vendor/menu/<item_id>     — update menu item (price / availability)
DELETE /api/vendor/menu/<item_id>   — delete menu item
GET  /api/vendor/stats              — today's revenue, order count, avg prep time
POST /api/vendor/toggle             — open / close stall
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from extensions import User, Vendor, MenuItem, Order, OrderItem
from datetime import datetime, date
from sqlalchemy import func

vendor_bp = Blueprint('vendor', __name__)


def _get_vendor(user_id):
    return Vendor.query.filter_by(user_id=user_id).first()


def _require_vendor(user_id):
    user = User.query.get(user_id)
    if not user or user.role not in ('vendor', 'admin'):
        return None, ({'error': 'Vendor access required'}, 403)
    vendor = _get_vendor(user_id)
    if not vendor:
        return None, ({'error': 'No vendor profile found'}, 404)
    return vendor, None


# ── Live Orders ───────────────────────────────────────────

@vendor_bp.route('/orders', methods=['GET'])
@jwt_required()
def vendor_orders():
    user_id = int(get_jwt_identity())
    vendor, err = _require_vendor(user_id)
    if err: return jsonify(err[0]), err[1]

    status_filter = request.args.get('status')

    query = (db.session.query(Order, OrderItem)
             .join(OrderItem, Order.order_id == OrderItem.order_id)
             .filter(OrderItem.vendor_id == vendor.vendor_id,
                     Order.status != 'cancelled'))

    if status_filter:
        query = query.filter(OrderItem.item_status == status_filter)

    rows = query.order_by(Order.created_at.desc()).all()

    # Group by order
    seen = {}
    for order, oi in rows:
        if order.order_id not in seen:
            seen[order.order_id] = {
                'order_id':     order.order_id,
                'token_number': order.token_number,
                'status':       order.status,
                'created_at':   order.created_at.strftime('%I:%M %p'),
                'total':        float(order.total),
                'items':        []
            }
        seen[order.order_id]['items'].append(oi.to_dict())

    return jsonify({'orders': list(seen.values())}), 200


@vendor_bp.route('/orders/<int:order_item_id>/status', methods=['POST'])
@jwt_required()
def update_item_status(order_item_id):
    user_id = int(get_jwt_identity())
    vendor, err = _require_vendor(user_id)
    if err: return jsonify(err[0]), err[1]

    data       = request.get_json()
    new_status = (data.get('status') or '').strip()
    if new_status not in ['pending','preparing','ready','collected']:
        return jsonify({'error': 'Invalid status'}), 400

    oi = OrderItem.query.filter_by(order_item_id=order_item_id,
                                   vendor_id=vendor.vendor_id).first_or_404()
    oi.item_status = new_status

    # If all items in the order are ready/done, update parent order status
    order = Order.query.get(oi.order_id)
    all_items = OrderItem.query.filter_by(order_id=oi.order_id).all()
    statuses  = {i.item_status for i in all_items}

    if statuses <= {'collected'}:
        order.status = 'collected'
    elif statuses <= {'ready', 'collected'}:
        order.status = 'ready'
    elif 'preparing' in statuses:
        order.status = 'preparing'
    else:
        order.status = 'placed'

    db.session.commit()
    return jsonify({'message': 'Status updated', 'item_status': new_status, 'order_status': order.status}), 200


# ── Menu Management ───────────────────────────────────────

@vendor_bp.route('/menu', methods=['GET'])
@jwt_required()
def get_vendor_menu():
    user_id = int(get_jwt_identity())
    vendor, err = _require_vendor(user_id)
    if err: return jsonify(err[0]), err[1]

    items = MenuItem.query.filter_by(vendor_id=vendor.vendor_id).all()
    return jsonify({'items': [i.to_dict() for i in items]}), 200


@vendor_bp.route('/menu', methods=['POST'])
@jwt_required()
def add_menu_item():
    user_id = int(get_jwt_identity())
    vendor, err = _require_vendor(user_id)
    if err: return jsonify(err[0]), err[1]

    data = request.get_json()
    item = MenuItem(
        vendor_id   = vendor.vendor_id,
        name        = data.get('name'),
        description = data.get('description', ''),
        price       = data.get('price'),
        emoji       = data.get('emoji', '🍱'),
        is_veg      = data.get('is_veg', False),
        is_spicy    = data.get('is_spicy', False),
        is_available= data.get('is_available', True)
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({'message': 'Item added', 'item': item.to_dict()}), 201


@vendor_bp.route('/menu/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_menu_item(item_id):
    user_id = int(get_jwt_identity())
    vendor, err = _require_vendor(user_id)
    if err: return jsonify(err[0]), err[1]

    item = MenuItem.query.filter_by(item_id=item_id, vendor_id=vendor.vendor_id).first_or_404()
    data = request.get_json()

    for field in ['name', 'description', 'price', 'emoji', 'is_veg', 'is_spicy', 'is_available']:
        if field in data:
            setattr(item, field, data[field])

    db.session.commit()
    return jsonify({'message': 'Item updated', 'item': item.to_dict()}), 200


@vendor_bp.route('/menu/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_menu_item(item_id):
    user_id = int(get_jwt_identity())
    vendor, err = _require_vendor(user_id)
    if err: return jsonify(err[0]), err[1]

    item = MenuItem.query.filter_by(item_id=item_id, vendor_id=vendor.vendor_id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Item deleted'}), 200


# ── Stats ─────────────────────────────────────────────────

@vendor_bp.route('/stats', methods=['GET'])
@jwt_required()
def vendor_stats():
    user_id = int(get_jwt_identity())
    vendor, err = _require_vendor(user_id)
    if err: return jsonify(err[0]), err[1]

    today = date.today()

    # Today's orders for this vendor
    today_orders = (db.session.query(Order)
                    .join(OrderItem, Order.order_id == OrderItem.order_id)
                    .filter(OrderItem.vendor_id == vendor.vendor_id,
                            func.date(Order.created_at) == today,
                            Order.status != 'cancelled')
                    .distinct().all())

    total_revenue = sum(
        float(oi.unit_price) * oi.quantity
        for o in today_orders
        for oi in o.items
        if oi.vendor_id == vendor.vendor_id
    )

    pending_count = sum(
        1 for o in today_orders
        for oi in o.items
        if oi.vendor_id == vendor.vendor_id and oi.item_status == 'pending'
    )

    # Top selling items
    top_items = (db.session.query(MenuItem.name, func.sum(OrderItem.quantity).label('sold'))
                 .join(OrderItem, MenuItem.item_id == OrderItem.item_id)
                 .join(Order, OrderItem.order_id == Order.order_id)
                 .filter(OrderItem.vendor_id == vendor.vendor_id,
                         func.date(Order.created_at) == today,
                         Order.status != 'cancelled')
                 .group_by(MenuItem.name)
                 .order_by(func.sum(OrderItem.quantity).desc())
                 .limit(5).all())

    return jsonify({
        'vendor':        vendor.to_dict(),
        'today_revenue': round(total_revenue, 2),
        'today_orders':  len(today_orders),
        'pending_items': pending_count,
        'top_items':     [{'name': r[0], 'sold': int(r[1])} for r in top_items]
    }), 200


@vendor_bp.route('/toggle', methods=['POST'])
@jwt_required()
def toggle_open():
    user_id = int(get_jwt_identity())
    vendor, err = _require_vendor(user_id)
    if err: return jsonify(err[0]), err[1]

    vendor.is_open = not vendor.is_open
    db.session.commit()
    return jsonify({'is_open': vendor.is_open}), 200
