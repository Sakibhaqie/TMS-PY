from flask import Blueprint, jsonify
import datetime

bp = Blueprint('main', __name__)

@bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'service': 'Flask API Demo',
        'version': '1.0.0'
    })

@bp.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        'message': 'Welcome to the Flask API Demo',
        'endpoints': {
            'health_check': '/health',
            'home': '/'
        }
    })