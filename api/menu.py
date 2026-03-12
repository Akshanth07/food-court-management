"""
Menu API
GET  /api/menu/vendors          — list all open vendors
GET  /api/menu/items            — all available menu items (optional ?vendor_id=X)
GET  /api/menu/items/<item_id>  — single item detail
"""

from flask import Blueprint, request, jsonify
from extensions import db, Vendor, MenuItem

menu_bp = Blueprint('menu', __name__)


@menu_bp.route('/vendors', methods=['GET'])
def get_vendors():
    vendors = Vendor.query.filter_by(is_open=True).all()
    return jsonify({'vendors': [v.to_dict() for v in vendors]}), 200


@menu_bp.route('/items', methods=['GET'])
def get_items():
    vendor_id = request.args.get('vendor_id', type=int)
    query = MenuItem.query.filter_by(is_available=True)
    if vendor_id:
        query = query.filter_by(vendor_id=vendor_id)
    items = query.all()
    return jsonify({'items': [i.to_dict() for i in items]}), 200


@menu_bp.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    return jsonify({'item': item.to_dict()}), 200
