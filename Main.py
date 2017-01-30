from flask import Flask, request, send_from_directory
from flask_socketio import SocketIO, join_room, leave_room, close_room
from game import Game, GameState
import uuid

app = Flask(__name__)
socket_io = SocketIO(app, async_mode=None)
games = []


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/js/<path:path>')
def scripts(path):
    return send_from_directory('static/js', path)


@socket_io.on('connect', namespace='/gomoku')
def connect():
    print("Client connected: " + request.sid)


@socket_io.on('join room', namespace='/gomoku')
def on_join_room(data):
    game_name = data['room']
    join_room(game_name)
    game = find_game(game_name)
    game.add_player(request.sid)
    emit_game_update_event(game)
    game.print_game_info()


@socket_io.on('make move', namespace='/gomoku')
def on_make_move(data):
    room = data['room']
    game = find_game(room)
    game.next_turn(request.sid, int(data['x']), int(data['y']))
    emit_game_update_event(game)
    if game.state == GameState.FINISHED:
        close_room(room)
        del game


def find_game(game_name):
    return next((x for x in games if str(x.gameName) == game_name), None)


def emit_game_update_event(game):
    socket_io.emit('game updated', {'roomId': str(game.gameName), 'currentPlayer': game.currentPlayer,
                                    'state': str(game.state), 'board': game.board},
                   namespace='/gomoku', room=str(game.gameName))


@socket_io.on('create room', namespace='/gomoku')
def on_create_room():
    new_game = Game(uuid.uuid1())
    games.append(new_game)
    socket_io.emit('room created', {'roomId': str(new_game.gameName)}, namespace='/gomoku', room=request.sid)
    print('Room created: ' + str(new_game.gameName))


@socket_io.on('leave room', namespace='/gomoku')
def on_leave_room(data):
    leave_room(data['room'])
    print(request.sid + ' left room: ' + data['room'])


@socket_io.on('disconnect', namespace='/gomoku')
def disconnect():
    print('Client disconnected: ' + request.sid)


if __name__ == '__main__':
    socket_io.run(app, debug=True, host='0.0.0.0')
