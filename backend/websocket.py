from flask_socketio import send, emit
# from app import socketio, app
from app import socketio

@socketio.on('connect')
def connect(auth):
    print("recieved " + str(auth))
    # app.logger.info("recieved " + str(auth))
    emit('response', {'Status': "Success"})

@socketio.on('disconnect')
def disconnect(reason):
    print("disconnect: " + str(reason))

@socketio.on('my_event')
def handle_event(json):
    print("recieved event " + str(json))
    emit('response', {'Status': "Event recieved"})
    # app.logger.info("recieved event " + str(json))