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
