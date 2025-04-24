
from . import db
import uuid
from datetime import datetime

def generate_uuid():
    return str(uuid.uuid4())

class Merchant(db.Model):
    __tablename__ = merchants

    merchant_id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    email = db.Column(db.String(255), unique=True, nullable=False)
    business_name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default=pending)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bank_accounts = db.relationship(BankAccount, backref=merchant, lazy=True)

class BankAccount(db.Model):
    __tablename__ = bank_accounts

    bank_account_id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    account_number = db.Column(db.String(255), nullable=False)
    routing_number = db.Column(db.String(255), nullable=False)
    merchant_id = db.Column(db.String(36), db.ForeignKey(merchants.merchant_id), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

class Transaction(db.Model):
    __tablename__ = transactions

    transaction_id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    merchant_id = db.Column(db.String(36), db.ForeignKey(merchants.merchant_id), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default=pending)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    refunded_at = db.Column(db.DateTime, nullable=True)

