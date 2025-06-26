# backend/app/api/category_api.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extension import db
from app.models import Category, User

category_api = Blueprint("category_api", __name__)

@category_api.route("/", methods=["GET"])
def get_categories():
    """Получить список всех категорий."""
    categories = Category.query.order_by(Category.name).all()
    return jsonify([cat.to_dict() for cat in categories]), 200

@category_api.route("/", methods=["POST"])
@jwt_required()
def create_category():
    """Создать новую категорию (только для админов)."""
    user = User.query.get(get_jwt_identity())
    if not user or not user.is_admin:
        return jsonify({"error": "Access denied"}), 403

    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    slug = (data.get("slug") or "").strip()
    description = data.get("description", "").strip()

    if not name or not slug:
        return jsonify({"error": "Both name and slug are required"}), 400

    if Category.query.filter((Category.name == name) | (Category.slug == slug)).first():
        return jsonify({"error": "Category with this name or slug already exists"}), 409

    category = Category(name=name, slug=slug, description=description)
    db.session.add(category)
    db.session.commit()
    return jsonify({"message": "Category created", "category": category.to_dict()}), 201

@category_api.route("/<int:category_id>", methods=["PUT"])
@jwt_required()
def update_category(category_id):
    """Обновить категорию (только для админов)."""
    user = User.query.get(get_jwt_identity())
    if not user or not user.is_admin:
        return jsonify({"error": "Access denied"}), 403

    category = Category.query.get_or_404(category_id)
    data = request.get_json() or {}
    new_name = (data.get("name") or category.name).strip()
    new_slug = (data.get("slug") or category.slug).strip()
    new_description = data.get("description", category.description).strip()

    # Проверяем уникальность name и slug
    conflict = Category.query.filter(
        ((Category.name == new_name) | (Category.slug == new_slug)) &
        (Category.id != category.id)
    ).first()
    if conflict:
        return jsonify({"error": "Another category with this name or slug exists"}), 409

    category.name = new_name
    category.slug = new_slug
    category.description = new_description
    db.session.commit()
    return jsonify({"message": "Category updated", "category": category.to_dict()}), 200

@category_api.route("/<int:category_id>", methods=["DELETE"])
@jwt_required()
def delete_category(category_id):
    """Удалить категорию (только для админов)."""
    user = User.query.get(get_jwt_identity())
    if not user or not user.is_admin:
        return jsonify({"error": "Access denied"}), 403

    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return jsonify({"message": "Category deleted"}), 204
