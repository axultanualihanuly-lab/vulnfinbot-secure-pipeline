from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException


def create_app():
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024

    from .routes import bp
    app.register_blueprint(bp)

    @app.after_request
    def add_security_headers(response):
        response.headers["Server"] = "webserver"
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    @app.errorhandler(HTTPException)
    def handle_http_error(e):
        return jsonify(error=e.name), e.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        app.logger.error("Unhandled error: %s", type(e).__name__)
        return jsonify(error="Internal server error"), 500

    return app