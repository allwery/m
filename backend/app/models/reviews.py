from app.extension import db
from datetime import datetime
from sqlalchemy import CheckConstraint

class Review(db.Model):
    """Модель отзыва на товар"""
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)  # Оценка товара от 1 до 5
    comment = db.Column(db.Text, nullable=True)     # Текст отзыва
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    product_id = db.Column(
        db.Integer,
        db.ForeignKey('products.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Ограничиваем рейтинг диапазоном 1–5
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='rating_range'),
    )

    # Двусторонние связи
    user = db.relationship(
        'User',
        back_populates='reviews'
    )
    product = db.relationship(
        'Product',
        back_populates='reviews'
    )

    def __repr__(self):
        return f'<Review {self.rating} for Product ID {self.product_id}>'

    def to_dict(self):
        return {
            "id": self.id,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.isoformat(),
            "user_id": self.user_id,
            "product_id": self.product_id
        }