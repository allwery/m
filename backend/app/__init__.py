# app/__init__.py

import os
from flask import Flask, send_from_directory
from .config    import Config
from .extension import db, migrate, jwt, cors, mail

def create_app():
    # создаём Flask-приложение, указываем папку со сборкой фронтенда
    app = Flask(
        __name__,
        static_folder=os.path.join(os.pardir, 'frontend', 'dist'),
        static_url_path='/static'
    )
    app.config.from_object(Config)

    # инициализация расширений
    cors.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)

    # регистрация API-блюпринтов
    from app.api.auth_api     import auth_api
    from app.api.category_api import category_api
    from app.api.product_api  import product_api
    from app.api.cart_api     import cart_api
    from app.api.order_api    import order_api
    from app.api.reviews_api  import reviews_api
    from app.api.user_api     import user_api
    from app.api.admin_api    import admin_api

    app.register_blueprint(auth_api,     url_prefix='/api/auth')
    app.register_blueprint(category_api, url_prefix='/api/categories')
    app.register_blueprint(product_api,  url_prefix='/api/products')
    app.register_blueprint(cart_api,     url_prefix='/api/cart')
    app.register_blueprint(order_api,    url_prefix='/api/orders')
    app.register_blueprint(reviews_api,  url_prefix='/api/reviews')
    app.register_blueprint(user_api,     url_prefix='/api/user')
    app.register_blueprint(admin_api,    url_prefix='/api/admin')

    # отдаём фронтенд (SPA)
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        full_path = os.path.join(app.static_folder, path)
        if path and os.path.exists(full_path):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, 'index.html')

    # отдаём медиа-файлы
    @app.route(f"{app.config['MEDIA_URL']}/<path:filename>")
    def serve_media(filename):
        media_root = os.path.join(app.root_path, app.config['MEDIA_ROOT'])
        return send_from_directory(media_root, filename)

    @app.route('/media/products/<path:filename>')
    def serve_product_images(filename):
        media_dir = os.path.abspath(
            os.path.join(app.root_path, os.pardir, 'media', 'img', 'products')
        )
        return send_from_directory(media_dir, filename)

    return app
