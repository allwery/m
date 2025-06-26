# app/models/user.py

import string
import random

from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

from app.extension import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token


def generate_referral_code(length=8):
    """Сгенерировать случайный реферальный код."""
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(random.choice(alphabet) for _ in range(length))


@event.listens_for(db.session, "before_flush")
def ensure_unique_referral_code(session, flush_context, instances):
    """
    Перед сохранением проверяем и при необходимости генерируем новый
    уникальный referral_code для новых User-объектов.
    """
    for obj in session.new:
        if isinstance(obj, User):
            # Если код не задан или уже встречается в БД, генерируем заново
            while True:
                code = generate_referral_code()
                exists = (
                    db.session.query(User.id)
                    .filter_by(referral_code=code)
                    .first()
                )
                if not exists:
                    obj.referral_code = code
                    break


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    _password = db.Column("password", db.Text, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    # Реферальный код и баланс баллов
    referral_code = db.Column(
        db.String(20),
        unique=True,
        nullable=False,
        index=True,
        default=generate_referral_code
    )
    points_balance = db.Column(db.Integer, default=0, nullable=False)

    # Связи
    orders = db.relationship(
        "Order",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="Order.user_id"
    )
    reviews = db.relationship(
        "Review",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    addresses = db.relationship(
        "UserAddress",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    cards = db.relationship(
        "UserCard",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    @property
    def password(self):
        raise AttributeError("Password is write-only")

    @password.setter
    def password(self, plain):
        self._password = generate_password_hash(plain)

    def check_password(self, plain):
        return check_password_hash(self._password, plain)

    def create_token(self):
        return create_access_token(identity=self.id)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "is_admin": self.is_admin,
            "referral_code": self.referral_code,
            "points_balance": self.points_balance,
        }


class UserAddress(db.Model):
    __tablename__ = "user_addresses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    street = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), nullable=False)

    user = db.relationship("User", back_populates="addresses")

    def to_dict(self):
        return {
            "id": self.id,
            "street": self.street,
            "city": self.city,
            "postal_code": self.postal_code,
            "country": self.country,
        }


class UserCard(db.Model):
    __tablename__ = "user_cards"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    card_number = db.Column(db.String(19), nullable=False)  # «XXXX XXXX XXXX XXXX»
    expiry = db.Column(db.String(7), nullable=False)        # «MM/YYYY»

    user = db.relationship("User", back_populates="cards")

    def masked_number(self):
        return "•••• •••• •••• " + self.card_number[-4:]

    def to_dict(self):
        return {
            "id": self.id,
            "card_number": self.masked_number(),
            "expiry": self.expiry,
        }
