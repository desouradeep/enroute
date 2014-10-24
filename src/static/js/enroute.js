$(document).ready(function() {
    WEB_SOCKET_SWF_LOCATION = "/static/WebSocketMain.swf";
    WEB_SOCKET_DEBUG = true;

    // Socket.io specific code
    var socket = io.connect('/enroute');

    // Update the graph when we get new data from the server
    socket.on('data', function(data) {
        console.log(data);
    });

    $('#start').click(function () {
        var url = $("#url").val();
        var payload = {
            'action': 'start',
            'url': url,
        };
        socket.emit('user message', JSON.stringify(payload));
        return false;
    });

    $('#stop').click(function () {
        socket.emit('user message', 'stop');
        return false;
    });
});