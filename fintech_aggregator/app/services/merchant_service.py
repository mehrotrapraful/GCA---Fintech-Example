from .. import db
from ..models import Merchant, BankAccount
from werkzeug.exceptions import NotFound, BadRequest

class MerchantService:
    def create_merchant(self, data):
        if not data or 'email' not in data or 'business_name' not in data:
            raise BadRequest('Missing required fields')

        merchant = Merchant(email=data['email'], business_name=data['business_name'])
        db.session.add(merchant)
        db.session.commit()
        return {'merchant_id': merchant.merchant_id, 'status': merchant.status}

    def add_bank_account(self, merchant_id, data):
        merchant = Merchant.query.get(merchant_id)
        if not merchant:
            raise NotFound('Merchant not found')

        if not data or 'account_number' not in data or 'routing_number' not in data:
            raise BadRequest('Missing required fields')

        bank_account = BankAccount(account_number=data['account_number'], routing_number=data['routing_number'], merchant_id=merchant_id)
        db.session.add(bank_account)
        db.session.commit()
        return {'bank_account_id': bank_account.bank_account_id}

    def get_merchant(self, merchant_id):
        merchant = Merchant.query.get(merchant_id)
        if not merchant:
            raise NotFound('Merchant not found')
        return {
            'merchant_id': merchant.merchant_id,
            'email': merchant.email,
            'business_name': merchant.business_name,
            'status': merchant.status,
            'created_at': merchant.created_at.isoformat(),
            'bank_accounts': [{'bank_account_id': ba.bank_account_id, 'account_number': ba.account_number, 'routing_number': ba.routing_number} for ba in merchant.bank_accounts]
        }
    
    def delete_merchant(self, merchant_id):
        merchant = Merchant.query.get(merchant_id)
        if not merchant:
            raise NotFound('Merchant not found')
        
        db.session.delete(merchant)
        db.session.commit()
