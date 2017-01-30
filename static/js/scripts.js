socket = io.connect('http://localhost:5000/gomoku');
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
$('form#makeMove').submit(function(event) {
    socket.emit('make move', {room: currentRoom, x: $('#x').val(), y: $('#y').val()});
    return false;
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
    formatted = '';
    for(var i = 0; i < 15; i++) {
        for(var z = 0; z < 15; z++) {
            formatted += (board[z][i]);
        }
        formatted += '<br>';
    }
    return formatted;
}