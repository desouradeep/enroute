from gevent import monkey; monkey.patch_all()
import gevent

from socketio import socketio_manage
from socketio.server import SocketIOServer
from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin, RoomsMixin

from eManager import EManager

class EnrouteNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):
    eManager = EManager()

    def recv_connect(self):
        print 'recv_connect'
        def sendcpu():
            while True:
                self.eManager.id += 1
                self.broadcast_event(
                    'data',
                    self.eManager.overall_status()
                )
                gevent.sleep(0.1)
        self.spawn(sendcpu)

    def on_user_message(self, msg):
        print "ACTION: %s" % (msg)
        self.broadcast_event('data', {'ACTION': msg})


class Application(object):
    def __init__(self):
        self.buffer = []

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO'].strip('/') or 'index.html'

        if path.startswith('static/') or path == 'index.html':
            try:
                data = open(path).read()
            except Exception:
                return not_found(start_response)

            if path.endswith(".js"):
                content_type = "text/javascript"
            elif path.endswith(".css"):
                content_type = "text/css"
            elif path.endswith(".swf"):
                content_type = "application/x-shockwave-flash"
            else:
                content_type = "text/html"

            start_response('200 OK', [('Content-Type', content_type)])
            return [data]

        if path.startswith("socket.io"):
            socketio_manage(environ, {'/enroute': EnrouteNamespace})
        else:
            return not_found(start_response)

        def hello(self):
            print "hello world"

def not_found(start_response):
    start_response('404 Not Found', [])
    return ['<h1>Not Found</h1>']


if __name__ == '__main__':
    print 'Listening on port http://0.0.0.0:8080 and on port 10843 (flash policy server)'
    SocketIOServer(('0.0.0.0', 8080), Application(),
        resource="socket.io", policy_server=True,
        policy_listener=('0.0.0.0', 10843)).serve_forever()
