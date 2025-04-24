from flask import Blueprint, request, jsonify
from ..services.merchant_service import MerchantService
from werkzeug.exceptions import NotFound, BadRequest

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
    except BadRequest as e:
        return jsonify({'error': str(e)}), 400


@merchant_bp.route('/<merchant_id>/bank_accounts', methods=['POST'])
def add_bank_account(merchant_id):
    data = request.get_json()
    try:
        bank_account = merchant_service.add_bank_account(merchant_id, data)
        return jsonify(bank_account), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except NotFound as e:
        return jsonify({'error': str(e)}), 404


@merchant_bp.route('/<merchant_id>', methods=['GET'])
def get_merchant(merchant_id):
    try:
        merchant = merchant_service.get_merchant(merchant_id)
        return jsonify(merchant), 200
    except NotFound as e:
        return jsonify({'error': str(e)}), 404

@merchant_bp.route('/<int:merchant_id>', methods=['DELETE'])
def delete_merchant(merchant_id):
    try:
        merchant_service.delete_merchant(merchant_id)
        return jsonify({'message': 'Merchant deleted successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except NotFound as e:
        return jsonify({'error': str(e)}), 404
