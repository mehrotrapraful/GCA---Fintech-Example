
from flask import Blueprint, request, jsonify
from ..services.payment_service import PaymentService

payment_bp = Blueprint(payment, __name__)
payment_service = PaymentService()

@payment_bp.route(, methods=[POST])
def create_payment():
    data = request.get_json()
    try:
        transaction = payment_service.create_payment(data)
        return jsonify(transaction), 201
    except ValueError as e:
        return jsonify({error: str(e)}), 400
    except Exception as e:
        return jsonify({error: str(e)}), 404

@payment_bp.route(/
