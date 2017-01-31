from .GameState import GameState


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
        print('game name: ' + str(self.gameName) + ' player1: ' + self.player1 + ' player2: ' + self.player2)
