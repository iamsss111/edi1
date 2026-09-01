"""
Health check routes for API verification
"""
from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__)


@health_bp.get('/health')
def health_check():
    """
    Health check endpoint to verify the API is running.
    
    Returns:
        JSON response with health status
    """
    return jsonify({
        'success': True,
        'message': 'Online Examination Platform API is running'
    }), 200


@health_bp.get('/db-health')
def database_health_check():
    """
    Verify that Flask can connect to finaldb through SQLAlchemy.
    """
    from sqlalchemy import text
    from app.extensions.database import db

    try:
        result = db.session.execute(text('SELECT DATABASE()'))
        database_name = result.scalar()

        return jsonify({
            'success': True,
            'message': 'Database connection successful',
            'database': database_name
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Database connection failed',
            'error': str(e)
        }), 500