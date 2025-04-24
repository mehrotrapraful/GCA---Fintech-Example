#!/bin/bash

# --- Script to generate the Fintech Aggregator project structure ---

# --- Constants ---
PROJECT_NAME="fintech_aggregator"
APP_DIR="app"
ROUTES_DIR="routes"
SERVICES_DIR="services"
UTILS_DIR="utils"
MIGRATIONS_DIR="migrations"
VERSIONS_DIR="versions"

# --- Functions ---

# Create a directory
create_dir() {
  local dir_name="$1"
  echo "Creating directory: $dir_name"
  mkdir -p "$dir_name"
}

# Create a file with content
create_file() {
  local file_name="$1"
  local content="$2"
  echo "Creating file: $file_name"
  echo "$content" > "$file_name"
}

# --- Main Script ---

echo "Starting project creation for: $PROJECT_NAME"

# Create the main project directory
create_dir "$PROJECT_NAME"
cd "$PROJECT_NAME"

# Create the app directory and subdirectories
create_dir "$APP_DIR"
create_dir "$APP_DIR/$ROUTES_DIR"
create_dir "$APP_DIR/$SERVICES_DIR"
create_dir "$APP_DIR/$UTILS_DIR"

# Create the migrations directory and subdirectories
create_dir "$MIGRATIONS_DIR"
create_dir "$MIGRATIONS_DIR/$VERSIONS_DIR"

# Create the config.py file
config_content='''
import os

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key')
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost:5432/fintech_dev')

class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL_TEST', 'postgresql://user:password@localhost:5432/fintech_test')

class ProductionConfig(Config):
    """Production configuration."""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost:5432/fintech_prod')

config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)
'''
create_file "config.py" "$config_content"

# Create the app/__init__.py file
app_init_content='''
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

    app.register_blueprint(merchant_bp, url_prefix='/merchants')
    app.register_blueprint(payment_bp, url_prefix='/payments')

    return app
'''
create_file "$APP_DIR/__init__.py" "$app_init_content"

# Create the app/models.py file
app_models_content='''
from . import db
import uuid
from datetime import datetime

def generate_uuid():
    return str(uuid.uuid4())

class Merchant(db.Model):
    __tablename__ = 'merchants'

    merchant_id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    email = db.Column(db.String(255), unique=True, nullable=False)
    business_name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bank_accounts = db.relationship('BankAccount', backref='merchant', lazy=True)

class BankAccount(db.Model):
    __tablename__ = 'bank_accounts'

    bank_account_id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    account_number = db.Column(db.String(255), nullable=False)
    routing_number = db.Column(db.String(255), nullable=False)
    merchant_id = db.Column(db.String(36), db.ForeignKey('merchants.merchant_id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

class Transaction(db.Model):
    __tablename__ = 'transactions'

    transaction_id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    merchant_id = db.Column(db.String(36), db.ForeignKey('merchants.merchant_id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    refunded_at = db.Column(db.DateTime, nullable=True)
'''
create_file "$APP_DIR/models.py" "$app_models_content"

# Create the app/routes/__init__.py file
create_file "$APP_DIR/$ROUTES_DIR/__init__.py" ""

# Create the app/routes/merchant_routes.py file
app_merchant_routes_content='''
from flask import Blueprint, request, jsonify
from ..services.merchant_service import MerchantService

merchant_bp = Blueprint('merchant', __name__)
merchant_service = MerchantService()

@merchant_bp.route('', methods=['POST'])
def create_merchant():
    data = request.get_json()
    try:
        merchant = merchant_service.create_merchant(data)
        return jsonify(merchant), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@merchant_bp.route('/<merchant_id>/bank_accounts', methods=['POST'])
def add_bank_account(merchant_id):
    data = request.get_json()
    try:
        bank_account = merchant_service.add_bank_account(merchant_id, data)
        return jsonify(bank_account), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@merchant_bp.route('/<merchant_id>', methods=['GET'])
def get_merchant(merchant_id):
    try:
        merchant = merchant_service.get_merchant(merchant_id)
        return jsonify(merchant), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404
'''
create_file "$APP_DIR/$ROUTES_DIR/merchant_routes.py" "$app_merchant_routes_content"

# Create the app/routes/payment_routes.py file
app_payment_routes_content='''
from flask import Blueprint, request, jsonify
from ..services.payment_service import PaymentService

payment_bp = Blueprint('payment', __name__)
payment_service = PaymentService()

@payment_bp.route('', methods=['POST'])
def create_payment():
    data = request.get_json()
    try:
        transaction = payment_service.create_payment(data)
        return jsonify(transaction), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@payment_bp.route('/<transaction_id>/refund', methods=['POST'])
def refund_payment(transaction_id):
    try:
        transaction = payment_service.refund_payment(transaction_id)
        return jsonify(transaction), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@payment_bp.route('/<transaction_id>', methods=['GET'])
def get_payment(transaction_id):
    try:
        transaction = payment_service.get_payment(transaction_id)
        return jsonify(transaction), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404
'''
create_file "$APP_DIR/$ROUTES_DIR/payment_routes.py" "$app_payment_routes_content"

