import os
from dotenv import load_dotenv

# подгрузим .env (локально)
load_dotenv()

class Config:
    # === Flask ===
    SECRET_KEY = os.getenv(
        'SECRET_KEY',
        'f4a1c3e87b2d5f0c6a9e8d1234567890abcdef1234567890abcdef1234567890'
    )

    # === SQLAlchemy / Postgres ===
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://vadimb:7wBsVahU7rvQk7v8aWSlixeJsj4rworW@dpg-d1egsvje5dus73bdok6g-a/moroznik_store' 
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # === Почта ===
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'your-email@gmail.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'your-app-specific-password')
    MAIL_DEFAULT_SENDER = os.getenv(
        'MAIL_DEFAULT_SENDER',
        MAIL_USERNAME or 'no-reply@your-domain.com'
    )

    # === JWT ===
    JWT_SECRET_KEY = os.getenv(
        'JWT_SECRET_KEY',
        'f4a1c3e87b2t5f0c6a9e8d3219967890abcdef1234567890bagtlq2178537790'
    )

    # === CORS ===
    # при необходимости ограничьте домены через ENV
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

    # === Пути для медиа-файлов / загрузок ===
    MEDIA_ROOT = os.getenv('MEDIA_ROOT', os.path.join(os.pardir, 'media'))
    MEDIA_URL  = os.getenv('MEDIA_URL', '/media')
    UPLOAD_FOLDER = os.getenv(
        'UPLOAD_FOLDER',
        os.path.join(MEDIA_ROOT, 'products')
    )

    # === Прочее ===
    DEBUG = os.getenv('FLASK_ENV') == 'development'
