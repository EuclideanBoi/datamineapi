from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_socketio import SocketIO
from backend.db import Database
from backend.api import api_blueprint
from argon2 import PasswordHasher
import time
import os
from dotenv import load_dotenv
import logging

load_dotenv()

app = Flask(__name__)

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

db_uri = os.getenv('DATABASE_URL', 'sqlite:///datamine.db')
is_postgres = True
if db_uri == 'sqlite:///datamine.db':
    app.logger.info("No database URI specified, using local SQLite database")
    is_postgres = False
db = Database(app, db_uri, is_postgres)
app.register_blueprint(api_blueprint(db, app))
socketio = SocketIO(cors_allowed_origins="*")
CORS(app)
socketio.init_app(app)

if __name__ == "__main__":
    app.run(ssl_context=('cert.pem', 'key.pem'))