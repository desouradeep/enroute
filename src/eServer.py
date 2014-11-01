#!/usr/bin/python
from flask import Flask, render_template
from flask.ext.socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

import os
from werkzeug.wsgi import SharedDataMiddleware

from flask import Flask, request, send_file
from eManager import EManager

import json

from socketio import socketio_manage
from socketio.server import SocketIOServer
from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin, RoomsMixin


eManager = EManager()


class EnrouteNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):
    def recv_connect(self):
        def start_notifying():
            while True:
                self.broadcast_event(
                    'data',
                    eManager.overall_status()
                )
                sockets = len(self.environ['socketio'].server.sockets.keys())
                gevent.sleep(sockets)
        self.spawn(start_notifying)

    def on_user_message(self, payload):
        payload = json.loads(payload)
        print "action: %s" % (payload['action'])
        eManager.create_eNode(payload)
        self.broadcast_event('data', 'new eNode created')


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('my event', namespace='/test')
def test_message(message):
    emit('my response', {'data': message['data']})


@socketio.on('my broadcast event', namespace='/test')
def test_message(message):
    emit('my response', {'data': message['data']}, broadcast=True)


@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected'})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


@app.route("/socket.io/<path:path>")
def run_socketio(path):
    socketio_manage(request.environ, {'': EnrouteNamespace})

if __name__ == '__main__':
    print 'Listening on http://localhost:8080'
    app.debug = True
    app = SharedDataMiddleware(app, {
        '/': os.path.join(os.path.dirname(__file__), 'static')
    })

    SocketIOServer(
        ('0.0.0.0', 8080), app,
        resource="socket.io", policy_server=False
    ).serve_forever()
