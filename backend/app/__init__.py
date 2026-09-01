"""
Online Examination Platform - Flask Application Factory
"""
from flask import Flask
from flask_jwt_extended import JWTManager

from app.extensions.database import db
from app.config.settings import config
from flask_migrate import Migrate
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
    
    # Load configuration
    app.config.from_object(config.get(config_name, config['default']))
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)
    
    # Register blueprints
    register_blueprints(app)
    
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
    
    # Additional blueprints will be registered here as features are implemented:
    # - Authentication routes
    # - User routes
    # - Question routes
    # - Exam routes
    # - Attempt routes
    # - Result routes
    # - Proctoring routes
    # - Notification routes
    # - Admin routes
