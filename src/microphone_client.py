import sys, json, alsaaudio, audioop

from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketClientFactory, \
                                         WebSocketClientProtocol, \
                                         connectWS

class Microphone():
    def __init__(self, name):
        self.name = name
        self.inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK)

        # Set attributes: Mono, 8000 Hz, 16 bit little endian samples
        self.inp.setchannels(1)
        self.inp.setrate(8000)
        self.inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        self.inp.setperiodsize(160)

    def get_level(self):
        # Read data from device
        l, data = self.inp.read()
        if l:
            # Return the maximum of the absolute value of
            # all samples in a fragment.
            level = audioop.max(data, 2)
            # 'Level' should fit the screen when we draw it.
            # Max value of the 'level' is 32767.
            # In .html file, screen height is 500.
            # So let's divide 'level' by for example 65.
            # So that it can fit to the screen
            return str(level // 40)
        else:
            return str(0)


class ChannelBlock():
    def __init__(self, ch_type, ch_count, ch_names):
        self.type = ch_type
        self.count = ch_count
        self.names = ch_names
        self.channels = {}
        for c in ch_names:
            self.channels[c] = Microphone(c)


class BroadcastClientProtocol(WebSocketClientProtocol):
    """
    Simple client that connects to a WebSocket server, send the Microphone's
    data every 0.015 seconds and print everything it receives.
    """
    def __init__(self):
        ch_names = ['Mic']
        self.client_channels = ChannelBlock("microphone", 1, ch_names)
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
            data = self.client_channels.channels[c].get_level()
            msg.append({'channel':self.client_channels.channels[c].name,
                                'signal': data,
                                'quality': 0})

        self.sendMessage(json.dumps({'about': 'channel', 'channels': msg}))
        if self.about == 'level':
            reactor.callLater(0.015, self.sendLevel)
        elif self.about == 'type':
            self.sendType()

    def onOpen(self):
        self.sendType()

    def onMessage(self, msg, binary):
        if msg == 'level':
            self.about = 'level'
        elif msg == 'type':
            self.about = 'type'
        # Debug
        # print "Got message: " + msg

if __name__ == '__main__':
    wsaddress = "ws://localhost:9000"
    if len(sys.argv) == 2:
        wsaddress = sys.argv[1]
        print "WebSocket server address: %s " % wsaddress

    factory = WebSocketClientFactory(wsaddress)
    factory.protocol = BroadcastClientProtocol
    connectWS(factory)

    reactor.run()
