from app.extension import db
from datetime import datetime
from sqlalchemy.sql import func

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    # Описание товара, содержит материал, цвет и т.п.
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0, nullable=False)
    popularity = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Категория
    category_id = db.Column(
        db.Integer,
        db.ForeignKey('categories.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    category = db.relationship('Category', back_populates='products')

    # Изображения товаров
    images = db.relationship(
        'ProductImage',
        back_populates='product',
        cascade='all, delete-orphan'
    )

    # Отзывы
    reviews = db.relationship(
        'Review',
        back_populates='product',
        cascade='all, delete-orphan'
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': str(self.price),
            'stock': self.stock,
            'popularity': self.popularity,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'category': self.category.to_dict() if self.category else None,
            'images': [img.to_dict() for img in self.images],
            'average_rating': (
                round(sum(r.rating for r in self.reviews) / len(self.reviews), 2)
                if self.reviews else None
            ),
            'reviews_count': len(self.reviews)
        }

class ProductImage(db.Model):
    __tablename__ = 'product_images'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer,
        db.ForeignKey('products.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    filename = db.Column(db.String(255), nullable=False)
    is_primary = db.Column(db.Boolean, default=False, nullable=False)

    product = db.relationship('Product', back_populates='images')

    def url(self):
        return f"/media/products/{self.filename}"

    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url(),
            'is_primary': self.is_primary
        }
