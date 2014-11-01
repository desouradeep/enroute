$(document).ready(function() {
    WEB_SOCKET_SWF_LOCATION = "/static/WebSocketMain.swf";
    WEB_SOCKET_DEBUG = true;

    // Socket.io specific code
    var socket = io.connect('http://' + document.domain + ':' + location.port);

    // Update DOM as per data received
    socket.on('data', function(data) {
        console.log(data);
    });

    socket.on('connect', function() {
        socket.emit('connect');
    });

    $('#start').click(function () {
        var url = $("#url").val();
        var payload = {
            'action': 'start',
            'url': url,
        };
        socket.emit('new-eNode', JSON.stringify(payload));
        return false;
    });

    $('#stop').click(function () {
        socket.emit('user message', 'stop');
        return false;
    });

    // page height setup specific codes
    function onResize() {
        var window_height = $(window).height();
        var navbar_height = $('#navbar').height();
        var page_wrapper = $('#page-wrapper');
        page_wrapper.height(window_height - navbar_height - 45);
    }
    onResize();
    $(window).resize(function() {
        onResize();
    });
});