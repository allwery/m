from app.extension import db
from sqlalchemy.sql import func

class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    # Если пользователь авторизован — привязываем к нему, иначе используем session_id
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=True,
        index=True
    )
    session_id = db.Column(
        db.String(64),
        nullable=True,
        index=True,
        doc="Идентификатор гостевой сессии для неавторизованных пользователей"
    )

    # Товар и количество
    product_id = db.Column(
        db.Integer,
        db.ForeignKey('products.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    quantity = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )
    size = db.Column(db.String(20), nullable=False)

    # Когда товар был добавлен в корзину
    added_at = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Связи
    user = db.relationship(
        'User',
        backref=db.backref('cart_items', cascade='all, delete-orphan')
    )
    product = db.relationship(
        'Product',
        lazy='joined'
    )

    def to_dict(self):
        """Вернуть структуру для JSON-ответа."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'product': {
                'id': self.product.id,
                'name': self.product.name,
                'price': str(self.product.price),
                'image': next((img.url() for img in self.product.images if img.is_primary), None)
            },
            'quantity': self.quantity,
            'size':     self.size,
            'added_at': self.added_at.isoformat()
        }

    @property
    def line_total(self):
        """Общая стоимость этой позиции (price × quantity)."""
        return self.product.price * self.quantity