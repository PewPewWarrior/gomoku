from flask import Flask, render_template, session, request, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from enum import Enum
import uuid

app = Flask(__name__)
socketio = SocketIO(app, async_mode=None)
games = []


class GameState(Enum):
    NOT_READY = 1
    IN_PROGRESS = 2
    FINISHED = 3


class Game:
    def __init__(self, game_name):
        self.gameName = game_name
        self.player1 = ''
        self.player2 = ''
        self.state = GameState.NOT_READY
        self.currentPlayer = ''

    def add_player(self, player):
        if self.player1 == '':
            self.player1 = player
        elif self.player2 == '' and self.player1 != player:
            self.player2 = player
            self.state = GameState.IN_PROGRESS
            self.currentPlayer = self.player1

    def next_turn(self, player, x, y):
        if self.state == GameState.IN_PROGRESS and self.currentPlayer == player:
            print(x + ' ' + y)
            self.switch_player(player)

    def switch_player(self, player):
        self.currentPlayer = self.player2 if player == self.player1 else self.player1

    def print_game_info(self):
        print('Game name: ' + str(self.gameName) + ' player1: ' + self.player1 + ' player2: ' + self.player2)


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@socketio.on('connect', namespace='/gomoku')
def connect():
    print("Client connected: " + request.sid)


@socketio.on('join room', namespace='/gomoku')
def on_join_room(data):
    game_name = data['room']
    join_room(game_name)
    game = find_game(game_name)
    game.add_player(request.sid)
    emit_game_update_event(game)
    game.print_game_info()


@socketio.on('make move', namespace='/gomoku')
def on_make_move(data):
    game = find_game(data['room'])
    game.next_turn(request.sid, data['x'], data['y'])
    emit_game_update_event(game)


def find_game(game_name):
    return next((x for x in games if str(x.gameName) == game_name), None)


def emit_game_update_event(game):
    socketio.emit('game updated', {'roomId': str(game.gameName), 'currentPlayer': game.currentPlayer,
                                   'state': str(game.state)}, namespace='/gomoku', room=str(game.gameName))


@socketio.on('create room', namespace='/gomoku')
def on_create_room():
    new_game = Game(uuid.uuid1())
    games.append(new_game)
    socketio.emit('room created', {'roomId': str(new_game.gameName)}, namespace='/gomoku', room=request.sid)
    print('Room created: ' + str(new_game.gameName))


@socketio.on('leave room', namespace='/gomoku')
def on_leave_room(data):
    leave_room(data['room'])
    print(request.sid + ' left room: ' + data['room'])


@socketio.on('disconnect', namespace='/gomoku')
def disconnect():
    print('Client disconnected: ' + request.sid)


if __name__ == '__main__':
    socketio.run(app, debug=True)
