# backend/app/api/user_api.py

import re
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extension import db
from app.models import User, Order, UserAddress, UserCard

user_api = Blueprint('user_api', __name__)

def validate_profile_data(data):
    errors = []
    username = data.get('username')
    if username is not None and len(username.strip()) < 1:
        errors.append('Это поле не может быть пустым')
    return errors

def validate_password_data(data):
    errors = []
    if not data.get('current_password'):
        errors.append('Current password is required')
    new_pw = data.get('new_password')
    if not new_pw:
        errors.append('New password is required')
    elif len(new_pw) < 8:
        errors.append('New password must be at least 8 characters')
    return errors

def validate_address_data(data):
    errors = []
    street = data.get('street', '').strip()
    city = data.get('city', '').strip()
    postal = data.get('postal_code', '').strip()
    country = data.get('country', '').strip()
    if not all([street, city, postal, country]):
        errors.append('All address fields (street, city, postal_code, country) are required')
    return errors

def validate_card_data(data):
    errors = []
    card_number = data.get('card_number', '')
    expiry = data.get('expiry', '')
    if not re.fullmatch(r'(\d\s?){16}', card_number):
        errors.append('Invalid card number format')
    if not re.fullmatch(r'\d{2}/\d{4}', expiry):
        errors.append('Invalid expiry date format (MM/YYYY)')
    return errors

@user_api.route('/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200

@user_api.route('/profile', methods=['PUT'])
@jwt_required()
def update_user_profile():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}

    errors = validate_profile_data(data)
    if errors:
        return jsonify({'errors': errors}), 422

    username = data.get('username', '').strip()
    user.username = username
    db.session.commit()

    return jsonify({'message': 'Profile updated successfully', 'user': user.to_dict()}), 200

@user_api.route('/password', methods=['PUT'])
@jwt_required()
def change_password():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}
    errors = validate_password_data(data)
    if errors:
        return jsonify({'errors': errors}), 400

    if not user.check_password(data['current_password']):
        return jsonify({'error': 'Current password is incorrect'}), 400

    user.password = data['new_password']
    db.session.commit()
    return jsonify({'message': 'Password updated successfully'}), 200

@user_api.route('/orders', methods=['GET'])
@jwt_required()
def get_user_orders():
    user_id = get_jwt_identity()
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    return jsonify([order.to_dict() for order in orders]), 200

@user_api.route('/addresses', methods=['GET'])
@jwt_required()
def get_addresses():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    return jsonify([addr.to_dict() for addr in user.addresses]), 200

@user_api.route('/addresses', methods=['POST'])
@jwt_required()
def add_address():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    errors = validate_address_data(data)
    if errors:
        return jsonify({'errors': errors}), 400

    addr = UserAddress(
        user_id=user_id,
        street=data['street'].strip(),
        city=data['city'].strip(),
        postal_code=data['postal_code'].strip(),
        country=data['country'].strip()
    )
    db.session.add(addr)
    db.session.commit()
    return jsonify({'message': 'Address added', 'address': addr.to_dict()}), 201

@user_api.route('/addresses/<int:address_id>', methods=['PUT'])
@jwt_required()
def update_address(address_id):
    user_id = get_jwt_identity()
    addr = UserAddress.query.filter_by(id=address_id, user_id=user_id).first_or_404()
    data = request.get_json() or {}
    errors = validate_address_data(data)
    if errors:
        return jsonify({'errors': errors}), 400

    addr.street      = data['street'].strip()
    addr.city        = data['city'].strip()
    addr.postal_code = data['postal_code'].strip()
    addr.country     = data['country'].strip()
    db.session.commit()
    return jsonify({'message': 'Address updated', 'address': addr.to_dict()}), 200

@user_api.route('/addresses/<int:address_id>', methods=['DELETE'])
@jwt_required()
def delete_address(address_id):
    user_id = get_jwt_identity()
    addr = UserAddress.query.filter_by(id=address_id, user_id=user_id).first()
    if not addr:
        return jsonify({'error': 'Address not found'}), 404

    db.session.delete(addr)
    db.session.commit()
    return '', 204

@user_api.route('/cards', methods=['GET'])
@jwt_required()
def get_cards():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    return jsonify([card.to_dict() for card in user.cards]), 200

@user_api.route('/cards', methods=['POST'])
@jwt_required()
def add_card():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    errors = validate_card_data(data)
    if errors:
        return jsonify({'errors': errors}), 400

    card = UserCard(
        user_id=user_id,
        card_number=re.sub(r'\s+', '', data['card_number']),
        expiry=data['expiry']
    )
    db.session.add(card)
    db.session.commit()
    return jsonify({'message': 'Card added', 'card': card.to_dict()}), 201

@user_api.route('/cards/<int:card_id>', methods=['DELETE'])
@jwt_required()
def delete_card(card_id):
    user_id = get_jwt_identity()
    card = UserCard.query.filter_by(id=card_id, user_id=user_id).first()
    if not card:
        return jsonify({'error': 'Card not found'}), 404

    db.session.delete(card)
    db.session.commit()
    return '', 204

@user_api.route('/', methods=['DELETE'])
@jwt_required()
def delete_account():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return '', 204
