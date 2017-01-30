from flask import Flask, request, send_from_directory
from flask_socketio import SocketIO, join_room, leave_room, close_room
from enum import Enum
import uuid

app = Flask(__name__)
socket_io = SocketIO(app, async_mode=None)
games = []


class GameState(Enum):
    NOT_READY = 1
    IN_PROGRESS = 2
    FINISHED = 3


class Game:
    BOARD_SIZE = 15
    LINE_LENGTH = 5

    def __init__(self, game_name):
        self.gameName = game_name
        self.player1 = ''
        self.player2 = ''
        self.state = GameState.NOT_READY
        self.currentPlayer = ''
        self.board = [[0 for x in range(self.BOARD_SIZE)] for y in range(self.BOARD_SIZE)]

    def add_player(self, player):
        if self.player1 == '':
            self.player1 = player
        elif self.player2 == '' and self.player1 != player:
            self.player2 = player
            self.state = GameState.IN_PROGRESS
            self.currentPlayer = self.player1

    def next_turn(self, player, x, y):
        if self.state == GameState.IN_PROGRESS and self.currentPlayer == player:
            if self.board[x][y] == 0:
                # TODO add enum instead of magic numbers
                self.board[x][y] = 1 if player == self.player1 else 2
                if self.check_if_finished(x, y):
                    self.state = GameState.FINISHED
                    return
                self.switch_player(player)

    def check_if_finished(self, x, y):
        symbol = self.board[x][y]
        if self.check_horizontal(y, symbol):
            return True
        if self.check_vertical(x, symbol):
            return True
        if self.check_diagonal(x, y, symbol):
            return True
        return False

    def check_horizontal(self, y, symbol):
        counter = 0
        for x in range(0, self.BOARD_SIZE):
            if self.board[x][y] == symbol:
                counter += 1
            else:
                counter = 0
            if counter == self.LINE_LENGTH:
                return True
        return False

    def check_vertical(self, x, symbol):
        counter = 0
        for y in range(0, self.BOARD_SIZE):
            if self.board[x][y] == symbol:
                counter += 1
            else:
                counter = 0
            if counter == self.LINE_LENGTH:
                return True
        return False

    # TODO refactor
    def check_diagonal(self, x, y, symbol):
        counter = 0

        # first diagonal
        xt = x
        yt = y
        while xt != 0 and yt != 0:
            xt -= 1
            yt -= 1

        for i in range(0, self.BOARD_SIZE):
            if xt + i == self.BOARD_SIZE or yt + i == self.BOARD_SIZE:
                break
            if self.board[xt + i][yt + i] == symbol:
                counter += 1
            else:
                counter = 0
            if counter == self.LINE_LENGTH:
                return True

        # second diagonal
        xt = x
        yt = y
        while xt != 0 and yt != self.BOARD_SIZE - 1:
            xt -= 1
            yt += 1

        for i in range(0, self.BOARD_SIZE):
            if xt + i == self.BOARD_SIZE or yt - i == -1:
                break
            if self.board[xt + i][yt - i] == symbol:
                counter += 1
            else:
                counter = 0
            if counter == self.LINE_LENGTH:
                return True
        return False

    def switch_player(self, player):
        self.currentPlayer = self.player2 if player == self.player1 else self.player1

    def print_game_info(self):
        print('Game name: ' + str(self.gameName) + ' player1: ' + self.player1 + ' player2: ' + self.player2)


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


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
                  'state': str(game.state), 'board': game.board}, namespace='/gomoku',
                   room=str(game.gameName))


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
    socket_io.run(app, debug=True)