# Create the app/services/__init__.py file
create_file "$APP_DIR/$SERVICES_DIR/__init__.py" ""

# Create the app/services/merchant_service.py file
app_merchant_service_content='''
from .. import db
from ..models import Merchant, BankAccount

class MerchantService:
    def create_merchant(self, data):
        if not data or 'email' not in data or 'business_name' not in data:
            raise ValueError('Missing required fields')

        merchant = Merchant(email=data['email'], business_name=data['business_name'])
        db.session.add(merchant)
        db.session.commit()
        return {'merchant_id': merchant.merchant_id, 'status': merchant.status}

    def add_bank_account(self, merchant_id, data):
        merchant = Merchant.query.get(merchant_id)
        if not merchant:
            raise Exception('Merchant not found')

        if not data or 'account_number' not in data or 'routing_number' not in data:
            raise ValueError('Missing required fields')

        bank_account = BankAccount(account_number=data['account_number'], routing_number=data['routing_number'], merchant_id=merchant_id)
        db.session.add(bank_account)
        db.session.commit()
        return {'bank_account_id': bank_account.bank_account_id}

    def get_merchant(self, merchant_id):
        merchant = Merchant.query.get(merchant_id)
        if not merchant:
            raise Exception('Merchant not found')
        return {
            'merchant_id': merchant.merchant_id,
            'email': merchant.email,
            'business_name': merchant.business_name,
            'status': merchant.status,
            'created_at': merchant.created_at.isoformat(),
            'bank_accounts': [{'bank_account_id': ba.bank_account_id, 'account_number': ba.account_number, 'routing_number': ba.routing_number} for ba in merchant.bank_accounts]
        }
'''
create_file "$APP_DIR/$SERVICES_DIR/merchant_service.py" "$app_merchant_service_content"

# Create the app/services/payment_service.py file
app_payment_service_content='''
from .. import db
from ..models import Transaction, Merchant

class PaymentService:
    def create_payment(self, data):
        if not data or 'merchant_id' not in data or 'amount' not in data or 'payment_method' not in data:
            raise ValueError('Missing required fields')

        merchant = Merchant.query.get(data['merchant_id'])
        if not merchant:
            raise Exception('Merchant not found')

        transaction = Transaction(merchant_id=data['merchant_id'], amount=data['amount'], payment_method=data['payment_method'])
        db.session.add(transaction)
        db.session.commit()
        return {'transaction_id': transaction.transaction_id, 'status': transaction.status}

    def refund_payment(self, transaction_id):
        transaction = Transaction.query.get(transaction_id)
        if not transaction:
            raise Exception('Transaction not found')

        if transaction.status != 'success':
            raise ValueError('Cannot refund a non-successful transaction')

        transaction.status = 'refunded'
        transaction.refunded_at = transaction.created_at.utcnow()
        db.session.commit()
        return {'transaction_id': transaction.transaction_id, 'status': transaction.status}

    def get_payment(self, transaction_id):
        transaction = Transaction.query.get(transaction_id)
        if not transaction:
            raise Exception('Transaction not found')
        return {
            'transaction_id': transaction.transaction_id,
            'merchant_id': transaction.merchant_id,
            'amount': transaction.amount,
            'payment_method': transaction.payment_method,
            'status': transaction.status,
            'created_at': transaction.created_at.isoformat(),
            'refunded_at': transaction.refunded_at.isoformat() if transaction.refunded_at else None
        }
'''
create_file "$APP_DIR/$SERVICES_DIR/payment_service.py" "$app_payment_service_content"

# Create the app/utils/__init__.py file
create_file "$APP_DIR/$UTILS_DIR/__init__.py" ""

# Create the app/utils/database.py file
app_utils_database_content='''
#This file is empty, it is a placeholder for future database utilities.
'''
create_file "$APP_DIR/$UTILS_DIR/database.py" "$app_utils_database_content"

# Create the run.py file
run_content='''
import os
from app import create_app, db

config_name = os.getenv('FLASK_ENV', 'dev')
app = create_app(config_name)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
'''
create_file "run.py" "$run_content"

# Create the requirements.txt file
requirements_content='''
Flask==2.3.2
Flask-SQLAlchemy==3.0.3
Flask-Migrate==4.0.4
psycopg2-binary==2.9.6
python-dotenv==1.0.0
'''
create_file "requirements.txt" "$requirements_content"

echo "Project creation completed for: $PROJECT_NAME"
