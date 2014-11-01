#!/usr/bin/python
from flask import Flask, render_template, request
from flask.ext.socketio import SocketIO, emit
from flask import copy_current_request_context

import gevent
import json

from eManager import EManager


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

eManager = EManager()


##################################
########## Flask views ###########
##################################

@app.route('/')
def index():
    status = eManager.overall_status()
    return render_template('index.html', status=status)


##################################
#### Socket io specific codes ####
##################################

# Connection established with a new client
@socketio.on('connect')
def connect():
    print 'Client connected'

    @copy_current_request_context
    def start_notifying():
        while True:
            emit('data', eManager.overall_status(), broadcast=True)
            sockets = len(request.environ['socketio'].server.sockets.keys())
            gevent.sleep(sockets)
    gevent.spawn(start_notifying)


# Connection to a client lost
@socketio.on('disconnect')
def disconnect():
    print 'Client disconnected'


# New eNode request initiated by a client
@socketio.on('new-eNode')
def new_download(payload):
    payload = json.loads(payload)
    print "action: %s" % (payload['action'])
    eManager.create_eNode(payload)
    emit('data', 'new eNode created', broadcast=True)


if __name__ == '__main__':
    print 'Listening on http://localhost:5000'
    app.DEBUG = True
    socketio.run(app)
