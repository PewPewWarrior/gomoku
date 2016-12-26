import socketio
import eventlet.wsgi
from flask import Flask, send_from_directory

sio = socketio.Server()
app = Flask(__name__)
appPort = 8000


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@sio.on('connect', namespace='/gomoku')
def connect(sid, environ):
    print("connect ", sid)


@sio.on('test event', namespace='/gomoku')
def message(sid, data):
    print("message ", data)
    sio.emit('reply', sid, namespace='/gomoku', room=sid)


@sio.on('disconnect', namespace='/gomoku')
def disconnect(sid):
    print('disconnect ', sid)


if __name__ == '__main__':
    app = socketio.Middleware(sio, app)
    eventlet.wsgi.server(eventlet.listen(('', appPort)), app)
