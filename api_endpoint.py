import uuid
import datetime
import json
from typing import Dict, Optional
from google.cloud.functions import HttpRequest
from google.cloud.functions import HttpResponse
from jsonschema import validate, ValidationError

# In a real application, you would use a database to store and retrieve payment data.
# Here, we'll use a simple in-memory dictionary for demonstration purposes.
payments_db: Dict[str, Dict] = {}


def create_payment(request: HttpRequest) -> HttpResponse:
    """
    Creates a payment request.

    Args:
        request: The HTTP request object.

    Returns:
        The HTTP response object.
    """
    if request.method != 'POST':
        return HttpResponse(
            json.dumps({"error": "Method Not Allowed", "code": "METHOD_NOT_ALLOWED"}),
            status_code=405,
            headers={"Content-Type": "application/json"}
        )

    try:
        request_json = request.get_json(silent=True)
        if not request_json:
            return HttpResponse(
                json.dumps({"error": "Bad Request", "code": "BAD_REQUEST"}),
                status_code=400,
                headers={"Content-Type": "application/json"}
            )

        # Define the JSON schema for validation
        payment_request_schema = {
            "type": "object",
            "properties": {
                "amount": {"type": "number", "minimum": 0.01},
                "currency": {"type": "string"},
                "description": {"type": "string"},
                "payerId": {"type": "string"},
                "payeeId": {"type": "string"},
            },
            "required": ["amount", "currency", "payerId", "payeeId"],
            "additionalProperties": False
        }

        # Validate the request against the schema
        validate(instance=request_json, schema=payment_request_schema)

        payment_response = create_payment_response(request_json)
        payment_id = payment_response["paymentId"]
        payments_db[payment_id] = payment_response  # Store the payment in the "database"
        return HttpResponse(
            json.dumps(payment_response),
            status_code=201,
            headers={"Content-Type": "application/json"}
        )

    except ValidationError as e:
        return HttpResponse(
            json.dumps({"error": "Invalid request body", "code": "INVALID_REQUEST", "details": e.message}),
            status_code=400,
            headers={"Content-Type": "application/json"}
        )
    except ValueError as e:
        return HttpResponse(
            json.dumps({"error": "Invalid JSON format", "code": "INVALID_JSON", "details": str(e)}),
            status_code=400,
            headers={"Content-Type": "application/json"}
        )
    except Exception as e:
        return HttpResponse(
            json.dumps({"error": "An unexpected error occurred.", "code": "INTERNAL_ERROR", "details": str(e)}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )


def get_payment(request: HttpRequest, payment_id: str) -> HttpResponse:
    """
    Retrieves payment data by payment ID.

    Args:
        request: The HTTP request object.
        payment_id: The ID of the payment to retrieve.

    Returns:
        The HTTP response object.
    """
    if request.method != 'GET':
        return HttpResponse(
            json.dumps({"error": "Method Not Allowed", "code": "METHOD_NOT_ALLOWED"}),
            status_code=405,
            headers={"Content-Type": "application/json"}
        )

    payment = payments_db.get(payment_id)
    if payment:
        return HttpResponse(
            json.dumps(payment),
            status_code=200,
            headers={"Content-Type": "application/json"}
        )
    else:
        return HttpResponse(
            json.dumps({"error": "Payment not found", "code": "NOT_FOUND"}),
            status_code=404,
            headers={"Content-Type": "application/json"}
        )


def create_payment_response(payment_request: Dict) -> Dict:
    """
    Creates a payment response dictionary.

    Args:
        payment_request: The payment request dictionary.

    Returns:
        The payment response dictionary.
    """
    payment_response = {
        "paymentId": str(uuid.uuid4()),
        "status": "PENDING",
        "amount": payment_request["amount"],
        "currency": payment_request["currency"],
        "description": payment_request.get("description"),
        "payerId": payment_request["payerId"],
        "payeeId": payment_request["payeeId"],
        "createdAt": datetime.datetime.now().isoformat(),
    }
    return payment_response


def main(request: HttpRequest) -> HttpResponse:
    """
    Main function to handle payment requests.

    Args:
        request: The HTTP request object.

    Returns:
        The HTTP response object.
    """
    if request.path == "/payments" and request.method == "POST":
        return create_payment(request)
    elif request.path.startswith("/payments/") and request.method == "GET":
        payment_id = request.path.split("/")[-1]
        return get_payment(request, payment_id)
    else:
        return HttpResponse(
            json.dumps({"error": "Not Found", "code": "NOT_FOUND"}),
            status_code=404,
            headers={"Content-Type": "application/json"}
        )
