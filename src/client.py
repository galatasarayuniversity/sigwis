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


class ChannelBlock():
    def __init__(self, ch_type, ch_count, ch_names):
        self.type = ch_type
        self.count = ch_count
        self.names = ch_names
        self.channels = {}
        for c in ch_names:
            self.channels[c] = Channel(c)


class BroadcastClientProtocol(WebSocketClientProtocol):
    """
    Simple client that connects to a WebSocket server, send a
    message every 0.2 seconds.
    """
    def __init__(self):
        ch_names = ['AF3', 'F7', 'F3', 'FC5',
                    'T7', 'P7', 'O1', 'O2',
                    'P8', 'T8', 'FC6', 'F4',
                    'F8', 'AF4']

        self.client_channels = ChannelBlock("eeg", 14, ch_names)
        self.about = 'type'

    def sendType(self):
        client_type = {'gtype': self.client_channels.type,
                            'gcount': self.client_channels.count,
                            'gnames': self.client_channels.names}
        self.sendMessage(json.dumps({'about': 'config', 'client': client_type }))
        
        if self.about == 'type':
            reactor.callLater(0.2, self.sendType)
        elif self.about == 'level':
            self.sendLevel()

    def sendLevel(self):  
        msg = list()
        for c in self.client_channels.names:
            data, qlt = self.client_channels.channels[c].generate_data()
            msg.append({'channel':self.client_channels.channels[c].name,
                                'signal': data,
                                'quality': qlt})

        self.sendMessage(json.dumps({'about': 'channel', 'channels': msg}))
        if self.about == 'level':    
            reactor.callLater(0.2, self.sendLevel)
        elif self.about == 'type':
            self.sendType()

    def onOpen(self):
        self.sendType()

    def onMessage(self, msg, binary):
        if msg == 'level':
            self.about = 'level'
        elif msg == 'type':
            self.about = 'type'
        #print "Got message: " + msg

if __name__ == '__main__':
    wsaddress = "ws://localhost:9000"
    if len(sys.argv) == 2:
        wsaddress = sys.argv[1]
        print "WebSocket server address: %s " % wsaddress

    factory = WebSocketClientFactory(wsaddress)
    factory.protocol = BroadcastClientProtocol
    connectWS(factory)

    reactor.run()
