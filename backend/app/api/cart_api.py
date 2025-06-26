from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extension import db
from app.models.cart import CartItem
from app.models.product import Product

# Создаём blueprint с единым префиксом и единообразными путями
cart_api = Blueprint('cart_api', __name__)  


# Допустимые размеры
ALLOWED_SIZES = {'s', 'm', 'l', 'xl'}

@cart_api.route('/', methods=['GET'])
@jwt_required()
def get_cart():
    """
    Получить все позиции корзины текущего пользователя и общую сумму.
    """
    user_id = get_jwt_identity()
    current_app.logger.debug(f"[get_cart] user_id={user_id}")

    items = CartItem.query.filter_by(user_id=user_id).all()
    total = sum(item.line_total for item in items)

    return jsonify({
        'items': [item.to_dict() for item in items],
        'total': str(total)
    }), 200

@cart_api.route('/', methods=['POST'])
@jwt_required()
def add_to_cart():
    """
    Добавить товар в корзину или увеличить количество, если уже есть.
    Ожидает JSON: { product_id: int, quantity?: int, size: str }
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    size = (data.get('size') or '').lower()

    current_app.logger.debug(
        f"[add_to_cart] user_id={user_id}, product_id={product_id}, quantity={quantity}, size={size}"
    )

    # Проверка входных данных
    if not product_id or not isinstance(quantity, int) or quantity < 1:
        return jsonify({'error': 'Invalid product_id or quantity'}), 400
    if size not in ALLOWED_SIZES:
        return jsonify({'error': f"Invalid size, must be one of {', '.join(ALLOWED_SIZES)}"}), 400

    # Проверка существования продукта
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    # Поиск существующей позиции
    item = CartItem.query.filter_by(
        user_id=user_id,
        product_id=product_id,
        size=size
    ).first()

    if item:
        item.quantity += quantity
    else:
        item = CartItem(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            size=size
        )
        db.session.add(item)

    db.session.commit()
    return jsonify({'message': 'Товар добавлен в корзину', 'item': item.to_dict()}), 201

@cart_api.route('/', methods=['PUT'])
@jwt_required()
def update_cart_item():
    """
    Обновить количество или удалить позицию, если quantity=0.
    Ожидает JSON: { product_id: int, quantity: int, size: str }
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    size = (data.get('size') or '').lower()

    current_app.logger.debug(
        f"[update_cart_item] user_id={user_id}, product_id={product_id}, quantity={quantity}, size={size}"
    )

    if not product_id or not isinstance(quantity, int) or quantity < 0:
        return jsonify({'error': 'Invalid product_id or quantity'}), 400
    if size not in ALLOWED_SIZES:
        return jsonify({'error': 'Invalid size'}), 400

    item = CartItem.query.filter_by(
        user_id=user_id,
        product_id=product_id,
        size=size
    ).first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404

    if quantity == 0:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': 'Товар удалён из корзины'}), 200

    item.quantity = quantity
    db.session.commit()
    return jsonify({'message': 'Количество обновлено', 'item': item.to_dict()}), 200

@cart_api.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def remove_cart_item(product_id):
    """
    Удалить конкретный товар из корзины по product_id.
    """
    user_id = get_jwt_identity()
    current_app.logger.debug(f"[remove_cart_item] user_id={user_id}, product_id={product_id}")

    item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Товар удалён из корзины'}), 200

@cart_api.route('/clear', methods=['DELETE'])
@jwt_required()
def clear_cart():
    """
    Очистить всю корзину пользователя.
    """
    user_id = get_jwt_identity()
    current_app.logger.debug(f"[clear_cart] user_id={user_id}")

    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    return jsonify({'message': 'Корзина очищена'}), 200
