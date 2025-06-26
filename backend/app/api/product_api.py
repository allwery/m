# backend/app/api/product_api.py

import os
import uuid
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from app.extension import db
from app.models import Product, ProductImage, Category, User

product_api = Blueprint('product_api', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )

@product_api.route('/', methods=['GET'])
def get_products():
    """Список товаров с фильтрацией, сортировкой по цене и пагинацией."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    category_id = request.args.get('category_id', type=int)
    search = request.args.get('search', type=str)
    sort = request.args.get('sort', type=str)  # 'asc' | 'desc'

    query = Product.query

    # Фильтрация по категории
    if category_id:
        query = query.filter_by(category_id=category_id)
    # Поиск по названию
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))

    # Сортировка
    if sort == 'asc':
        order_clause = Product.price.asc()
    elif sort == 'desc':
        order_clause = Product.price.desc()
    else:
        order_clause = Product.popularity.desc()

    pagination = query.order_by(order_clause).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'products':     [p.to_dict() for p in pagination.items],
        'total':        pagination.total,
        'pages':        pagination.pages,
        'current_page': pagination.page
    }), 200

@product_api.route('/new', methods=['GET'])
def get_new_products():
    """
    Список новейших товаров (новинки).
    Можно передать ?limit=5 для ограничения количества (по умолчанию 10).
    """
    limit = request.args.get('limit', 10, type=int)
    products = (
        Product.query
        .order_by(Product.created_at.desc())
        .limit(limit)
        .all()
    )
    return jsonify([p.to_dict() for p in products]), 200

@product_api.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Детали одного товара."""
    p = Product.query.get_or_404(product_id)
    return jsonify(p.to_dict()), 200

@product_api.route('/<int:product_id>/images', methods=['GET'])
def list_product_images(product_id):
    """
    Возвращает список URL-ов всех картинок из папки
    media/img/products/product{product_id}/
    """
    # Путь к каталогу с фотографиями относительно MEDIA_ROOT
    rel_folder = os.path.join('img', 'products', f'product{product_id}')
    media_root = os.path.join(current_app.root_path, current_app.config['MEDIA_ROOT'])
    abs_folder = os.path.join(media_root, rel_folder)

    urls = []
    if os.path.isdir(abs_folder):
        for fname in sorted(os.listdir(abs_folder)):
            if not allowed_file(fname):
                continue
            urls.append(f"{current_app.config['MEDIA_URL']}/{rel_folder}/{fname}")

    return jsonify({'images': urls}), 200

@product_api.route('/', methods=['POST'])
@jwt_required()
def create_product():
    """Создать товар (только админ)."""
    user = User.query.get(get_jwt_identity())
    if not user or not user.is_admin:
        return jsonify({'error': 'Access denied'}), 403

    data = request.get_json() or {}
    name = data.get('name', '').strip()
    price = data.get('price')
    category_id = data.get('category_id')

    if not name or price is None or category_id is None:
        return jsonify({'error': 'Missing required fields'}), 400
    if not Category.query.get(category_id):
        return jsonify({'error': 'Invalid category'}), 400

    product = Product(
        name=name,
        description=data.get('description', '').strip(),
        price=price,
        stock=data.get('stock', 0),
        popularity=data.get('popularity', 0),
        category_id=category_id
    )
    db.session.add(product)
    db.session.commit()

    return jsonify({'message': 'Product created', 'product': product.to_dict()}), 201

@product_api.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """Обновить товар (только админ)."""
    user = User.query.get(get_jwt_identity())
    if not user or not user.is_admin:
        return jsonify({'error': 'Access denied'}), 403

    product = Product.query.get_or_404(product_id)
    data = request.get_json() or {}

    # Обновление полей
    if 'category_id' in data:
        if not Category.query.get(data['category_id']):
            return jsonify({'error': 'Invalid category'}), 400
        product.category_id = data['category_id']

    for field in ('name', 'description', 'price', 'stock', 'popularity'):
        if field in data:
            setattr(product, field, data[field])

    db.session.commit()
    return jsonify({'message': 'Product updated', 'product': product.to_dict()}), 200

@product_api.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """Удалить товар (только админ)."""
    user = User.query.get(get_jwt_identity())
    if not user or not user.is_admin:
        return jsonify({'error': 'Access denied'}), 403

    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return '', 204

@product_api.route('/<int:product_id>/upload-image', methods=['POST'])
@jwt_required()
def upload_image(product_id):
    """Загрузить изображение для товара (только админ)."""
    user = User.query.get(get_jwt_identity())
    if not user or not user.is_admin:
        return jsonify({'error': 'Access denied'}), 403

    product = Product.query.get_or_404(product_id)
    file = request.files.get('image')
    if not file or file.filename == '':
        return jsonify({'error': 'No file provided'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    # Сохраняем файл
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    upload_dir = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, secure_filename(filename))
    file.save(filepath)

    # Если это первая картинка — делаем её primary в БД
    is_primary = (len(product.images) == 0)
    img = ProductImage(
        product_id=product.id,
        filename=filename,
        is_primary=is_primary
    )
    if is_primary:
        for other in product.images:
            other.is_primary = False

    db.session.add(img)
    db.session.commit()

    # Возвращаем полный URL новой картинки
    img_data = img.to_dict()
    img_data['url'] = f"{current_app.config['MEDIA_URL']}/products/{filename}"
    return jsonify({'message': 'Image uploaded', 'image': img_data}), 200
