"""
Online Examination Platform - Flask Application Factory
"""
from flask import Flask, app
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.extensions.database import db
from app.config.settings import config
from flask_migrate import Migrate
from flasgger import Swagger
from app import models

migrate = Migrate()


def create_app(config_name: str = 'development') -> Flask:
    """
    Create and configure the Flask application.
    
    Args:
        config_name: The configuration environment ('development', 'testing', 'production')
    
    Returns:
        Configured Flask application instance
    """
    # Create Flask application
    app = Flask(__name__)
    swagger_config = {
    "swagger": "2.0",
    "info": {
        "title": "Online Examination Platform API",
        "description": "REST API for the Online Examination Platform",
        "version": "1.0.0"
    },
    "securityDefinitions": {
    "BearerAuth": {
        "type": "apiKey",
        "name": "Authorization",
        "in": "header",
        "description": "Enter: Bearer <your JWT token>"
    }
}
}

    Swagger(app, config={
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec_1",
            "route": "/apispec_1.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "specs_route": "/apidocs/"
}, template=swagger_config)
    
    # Load configuration
    app.config.from_object(config.get(config_name, config['default']))

    CORS(
        app,
        origins=[
            'http://127.0.0.1:5500',
            'http://localhost:5500'
        ],
        supports_credentials=False
    )
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)
    
    # Register blueprints
    register_blueprints(app)

    if config_name == 'development':
        from app.swagger_ui import register_swagger
        register_swagger(app)
    
    return app


def register_blueprints(app: Flask) -> None:
    """
    Register all Flask blueprints with the application.
    
    Args:
        app: The Flask application instance
    """
    # Health check blueprint
    from app.routes.health_routes import health_bp
    app.register_blueprint(health_bp, url_prefix='/api/v1')

    # Authentication blueprint
    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/v1')

    from app.routes.exam_attempt_routes import exam_attempt_bp
    app.register_blueprint(exam_attempt_bp, url_prefix='/api/v1')

    from app.routes.question_routes import question_bp
    app.register_blueprint(question_bp, url_prefix='/api/v1')

    from app.routes.student_answer_routes import student_answer_bp
    app.register_blueprint(student_answer_bp, url_prefix='/api/v1')

    from app.routes.exam_submission_routes import exam_submission_bp
    app.register_blueprint(exam_submission_bp, url_prefix='/api/v1')

    from app.routes.evaluation_routes import evaluation_bp
    app.register_blueprint(evaluation_bp, url_prefix='/api/v1')

    from app.routes.result_routes import result_bp
    app.register_blueprint(result_bp, url_prefix='/api/v1')

    from app.routes.integrity_routes import integrity_bp
    app.register_blueprint(integrity_bp, url_prefix='/api/v1')

    from app.routes.faculty_subject_routes import faculty_subject_bp
    app.register_blueprint(faculty_subject_bp, url_prefix='/api/v1')

    from app.routes.faculty_question_routes import faculty_question_bp
    app.register_blueprint(faculty_question_bp, url_prefix='/api/v1')

    from app.routes.faculty_question_option_routes import faculty_question_option_bp
    app.register_blueprint(faculty_question_option_bp, url_prefix='/api/v1')

    from app.routes.faculty_exam_routes import faculty_exam_bp
    app.register_blueprint(faculty_exam_bp, url_prefix='/api/v1')

    from app.routes.faculty_exam_question_routes import faculty_exam_question_bp
    app.register_blueprint(faculty_exam_question_bp, url_prefix='/api/v1')

    from app.routes.faculty_exam_schedule_routes import faculty_exam_schedule_bp
    app.register_blueprint(faculty_exam_schedule_bp, url_prefix='/api/v1')

    from app.routes.faculty_exam_publish_routes import faculty_exam_publish_bp
    app.register_blueprint(faculty_exam_publish_bp, url_prefix='/api/v1')

    from app.routes.admin_routes import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/v1')