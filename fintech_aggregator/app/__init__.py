
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config_by_name

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    db.init_app(app)
    migrate.init_app(app, db)

    from .routes.merchant_routes import merchant_bp
    from .routes.payment_routes import payment_bp

    app.register_blueprint(merchant_bp, url_prefix=/merchants)
    app.register_blueprint(payment_bp, url_prefix=/payments)

    return app

