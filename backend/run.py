"""
Application entry point
"""
import os
from app import create_app


if __name__ == '__main__':
    # Get configuration environment
    config_name = os.getenv('FLASK_ENV', 'development')
    
    # Create Flask application
    app = create_app(config_name)
    
    # Run development server
    app.run(debug=app.config['DEBUG'], host='127.0.0.1', port=5000)
