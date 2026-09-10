"""Flask application factory. Creating an app does not download BART."""
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException


def create_app(test_config=None, service=None):
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    from .config import Config
    from .routes import api
    from .services.summarizer import Summarizer
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})
    app.extensions["summarizer"] = service if service is not None else Summarizer(app.config)
    app.register_blueprint(api)

    @app.errorhandler(HTTPException)
    def http_error(error):
        return jsonify(error=error.description), error.code

    @app.errorhandler(Exception)
    def unexpected_error(error):
        app.logger.exception("Request failed")
        return jsonify(error="Processing failed. Check the backend terminal for details."), 500

    return app
