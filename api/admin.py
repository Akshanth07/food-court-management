"""
Admin API  (Admin dashboard — requires admin role)
GET /api/admin/stats            — overall KPIs: revenue, orders, customers
GET /api/admin/revenue/weekly   — last 7 days revenue per day
GET /api/admin/vendors          — all vendors with today's stats
GET /api/admin/bestsellers      — top selling items today
GET /api/admin/queue            — live queue across all vendors
GET /api/admin/alerts           — system alerts (low stock hints, peak hours)
PUT /api/admin/vendors/<id>     — update vendor (open/close, details)
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db, User, Vendor, MenuItem, Order, OrderItem
from datetime import datetime, date, timedelta
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)


def _require_admin(user_id):
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return False
    return True


# ── Overall Stats ─────────────────────────────────────────

@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
def overall_stats():
    user_id = int(get_jwt_identity())
    if not _require_admin(user_id):
        return jsonify({'error': 'Admin access required'}), 403

    today = date.today()

    today_orders = Order.query.filter(
        func.date(Order.created_at) == today,
        Order.status != 'cancelled'
    ).all()

    total_revenue    = sum(float(o.total) for o in today_orders)
    total_orders     = len(today_orders)
    avg_order_value  = round(total_revenue / total_orders, 2) if total_orders else 0
    active_customers = db.session.query(func.count(func.distinct(Order.user_id))).filter(
        func.date(Order.created_at) == today,
        Order.status != 'cancelled'
    ).scalar() or 0

    # Yesterday comparison
    yesterday = today - timedelta(days=1)
    yest_revenue = db.session.query(func.sum(Order.total)).filter(
        func.date(Order.created_at) == yesterday,
        Order.status != 'cancelled'
    ).scalar() or 0
    yest_orders = Order.query.filter(
        func.date(Order.created_at) == yesterday,
        Order.status != 'cancelled'
    ).count()

    rev_change = round(((total_revenue - float(yest_revenue)) / float(yest_revenue) * 100), 1) if yest_revenue else 0
    ord_change = total_orders - yest_orders

    return jsonify({
        'today_revenue':    round(total_revenue, 2),
        'today_orders':     total_orders,
        'avg_order_value':  avg_order_value,
        'active_customers': active_customers,
        'revenue_change':   rev_change,
        'orders_change':    ord_change
    }), 200


# ── Weekly Revenue ────────────────────────────────────────

@admin_bp.route('/revenue/weekly', methods=['GET'])
@jwt_required()
def weekly_revenue():
    user_id = int(get_jwt_identity())
    if not _require_admin(user_id): return jsonify({'error': 'Admin access required'}), 403

    today  = date.today()
    days   = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    result = []

    for d in days:
        row = db.session.query(
            func.coalesce(func.sum(Order.total), 0).label('revenue'),
            func.count(Order.order_id).label('orders')
        ).filter(
            func.date(Order.created_at) == d,
            Order.status != 'cancelled'
        ).first()
        result.append({
            'date':    d.strftime('%Y-%m-%d'),
            'day':     d.strftime('%a'),
            'revenue': round(float(row.revenue), 2),
            'orders':  row.orders
        })

    return jsonify({'weekly': result}), 200


# ── Vendor Performance ────────────────────────────────────

@admin_bp.route('/vendors', methods=['GET'])
@jwt_required()
def all_vendors():
    user_id = int(get_jwt_identity())
    if not _require_admin(user_id): return jsonify({'error': 'Admin access required'}), 403

    today   = date.today()
    vendors = Vendor.query.all()
    result  = []

    for v in vendors:
        rev = db.session.query(func.coalesce(func.sum(OrderItem.unit_price * OrderItem.quantity), 0)).join(
            Order, OrderItem.order_id == Order.order_id
        ).filter(
            OrderItem.vendor_id == v.vendor_id,
            func.date(Order.created_at) == today,
            Order.status != 'cancelled'
        ).scalar() or 0

        orders = db.session.query(func.count(func.distinct(Order.order_id))).join(
            OrderItem, Order.order_id == OrderItem.order_id
        ).filter(
            OrderItem.vendor_id == v.vendor_id,
            func.date(Order.created_at) == today,
            Order.status != 'cancelled'
        ).scalar() or 0

        d = v.to_dict()
        d['today_revenue'] = round(float(rev), 2)
        d['today_orders']  = orders
        result.append(d)

    return jsonify({'vendors': result}), 200


# ── Best Sellers ──────────────────────────────────────────

@admin_bp.route('/bestsellers', methods=['GET'])
@jwt_required()
def bestsellers():
    user_id = int(get_jwt_identity())
    if not _require_admin(user_id): return jsonify({'error': 'Admin access required'}), 403

    today = date.today()
    rows  = (db.session.query(
                MenuItem.name,
                MenuItem.emoji,
                Vendor.name.label('vendor_name'),
                func.sum(OrderItem.quantity).label('total_sold')
             )
             .join(OrderItem, MenuItem.item_id == OrderItem.item_id)
             .join(Order, OrderItem.order_id == Order.order_id)
             .join(Vendor, MenuItem.vendor_id == Vendor.vendor_id)
             .filter(func.date(Order.created_at) == today, Order.status != 'cancelled')
             .group_by(MenuItem.item_id, MenuItem.name, MenuItem.emoji, Vendor.name)
             .order_by(func.sum(OrderItem.quantity).desc())
             .limit(10).all())

    return jsonify({
        'bestsellers': [
            {'rank': i+1, 'name': r[0], 'emoji': r[1],
             'vendor': r[2], 'sold': int(r[3])}
            for i, r in enumerate(rows)
        ]
    }), 200


# ── Live Queue ────────────────────────────────────────────

@admin_bp.route('/queue', methods=['GET'])
@jwt_required()
def live_queue():
    user_id = int(get_jwt_identity())
    if not _require_admin(user_id): return jsonify({'error': 'Admin access required'}), 403

    active = Order.query.filter(
        Order.status.in_(['placed','confirmed','preparing','ready'])
    ).order_by(Order.token_number).all()

    return jsonify({'queue': [o.to_dict() for o in active]}), 200


# ── Alerts ────────────────────────────────────────────────

@admin_bp.route('/alerts', methods=['GET'])
@jwt_required()
def alerts():
    user_id = int(get_jwt_identity())
    if not _require_admin(user_id): return jsonify({'error': 'Admin access required'}), 403

    alerts_list = []

    # Vendors that are closed
    closed = Vendor.query.filter_by(is_open=False).all()
    for v in closed:
        alerts_list.append({
            'type': 'warn', 'icon': '⚠️',
            'title': f'{v.name} is closed',
            'desc':  'Vendor has paused order acceptance'
        })

    # Long queue warning (> 10 active orders)
    active_count = Order.query.filter(
        Order.status.in_(['placed','confirmed','preparing'])
    ).count()
    if active_count > 10:
        alerts_list.append({
            'type': 'warn', 'icon': '🕐',
            'title': f'High queue load: {active_count} active orders',
            'desc':  'Consider alerting vendors to increase pace'
        })

    # All good
    if not alerts_list:
        alerts_list.append({
            'type': 'ok', 'icon': '✅',
            'title': 'All systems operational',
            'desc':  f'All {Vendor.query.filter_by(is_open=True).count()} vendors online'
        })

    return jsonify({'alerts': alerts_list}), 200


# ── Vendor Management ─────────────────────────────────────

@admin_bp.route('/vendors/<int:vendor_id>', methods=['PUT'])
@jwt_required()
def update_vendor(vendor_id):
    user_id = int(get_jwt_identity())
    if not _require_admin(user_id): return jsonify({'error': 'Admin access required'}), 403

    vendor = Vendor.query.get_or_404(vendor_id)
    data   = request.get_json()

    for field in ['name', 'description', 'emoji', 'is_open']:
        if field in data:
            setattr(vendor, field, data[field])

    db.session.commit()
    return jsonify({'message': 'Vendor updated', 'vendor': vendor.to_dict()}), 200
