import os
from dotenv import load_dotenv

load_dotenv()  # Загружаем .env

class Config:
    # Основные
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-flask-secret-key')

    # База данных
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://user:password@localhost/clothing_store'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Режим разработки
    DEBUG = os.getenv('FLASK_ENV') == 'development'

    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

    # Почта
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv(
        'MAIL_DEFAULT_SENDER',
        MAIL_USERNAME or 'no-reply@artboutique.com'
    )

    # JWT
    JWT_SECRET_KEY = os.getenv(
        'JWT_SECRET_KEY',
        'fallback-jwt-secret-key-should-be-long-and-random'
    )

    # Пути для медиа-файлов
    # Медиа-корень (для отдачи статических файлов через Flask)
    MEDIA_ROOT = os.getenv(
        'MEDIA_ROOT',
        os.path.join(os.pardir, 'media')
    )
    # URL-префикс для доступа к медиа через браузер
    MEDIA_URL = os.getenv('MEDIA_URL', '/media')

    # Папка для загрузки product-image через API
    UPLOAD_FOLDER = os.getenv(
        'UPLOAD_FOLDER',
        os.path.join(MEDIA_ROOT, 'products')
    )

    # Защита форм
    WTF_CSRF_ENABLED = True