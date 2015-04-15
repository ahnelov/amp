# amp
Python library to mimic an AMP Video Server.

With this library you will be able to start a server and listen for commands from any number of clients connected. When a command is understood a callback function that the user have registered for that particular command is executed.

This library is primarily developed for use with Ross vision switchers (tested with a Ross Carbonite v9) and do only support a very small amount of commands. It also have other limitations, like that all clients only control one channel. More commands will be added as the need arises.

## Installation

Drop `amp.py` in the directory of the project you wish use it with.

This project is developed with and tested on python 3.4. I do not know if it will run on python 2.7, but if you get it to work, please let me know.

This library uses the built-in `socketserver` library, and have no external dependancies.

## Usage

This library is very easy to implement:

```python
import amp

server = amp.Server()

# Add callbacks
server.PLAY = lambda: print("command: PLAY")
server.CUE  = lambda: print("command: CUE")
server.STOP = lambda: print("command: STOP")
server.LOOP = lambda bool: print("command: LOOP %s" % bool)       
server.LOOP_ON  = lambda: print("command: LOOP ON")
server.LOOP_OFF = lambda: print("command: LOOP OFF")

# Start the server. This is blocking.
server.serve_forever()
```

You can also define your functions without using a lambda:

```python
import amp

def load(clip):
    print("Loading clip: %s" %clip)

def play():
    print("Play!")

server = amp.Server()

server.PLAY = play
server.CUE  = lambda: load("MyClip.ogg")

server.serve_forever()
```

## Caveats

`Server.CUE` will not send any response to the client regarding what clip was successfully loaded, even though it should do that according to the specification.

When a loop on/off command is recieved (41.42) two callback commands will be executed: first `Server.LOOP_ON` or `Server.LOOP_OFF`, after that `Server.LOOP` will be executed with either a `True` or `False` as the first argument.
