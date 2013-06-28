import sys, json, random

from twisted.internet import reactor
from autobahn.websocket import WebSocketClientFactory, \
                                         WebSocketClientProtocol, \
                                         connectWS

class Channel():
    def __init__(self, name):
        self.name = name
        self.data = 0
        self.quality = 0
    def generate_data(self):
        self.data = random.randrange(1024) * random.choice([-1,1]) + 1024 * 8
        self.quality = random.randrange(200) * random.choice([-1,1]) + 900
        return self.data, self.quality

class BroadcastClientProtocol(WebSocketClientProtocol):
    """
    Simple client that connects to a WebSocket server, send a
    message every 0.02 seconds and print everything it receives.
    """
    def __init__(self):
        ch_names = ['AF3', 'F7', 'F3', 'FC5',
                    'T7', 'P7', 'O1', 'O2',
                    'P8', 'T8', 'FC6', 'F4',
                    'F8', 'AF4']
        self.channels = {}
        for c in ch_names:
            self.channels[c] = Channel(c)

    def sendLevel(self):
        msg = list()
        for c in self.channels:
            data, qlt = self.channels[c].generate_data()
            msg.append({'channel':self.channels[c].name,
                                'signal': data,
                                'quality': qlt})

        self.sendMessage(json.dumps({'channels': msg}))
        reactor.callLater(0.2, self.sendLevel)

    def onOpen(self):
        self.sendLevel()

    def onMessage(self, msg, binary):
        pass
        #print "Got message: " + msg

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Need the WebSocket server address, i.e. ws://localhost:9000"
        sys.exit(1)

    factory = WebSocketClientFactory(sys.argv[1])
    factory.protocol = BroadcastClientProtocol
    connectWS(factory)

    reactor.run()