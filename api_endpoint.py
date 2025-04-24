import uuid
import datetime
import json
from typing import Dict, Optional
from google.cloud.functions import HttpRequest
from google.cloud.functions import HttpResponse
from jsonschema import validate, ValidationError
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR)

class ErrorCode(Enum):
    METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED"
    BAD_REQUEST = "BAD_REQUEST"
    INVALID_JSON = "INVALID_JSON"
    INVALID_REQUEST = "INVALID_REQUEST"
    MISSING_FIELD = "MISSING_FIELD"
    INVALID_FIELD_TYPE = "INVALID_FIELD_TYPE"
    INVALID_FIELD_VALUE = "INVALID_FIELD_VALUE"
    NOT_FOUND = "NOT_FOUND"
    INTERNAL_ERROR = "INTERNAL_ERROR"

# In a real application, you would use a database to store and retrieve payment data.
# Here, we'll use a simple in-memory dictionary for demonstration purposes.
payments_db: Dict[str, Dict] = {}

def error_response(error_message: str, error_code: ErrorCode, status_code: int, details: Optional[str] = None) -> HttpResponse:
    """
    Creates a standardized error response.

    Args:
        error_message: A human-readable error message.
        error_code: The error code.
        status_code: The HTTP status code.
        details: Optional details about the error.

    Returns:
        The HTTP response object.
    """
    response_body = {"error": error_message, "code": error_code.value}
    if details:
        response_body["details"] = details
    return HttpResponse(
        json.dumps(response_body),
        status_code=status_code,
        headers={"Content-Type": "application/json"}
    )

def create_payment(request: HttpRequest) -> HttpResponse:
    """
    Creates a payment request.

    Args:
        request: The HTTP request object.

    Returns:
        The HTTP response object.
    """
    if request.method != 'POST':
        return error_response("Method Not Allowed", ErrorCode.METHOD_NOT_ALLOWED, 405)

    try:
        request_json = request.get_json(silent=True)
        if request_json is None:
            return error_response("Invalid JSON format", ErrorCode.INVALID_JSON, 400, "Request body is not valid JSON")
        if not request_json:
            return error_response("Bad Request", ErrorCode.BAD_REQUEST, 400, "Request body is empty")

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
        if e.validator == "required":
            error_code = ErrorCode.MISSING_FIELD
            details = f"Missing required field: {', '.join(e.path)}"
        elif e.validator == "type":
            error_code = ErrorCode.INVALID_FIELD_TYPE
            details = f"Invalid type for field '{e.path[-1]}'. Expected {e.validator_value}, got {e.instance.__class__.__name__}"
        elif e.validator == "minimum":
            error_code = ErrorCode.INVALID_FIELD_VALUE
            details = f"Invalid value for field '{e.path[-1]}'. Minimum value is {e.validator_value}"
        else:
            error_code = ErrorCode.INVALID_REQUEST
            details = e.message

        return error_response("Invalid request body", error_code, 400, details)
    except ValueError as e:
        return error_response("Invalid JSON format", ErrorCode.INVALID_JSON, 400, str(e))
    except Exception as e:
        logging.exception("An unexpected error occurred.")
        return error_response("An unexpected error occurred.", ErrorCode.INTERNAL_ERROR, 500, str(e))


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
        return error_response("Method Not Allowed", ErrorCode.METHOD_NOT_ALLOWED, 405)

    payment = payments_db.get(payment_id)
    if payment:
        return HttpResponse(
            json.dumps(payment),
            status_code=200,
            headers={"Content-Type": "application/json"}
        )
    else:
        return error_response("Payment not found", ErrorCode.NOT_FOUND, 404)


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
        return error_response("Not Found", ErrorCode.NOT_FOUND, 404)
