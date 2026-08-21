from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required
from backend.db import Database

def is_valid_username(input: str):
    return True

def api_blueprint(db: Database, app):
    api_bp = Blueprint('api', __name__)

    @api_bp.route('/api/health', methods=['GET'])
    def health():
        return jsonify({'Status': "Ok"}), 200

    @api_bp.route('/api/login', methods=['POST'])
    def login():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        login_result = db.login(username, password, request.environ.get('HTTP_X_REAL_IP', request.remote_addr))
        if login_result is not False:
            return jsonify({'Status': "Success", 'Username': username}), 200
        return jsonify({'Status': "Error"}), 401
    
    return api_bp