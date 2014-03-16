###############################################################################
##
##  Copyright 2011,2012 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##        http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

import sys, json

from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.twisted.websocket import WebSocketServerFactory, \
                                         WebSocketServerProtocol, \
                                         listenWS


class BroadcastServerProtocol(WebSocketServerProtocol):

    def __init__(self):
        self.client = ""
        self.saved = False

    def onOpen(self):
        self.factory.register(self)

    def onMessage(self, msg, binary):
        if not binary:
            if msg == "type":
                if self.saved:
                    self.factory.broadcast("%s" % self.client)
                else:
                    self.factory.broadcast(msg)

            elif msg == "level":
                self.factory.broadcast(msg)

            elif not self.saved:
                try:
                    check = json.loads(msg)
                except ValueError:
                    pass
                else:
                    if check["about"] == "config":
                        self.saveClientData(msg)
                finally:
                    self.factory.broadcast("%s" % msg)

            else:
                self.factory.broadcast("%s" % msg)

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)

    def saveClientData(self, msg):
        self.client = msg
        self.saved = True

class BroadcastServerFactory(WebSocketServerFactory):
    """
    Simple broadcast server broadcasting any message it receives to all
    currently connected clients.
    """

    def __init__(self, url, debug = False, debugCodePaths = False):
        WebSocketServerFactory.__init__(self, url, debug = debug,
                                            debugCodePaths = debugCodePaths)
        self.clients = []

    def register(self, client):
        if not client in self.clients:
            print "client registered"
            self.clients.append(client)

    def unregister(self, client):
        if client in self.clients:
            print "client unregistered"
            self.clients.remove(client)
            self.broadcast(json.dumps({'about': 'disconnect' }))

    def broadcast(self, msg):
        for c in self.clients:
            c.sendMessage(msg)

if __name__ == '__main__':

    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        log.startLogging(sys.stdout)
        debug = True
    else:
        debug = False

    ServerFactory = BroadcastServerFactory

    factory = ServerFactory("ws://localhost:9000",
                                    debug = debug,
                                    debugCodePaths = debug)

    factory.protocol = BroadcastServerProtocol
    factory.setProtocolOptions(allowHixie76 = True)
    listenWS(factory)

    webdir = File(".")
    web = Site(webdir)
    reactor.listenTCP(8080, web)

    reactor.run()
