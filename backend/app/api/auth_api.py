# backend/app/api/auth_api.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from app.extension import db
from app.models import User

auth_api = Blueprint('auth_api', __name__)

@auth_api.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Укажите почту и пароль'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Почта уже используется'}), 409

    user = User(email=email)
    user.password = password
    db.session.add(user)
    db.session.commit()

    # Передаём строку, а не число — JWT требует, чтобы sub был строкой
    token = create_access_token(identity=str(user.id))
    return jsonify({
        'token': token,
        'user':  user.to_dict()
    }), 201


@auth_api.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Укажите почту и пароль'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Неверная почта или пароль'}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({
        'token': token,
        'user':  user.to_dict()
    }), 200


@auth_api.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(int(user_id))
    return jsonify(user.to_dict()), 200
