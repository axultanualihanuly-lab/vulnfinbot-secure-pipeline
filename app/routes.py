from flask import Blueprint, jsonify, request

bp = Blueprint("main", __name__)

MAX_MESSAGE_LENGTH = 1000


def mock_ai_response(message: str) -> str:
    return "You can start by tracking your income and expenses."


@bp.get("/health")
def health():
    return jsonify(status="healthy"), 200


@bp.post("/api/chat")
def chat():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Invalid JSON body"), 400

    message = data.get("message")
    if message is None:
        return jsonify(error="Field 'message' is required"), 400
    if not isinstance(message, str):
        return jsonify(error="Field 'message' must be a string"), 400

    message = message.strip()
    if not message:
        return jsonify(error="Message must not be empty"), 400
    if len(message) > MAX_MESSAGE_LENGTH:
        return jsonify(error="Message is too long"), 413

    return jsonify(response=mock_ai_response(message)), 200