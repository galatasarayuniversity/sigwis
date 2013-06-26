sigwis
======

Real time general purpose signal visualizer for web browsers.

Requirements
------------

### UI Frontend (included)
  * rickshaw.js, d3.js
  * A browser that supports websockets

### Python Backend
  * [twisted](twistedmatrix.com) (Generally found in distribution repositories)
  * [autobahn](autobahn.ws) (You can install using pip)

Simple Test
-----------

```
python src/server.py &
python src/client.py ws://localhost:9000 &
firefox ui/index.html
```

You have to see a number of random series plotted in real-time.

