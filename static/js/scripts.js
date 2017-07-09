socket = io();
currentRoom = '';
userId = '';

<!-- event handlers -->
socket.on('connect', function() {
    userId = socket.io.engine.id;
});
socket.on('room created', function(data) {
    currentRoom = data.roomId;
    socket.emit('join room', {room: currentRoom});
    updateRoomInfo();
});
socket.on('game interrupted', function(data) {
    currentRoom = '';
    updateRoomInfo();
    updateStatus(data.reason);
});
socket.on('game updated', function(data) {
    if (data.state == 'GameState.NOT_READY') {
        updateStatus('Waiting for other player to join');
    } else if (data.state == 'GameState.FINISHED') {
        if (data.currentPlayer == userId) {
            updateStatus('You won!');
        } else {
            updateStatus('You lost!');
        }
    } else if (data.currentPlayer == userId) {
        updateStatus('Your turn!');
    } else {
        updateStatus('Other player turn!');
    }
    updateBoard(data.board);
});

<!-- form handlers -->
$('form#createRoom').submit(function(event) {
    socket.emit('create room');
    return false;
});
$('form#joinRoom').submit(function(event) {
    currentRoom = $('#roomId').val();
    socket.emit('join room', {room: currentRoom});
    updateRoomInfo();
    return false;
});

$(window).on("beforeunload", function() {
    socket.emit('leave room', {room: currentRoom});
});

<!-- helper functions -->
function updateRoomInfo() {
    $('#gameId').html('Current room: ' + currentRoom);
}
function updateStatus(status) {
    $('#status').html(status);
}
function updateBoard(board) {
    $('#board').html(formatBoard(board));
}
function formatBoard(board) {
    BOARD_SIZE =15;
    formatted = '';
    for (var y = 0; y < BOARD_SIZE; y++) {
        for (var x = 0; x < BOARD_SIZE; x++) {
            if (board[x][y] == '0') {
                formatted +=
                        '<img class="square" src="static/img/empty.png" onclick="selectSquare('+ x + ',' + y + ')">';
            } else if (board[x][y] == '1') {
                formatted += '<img class="square" src="static/img/x.png">';
            } else {
                formatted += '<img class="square" src="static/img/o.png">';
            }
            if (x != BOARD_SIZE - 1) {
                formatted += '<img class="verticalBar" src="static/img/solid.png">';
            }
        }
        if (y != BOARD_SIZE - 1) {
            formatted += '<img class="horizontalBar" src="static/img/solid.png">';
        }
    }
    return formatted;
}
function selectSquare(x, y) {
    socket.emit('make move', {room: currentRoom, x: x, y: y});
    return false;
}
