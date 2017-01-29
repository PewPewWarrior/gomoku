from flask import Flask, render_template, session, request, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@socketio.on('connect', namespace='/gomoku')
def connect():
    print("connect " + request.sid)


@socketio.on('join room', namespace='/gomoku')
def on_join_room(data):
    join_room(data['room'])
    print(request.sid + ' joined room: ' + data['room'])


@socketio.on('leave room', namespace='/gomoku')
def on_leave_room(data):
    leave_room(data['room'])
    print(request.sid + 'left room: ' + data['room'])


@socketio.on('test event', namespace='/gomoku')
def message(data):
    print("message ", data)
    socketio.emit('reply', {'data': 'Ok!'}, namespace='/gomoku', room=data['room'])


@socketio.on('disconnect', namespace='/gomoku')
def disconnect():
    print('disconnect ', request.sid)


if __name__ == '__main__':
    socketio.run(app, debug=True)
