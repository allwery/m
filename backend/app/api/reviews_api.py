# backend/app/api/reviews_api.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extension import db
from app.models import Review, Product, Order, OrderItem, User, OrderStatus

reviews_api = Blueprint('reviews_api', __name__)

def validate_review_params(data):
    errors = []
    # Проверяем рейтинг
    try:
        rating = int(data.get('rating', 0))
        if rating < 1 or rating > 5:
            errors.append('Оценка должна быть между 1 и 5')
    except (TypeError, ValueError):
        errors.append('Rating must be an integer')

    # Проверяем длину комментария
    comment = data.get('comment', '')
    if comment and len(comment) > 1000:
        errors.append('Отзыв не должен привышать 1000 символов')

    # Проверяем наличие товара
    product_id = data.get('product_id')
    if not product_id or not Product.query.get(product_id):
        errors.append('Invalid or missing product_id')

    return errors

@reviews_api.route('/', methods=['GET'])
def get_reviews():
    """Получение отзывов по товару."""
    product_id = request.args.get('product_id', type=int)
    if not product_id:
        return jsonify({'errors': ['product_id is required']}), 400
    if not Product.query.get(product_id):
        return jsonify({'errors': ['Invalid product_id']}), 400

    reviews = (
        Review.query
        .filter_by(product_id=product_id)
        .order_by(Review.created_at.desc())
        .all()
    )

    # Собираем отзывы вместе с никнеймами пользователей
    result = []
    for r in reviews:
        result.append({
            **r.to_dict(),
            'username': r.user.username  # добавляем никнейм автора
        })

    return jsonify(result), 200

@reviews_api.route('/', methods=['POST'])
@jwt_required()
def create_review():
    """Добавление отзыва пользователем."""
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    errors = validate_review_params(data)
    if errors:
        return jsonify({'errors': errors}), 400

    product_id = data['product_id']

    # Проверка, что пользователь ещё не оставлял отзыв на этот товар
    if Review.query.filter_by(user_id=user_id, product_id=product_id).first():
        return jsonify({'errors': ['Отзыв уже существует']}), 409

    # Проверка, что пользователь получил товар (статус COMPLETED)
    purchased = (
        db.session.query(OrderItem)
        .join(Order)
        .filter(
            Order.user_id == user_id,
            Order.status == OrderStatus.COMPLETED,
            OrderItem.product_id == product_id
        )
        .first()
    )
    if not purchased:
        return jsonify({'errors': ['Вы можете оставить отзыв только на приобретенный товар']}), 403

    review = Review(
        rating=int(data['rating']),
        comment=data.get('comment'),
        user_id=user_id,
        product_id=product_id
    )
    db.session.add(review)
    db.session.commit()

    return jsonify(review.to_dict()), 201

@reviews_api.route('/<int:review_id>', methods=['PUT'])
@jwt_required()
def update_review(review_id):
    """Редактирование своего отзыва или админом."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    review = Review.query.get_or_404(review_id)

    if review.user_id != user_id and not user.is_admin:
        return jsonify({'errors': ['Unauthorized']}), 403

    data = request.get_json() or {}
    errors = validate_review_params(data)
    if errors:
        return jsonify({'errors': errors}), 400

    # Нельзя менять товар в отзыве
    if data.get('product_id') and data['product_id'] != review.product_id:
        return jsonify({'errors': ['Cannot change product_id']}), 400

    review.rating = int(data['rating'])
    review.comment = data.get('comment')
    db.session.commit()

    return jsonify(review.to_dict()), 200

@reviews_api.route('/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    """Удаление своего отзыва или админом."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    review = Review.query.get_or_404(review_id)

    if review.user_id != user_id and not user.is_admin:
        return jsonify({'errors': ['Unauthorized']}), 403

    db.session.delete(review)
    db.session.commit()
    return '', 204

@reviews_api.route('/admin', methods=['GET'])
@jwt_required()
def get_all_reviews():
    """Получение всех отзывов (только админ)."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    if not user.is_admin:
        return jsonify({'errors': ['Admin access required']}), 403

    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return jsonify([r.to_dict() for r in reviews]), 200

@reviews_api.route('/admin/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_any_review(review_id):
    """Удаление любого отзыва (только админ)."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    if not user.is_admin:
        return jsonify({'errors': ['Admin access required']}), 403

    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    return '', 204
