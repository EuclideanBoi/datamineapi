from flask import Blueprint, request, jsonify
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
            return jsonify({'Status': "Success", 'UID': login_result.uid, 'Token': login_result.session_token}), 200
        return jsonify({'Status': "Error"}), 401
    
    @api_bp.route('/api/logout', methods=['POST'])
    def logout():
        data = request.get_json()
        token = data.get('token')
        if db.logout(token, request.environ.get('HTTP_X_REAL_IP', request.remote_addr)):
            return jsonify({'Status': "Success"}), 200
        return jsonify({'Status': "Error"}), 401
    
    @api_bp.route('/api/create-api-user', methods=['POST'])
    def create_api_user():
        data = request.get_json()
        token = data.get('token')
        if db.check_token(token): # TODO: ACL CHECK
            result = db.create_api_user()
            return jsonify({'Status': "Success", 'Key': result}), 200
        return jsonify({'Status': "Invalid token"}), 401

    return api_bp