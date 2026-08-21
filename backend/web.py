from flask import Blueprint, send_from_directory

def web_blueprint(app):
    web_bp = Blueprint('web', __name__)

    @web_bp.route('/', methods=['GET'])
    def index():
        return send_from_directory('./frontend', 'index.html')

    return web_bp