# app/models/order.py

from app.extension import db
from sqlalchemy.sql import func
from sqlalchemy import Enum as PgEnum
import enum

class OrderStatus(enum.Enum):
    PENDING   = "Обработка"
    PAID      = "Оплачен"
    SHIPPED   = "Отправлен"
    COMPLETED = "Завершен"
    CANCELED  = "Закрыт"

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    # Реферальный пользователь
    referrer_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )

    status = db.Column(
        PgEnum(OrderStatus, name='order_status', create_type=False),
        default=OrderStatus.PENDING,
        nullable=False
    )
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)

    # Списанные и начисленные баллы
    referrer_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    used_points    = db.Column(db.Integer, default=0, nullable=False)
    earned_points  = db.Column(db.Integer, default=0, nullable=False)

    # Адрес доставки
    shipping_street      = db.Column(db.String(255), nullable=False)
    shipping_city        = db.Column(db.String(100), nullable=False)
    shipping_postal_code = db.Column(db.String(20), nullable=False)
    shipping_country     = db.Column(db.String(100), nullable=False)

    # Доставка
    shipping_method = db.Column(db.String(50), nullable=False)
    shipping_cost   = db.Column(db.Numeric(10, 2), nullable=False)

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

    # Связи
    user     = db.relationship('User', foreign_keys=[user_id], back_populates='orders')
    referrer = db.relationship('User', foreign_keys=[referrer_id])
    items    = db.relationship(
        'OrderItem',
        back_populates='order',
        cascade='all, delete-orphan'
    )

    def to_dict(self):
        return {
            'id':            self.id,
            'user_id':       self.user_id,
            'referrer_id':   self.referrer_id,
            'status':        self.status.value,
            'total_amount':  str(self.total_amount),
            'used_points':   self.used_points,
            'earned_points': self.earned_points,
            'shipping': {
                'street':      self.shipping_street,
                'city':        self.shipping_city,
                'postal_code': self.shipping_postal_code,
                'country':     self.shipping_country
            },
            'shipping_method': self.shipping_method,
            'shipping_cost':   str(self.shipping_cost),
            'items':           [item.to_dict() for item in self.items],
            'created_at':      self.created_at.isoformat(),
            'updated_at':      self.updated_at.isoformat()
        }

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(
        db.Integer,
        db.ForeignKey('orders.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    product_id = db.Column(
        db.Integer,
        db.ForeignKey('products.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    quantity = db.Column(db.Integer, nullable=False)
    price    = db.Column(db.Numeric(10, 2), nullable=False)
    size     = db.Column(db.String(20), nullable=False)

    order   = db.relationship('Order', back_populates='items')
    product = db.relationship('Product')

    def to_dict(self):
        return {
            'id':         self.id,
            'product_id': self.product_id,
            'quantity':   self.quantity,
            'price':      str(self.price),
            'size':       self.size
        }
