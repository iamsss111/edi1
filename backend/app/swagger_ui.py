"""Development-only Swagger UI registration."""

from pathlib import Path

from flask import Flask, Blueprint, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint


SWAGGER_URL = '/swagger'
SPEC_URL = '/swagger/openapi.yaml'
SPEC_DIRECTORY = Path(__file__).with_name('swagger')

swagger_spec_bp = Blueprint('swagger_spec', __name__)


@swagger_spec_bp.get('/swagger/openapi.yaml')
def openapi_spec():
    return send_from_directory(
        SPEC_DIRECTORY,
        'openapi.yaml',
        mimetype='text/yaml',
    )


def register_swagger(app: Flask) -> None:
    """Register the documentation UI without touching the existing API routes."""
    swagger_ui_bp = get_swaggerui_blueprint(
        SWAGGER_URL,
        SPEC_URL,
        config={
            'app_name': 'Online Examination Platform API',
            'persistAuthorization': True,
        },
    )

    app.register_blueprint(swagger_spec_bp)
    app.register_blueprint(swagger_ui_bp)