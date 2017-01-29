from flask import Flask, render_template, session, request, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from enum import Enum
import uuid

async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None

games = []


class GameState(Enum):
    NOT_READY = 1
    IN_PROGRESS = 2
    FINISHED = 3


class Game:
    def __init__(self, gameName):
        self.gameName = gameName
        self.player1 = ''
        self.player2 = ''
        self.state = GameState.NOT_READY
        self.currentPlayer = ''

    def addPlayer(self, player):
        if self.player1 == '':
            self.player1 = player
        elif self.player2 == '' and self.player1 != player:
            self.player2 = player
            self.state = GameState.IN_PROGRESS
            self.currentPlayer = self.player1

    def nextTurn(self, player, x, y):
        if self.state == GameState.IN_PROGRESS and self.currentPlayer == player:
            print(x + ' ' + y)
            self.currentPlayer = self.player2 if player == self.player1 else self.player1

    def printGameInfo(self):
        print('Game name: ' + str(self.gameName) + ' player1: ' + self.player1 + ' player 2: ' + self.player2)


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@socketio.on('connect', namespace='/gomoku')
def connect():
    print("connect " + request.sid)


@socketio.on('join room', namespace='/gomoku')
def on_join_room(data):
    join_room(data['room'])
    game = next((x for x in games if str(x.gameName) == data['room']), None)
    game.addPlayer(request.sid)
    game.printGameInfo()


@socketio.on('make move', namespace='/gomoku')
def on_make_move(data):
    game = next((x for x in games if str(x.gameName) == data['room']), None)
    game.nextTurn(request.sid, data['x'], data['y'])


@socketio.on('create room', namespace='/gomoku')
def on_create_room():
    newGame = Game(uuid.uuid1())
    newGame.printGameInfo()
    games.append(newGame)
    socketio.emit('room created', {'roomId': str(newGame.gameName)}, namespace='/gomoku', room=str(newGame.gameName))


@socketio.on('leave room', namespace='/gomoku')
def on_leave_room(data):
    leave_room(data['room'])
    print(request.sid + 'left room: ' + data['room'])


@socketio.on('send message', namespace='/gomoku')
def on_receive_message(data):
    print(request.sid + " message: " + data['message'])
    socketio.emit('reply', {'message': data['message']}, namespace='/gomoku', room=data['room'])


@socketio.on('disconnect', namespace='/gomoku')
def disconnect():
    print('disconnect ', request.sid)


if __name__ == '__main__':
    socketio.run(app, debug=True)
