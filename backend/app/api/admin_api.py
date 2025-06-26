# backend/app/api/admin_api.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

from app.extension import db
from app.models import Product, Category, Order, OrderItem, User, OrderStatus

admin_api = Blueprint('admin_api', __name__)

def is_admin(user_id):
    user = User.query.get(user_id)
    return user and user.is_admin

def validate_product_data(data):
    errors = []
    name = data.get('name', '').strip()
    price = data.get('price')
    cat_id = data.get('category_id')
    if not name:
        errors.append('Name is required')
    if price is None or not isinstance(price, (int, float)) or price <= 0:
        errors.append('Price must be a positive number')
    if not Category.query.get(cat_id):
        errors.append('Invalid category_id')
    return errors

@admin_api.route('/products', methods=['GET'])
@jwt_required()
def get_all_products():
    uid = get_jwt_identity()
    if not is_admin(uid):
        return jsonify({'error': 'Unauthorized access'}), 403

    prods = Product.query.all()
    return jsonify([p.to_dict() for p in prods]), 200

@admin_api.route('/products', methods=['POST'])
@jwt_required()
def create_product():
    uid = get_jwt_identity()
    if not is_admin(uid):
        return jsonify({'error': 'Unauthorized access'}), 403

    data = request.get_json() or {}
    errors = validate_product_data(data)
    if errors:
        return jsonify({'errors': errors}), 400

    p = Product(
        name=data['name'].strip(),
        price=data['price'],
        category_id=data['category_id'],
        description=data.get('description', '').strip(),
        stock=data.get('stock', 0),
        popularity=data.get('popularity', 0)
    )
    db.session.add(p)
    db.session.commit()
    return jsonify({'message': 'Product created', 'product': p.to_dict()}), 201

@admin_api.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    uid = get_jwt_identity()
    if not is_admin(uid):
        return jsonify({'error': 'Unauthorized access'}), 403

    p = Product.query.get_or_404(product_id)
    data = request.get_json() or {}
    errors = validate_product_data(data)
    if errors:
        return jsonify({'errors': errors}), 400

    p.name = data['name'].strip()
    p.price = data['price']
    p.category_id = data['category_id']
    p.description = data.get('description', p.description).strip()
    p.stock = data.get('stock', p.stock)
    p.popularity = data.get('popularity', p.popularity)
    db.session.commit()
    return jsonify({'message': 'Product updated', 'product': p.to_dict()}), 200

@admin_api.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    uid = get_jwt_identity()
    if not is_admin(uid):
        return jsonify({'error': 'Unauthorized access'}), 403

    p = Product.query.get_or_404(product_id)
    db.session.delete(p)
    db.session.commit()
    return '', 204

@admin_api.route('/orders', methods=['GET'])
@jwt_required()
def get_all_orders():
    uid = get_jwt_identity()
    if not is_admin(uid):
        return jsonify({'error': 'Unauthorized access'}), 403

    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify([o.to_dict() for o in orders]), 200

@admin_api.route('/orders/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order_details(order_id):
    uid = get_jwt_identity()
    if not is_admin(uid):
        return jsonify({'error': 'Unauthorized access'}), 403

    o = Order.query.get_or_404(order_id)
    return jsonify(o.to_dict()), 200

@admin_api.route('/orders/<int:order_id>', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    uid = get_jwt_identity()
    if not is_admin(uid):
        return jsonify({'error': 'Unauthorized access'}), 403

    data = request.get_json() or {}
    status = data.get('status', '').strip()
    if not status or status not in OrderStatus.__members__:
        return jsonify({'error': 'Invalid status'}), 400

    o = Order.query.get_or_404(order_id)
    o.status = OrderStatus[status]
    db.session.commit()
    return jsonify({'message': 'Order status updated', 'order': o.to_dict()}), 200

@admin_api.route('/categories', methods=['GET'])
@jwt_required()
def get_all_categories():
    uid = get_jwt_identity()
    if not is_admin(uid):
        return jsonify({'error': 'Unauthorized access'}), 403

    cats = Category.query.all()
    return jsonify([c.to_dict() for c in cats]), 200

@admin_api.route('/categories', methods=['POST'])
@jwt_required()
def create_category():
    uid = get_jwt_identity()
    if not is_admin(uid):
        return jsonify({'error': 'Unauthorized access'}), 403

    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    slug = (data.get('slug') or '').strip()
    description = data.get('description', '').strip()

    if not name or not slug:
        return jsonify({'error': 'Name and slug are required'}), 400
    if Category.query.filter((Category.name == name) | (Category.slug == slug)).first():
        return jsonify({'error': 'Category with this name or slug already exists'}), 409

    c = Category(name=name, slug=slug, description=description)
    db.session.add(c)
    db.session.commit()
    return jsonify({'message': 'Category created', 'category': c.to_dict()}), 201
