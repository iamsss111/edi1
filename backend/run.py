"""
Application entry point
"""
import os
from app import create_app
from app.extensions.database import db

def create_app_instance():
    """Create and configure the Flask application"""
    from app.config.settings import config
    config_name = os.getenv('FLASK_ENV', 'development')
    app = create_app(config_name)
    return app

if __name__ == '__main__':
    app = create_app_instance()
    app.run(debug=app.config['DEBUG'])
