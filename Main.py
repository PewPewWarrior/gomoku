from flask import Flask, request, send_from_directory
from flask_socketio import SocketIO, join_room, close_room
from game import Game, GameState
import uuid
import time
import threading

MOVE_TIMEOUT = 300
THREAD_SLEEP_TIME = 300

app = Flask(__name__)
socket_io = SocketIO(app)
thread = None
games = []


@app.route('/')
def index():
    global thread
    if thread is None:
        thread = threading.Thread(target=close_inactive_games_thread)
        thread.start()
    return send_from_directory('static', 'index.html')


def close_inactive_games_thread():
    while True:
        time.sleep(THREAD_SLEEP_TIME)
        close_inactive_games()


def close_inactive_games():
    for game in games:
        if time.time() - game.lastMoveTimestamp > MOVE_TIMEOUT:
            close_room(game.gameName)
            games.remove(game)


@socket_io.on('connect')
def connect():
    print("Client connected: " + request.sid)


@socket_io.on('join room')
def on_join_room(data):
    game_name = data['room']
    join_room(game_name)
    game = find_game(game_name)
    game.add_player(request.sid)
    emit_game_update_event(game)
    game.print_game_info()


@socket_io.on('make move')
def on_make_move(data):
    room = data['room']
    game = find_game(room)
    if game is not None:
        game.next_turn(request.sid, int(data['x']), int(data['y']))
        emit_game_update_event(game)
        if game.state == GameState.FINISHED:
            close_room(room)
            games.remove(game)


def find_game(game_name):
    return next((x for x in games if str(x.gameName) == game_name), None)


def emit_game_update_event(game):
    socket_io.emit('game updated', {'roomId': str(game.gameName), 'currentPlayer': game.currentPlayer,
                                    'state': str(game.state), 'board': game.board},
                   room=str(game.gameName))


def emit_game_interrupted_event(game):
    socket_io.emit('game interrupted', {'roomId': str(game.gameName), 'reason': 'other player left'},
                   room=str(game.gameName))


@socket_io.on('create room')
def on_create_room():
    new_game = Game(uuid.uuid1())
    games.append(new_game)
    socket_io.emit('room created', {'roomId': str(new_game.gameName)}, room=request.sid)
    print('Room created: ' + str(new_game.gameName))


@socket_io.on('leave room')
def on_leave_room(data):
    room = data['room']
    game = find_game(room)
    if game.player1 == request.sid or game.player2 == request.sid:
        emit_game_interrupted_event(game)
        close_room(room)
        games.remove(game)
    print(request.sid + ' left room: ' + room)


@socket_io.on('disconnect')
def disconnect():
    print('Client disconnected: ' + request.sid)


if __name__ == '__main__':
    socket_io.run(app, debug=True, host='0.0.0.0', port=5000)
