# backend/app/api/order_api.py

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

from app.extension import db
from app.models import Order, OrderItem, CartItem, Product, User
import math

order_api = Blueprint('order_api', __name__)

def validate_order_data(data):
    errors = []
    # Проверяем поля доставки
    street = data.get('shipping_street', '').strip()
    city = data.get('shipping_city', '').strip()
    postal = data.get('shipping_postal_code', '').strip()
    country = data.get('shipping_country', '').strip()
    method = data.get('shipping_method', '').strip()
    cost = data.get('shipping_cost', None)

    if not street or not city or not postal or not country:
        errors.append('Shipping address (street, city, postal_code, country) is required')
    if method not in ['pochta', 'cdek']:
        errors.append("shipping_method must be one of: 'pochta', 'cdek'")
    try:
        if cost is None or float(cost) < 0:
            errors.append('shipping_cost must be a non-negative number')
    except (ValueError, TypeError):
        errors.append('shipping_cost must be a valid number')

    # Проверяем use_points
    use_pts = data.get('use_points')
    if use_pts is not None:
        try:
            if int(use_pts) < 0:
                errors.append('Нельзя ввести кол-во баллов меньше 0')
        except (ValueError, TypeError):
            errors.append('Неверный тип данных')

    return errors

@order_api.route('/', methods=['POST'])
@jwt_required()
def create_order():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}

    # 1) Валидация входных данных
    errors = validate_order_data(data)
    if errors:
        return jsonify({'errors': errors}), 400

    # 2) Собираем позиции из корзины
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    if not cart_items:
        return jsonify({'error': 'Корзина пуста'}), 400

    # 3) Создаём объект заказа (поля total_amount ещё не знаем)
    order = Order(
        user_id=user_id,
        shipping_street=data['shipping_street'].strip(),
        shipping_city=data['shipping_city'].strip(),
        shipping_postal_code=data['shipping_postal_code'].strip(),
        shipping_country=data['shipping_country'].strip(),
        shipping_method=data['shipping_method'].strip(),
        shipping_cost=data['shipping_cost']
    )

    # 4) Обрабатываем реферальный код
    ref_code = data.get('referral_code')
    if ref_code:
        ref_user = User.query.filter_by(referral_code=ref_code).first()
        if ref_user and ref_user.id != user_id:
            order.referrer_id = ref_user.id

    # 5) Подсчитываем subtotal (до доставки и баллов)
    subtotal = 0
    for ci in cart_items:
        prod = Product.query.get(ci.product_id)
        if not prod:
            continue
        subtotal += float(prod.price) * ci.quantity

    # 6) Списание баллов
    used = 0
    if data.get('use_points'):
        desired = int(data['use_points'])
        used = min(desired, user.points_balance)
        user.points_balance -= used

    # 7) Начисление рефбонуса
    earned = 0
    if order.referrer_id:
        earned = math.floor(subtotal * 0.1)
        ref_user.points_balance += earned

    # 8) Финальный total_amount
    total = subtotal + float(order.shipping_cost) - used
    order.used_points    = used
    order.earned_points  = earned
    order.total_amount   = total

    # 9) Добавляем сам заказ в сессию
    db.session.add(order)
    # Не делаем flush() здесь!

    # 10) Создаём и привязываем позиции заказа
    for ci in cart_items:
        prod = Product.query.get(ci.product_id)
        if not prod:
            continue
        item = OrderItem(
            order=order,            # назначаем объект, SQLAlchemy подставит order.id
            product_id=ci.product_id,
            quantity=ci.quantity,
            price=prod.price,
            size=ci.size
        )
        db.session.add(item)

    # 11) Очищаем корзину
    CartItem.query.filter_by(user_id=user_id).delete()

    # 12) Сохраняем всё разом
    db.session.commit()

    return jsonify({
        'message': 'Заказ успешно создан',
        'order': order.to_dict()
    }), 201

@order_api.route('/', methods=['GET'])
@jwt_required()
def get_orders():
    user_id = get_jwt_identity()
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    return jsonify([o.to_dict() for o in orders]), 200

@order_api.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    user_id = get_jwt_identity()
    order = Order.query.filter_by(id=order_id, user_id=user_id).first_or_404()
    return jsonify(order.to_dict()), 200
