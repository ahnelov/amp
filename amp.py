#!/usr/bin/env python3

# Copyright 2015 Martin Ahnelöv

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import socketserver

class TCPHandler(socketserver.BaseRequestHandler):

    def setup(self):
        print("Client connecting from %s:%d" % (self.client_address[0], 
                                                self.client_address[1]))
        self.open = True # Connection is open
        
        # Add to the number of concurrent handlers
        self.server.handlers += 1
        
        return
        
    def handle(self):
        # self.request is the TCP socket connected to the client
        
        while self.open: # Keep listening and processing commands
            try:
                data = self.request.recv(1024)
            except OSError:
                break
            
            # Debug Mode
            if __name__ == "__main__":
                print(self.client_address[0].encode() + b": " + data)
            
            data = data.decode()
                        
            # Have they sent a command?
            if data[0:4] == "CMDS":
                
                try:
                    data_length = int(data[4:8])
                    cmd_type = data[8]
                    cmd_code = data[10:12]
                except IndexError:
                    message = "Command not understood from %s: %s"
                    print(message % (self.client_address, data))
                    continue
                
                # Dissect the command one bit at a time.
                # Start with the type, then the command code.
                # If there is parameters we look at those too
                # before deciding what callback function to invoke.
                
                if cmd_type == "2":
                    # Transport controls
                    if cmd_code == "00":
                        # Stop
                        if self.server.STOP:
                            self.server.STOP()
                            
                    elif cmd_code == "01":
                        # Play
                        if self.server.PLAY:
                            self.server.PLAY()
                
                elif cmd_type == "4":
                    # Manage clips in timeline
                    if cmd_code == "42":
                        # Loop
                        if data[12] == "1":
                            # On
                            if self.server.LOOP_ON:
                                self.server.LOOP_ON()
                            if self.server.LOOP:
                                self.server.LOOP(True)
                                
                        elif data[12] == "0":
                            # Off
                            if self.server.LOOP_OFF:
                                self.server.LOOP_OFF()
                            if self.server.LOOP:
                                self.server.LOOP(False)
                    
                elif cmd_type.upper() == "A":
                    # More clip management
                    if cmd_code == "16":
                        # Cue
                        if self.server.CUE:
                            self.server.CUE()
            
            self.ACK()
        
        self.request.close()
        return
    
    def finish(self):
        print("Client disconnected: %s:%d" % (self.client_address[0], 
                                                self.client_address[1]))
        
        self.open = False
        
        # Remove from the number of concurrent handlers
        self.server.handerls = -= 1
        
        return

    def ACK(self):
        try:
            self.request.send(b"\x06") # ACK-character
        except OSError as errMsg:
            print("Client error: %s:%d: %s" % (self.client_address[0], 
                                                self.client_address[1],
                                                errMsg))
            self.open = False
            
        
class Server(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def __init__(self):
        self.HOST = "" # Accept connections from any interfaces with
        self.PORT = 3811 #                                  any IP address
        socketserver.TCPServer.__init__(self, (self.HOST, self.PORT), 
                                                TCPHandler)
        self.daemon_threads = True
        
        # Number of concurrent handlers. Is this built in anywhere?
        self.handlers = 0
        
        # Callbacks
        self.PLAY = None
        self.CUE  = None # Not possible to send a 8X.16 as response as specified
        self.STOP = None
        self.LOOP = None # Takes one boolean argument (On/Off)
        self.LOOP_ON  = None
        self.LOOP_OFF = None
        
if __name__ == "__main__":
    
    # Debug Mode. Create a server
    server = Server()
    
    server.PLAY = lambda: print("command: PLAY")
    server.CUE  = lambda: print("command: CUE")
    server.STOP = lambda: print("command: STOP")
    server.LOOP = lambda bool: print("command: LOOP %s" % bool)       
    server.LOOP_ON  = lambda: print("command: LOOP ON")
    server.LOOP_OFF = lambda: print("command: LOOP OFF")
    
    # Start the server
    server.serve_forever()
    

# Commands from a Ross Carbonite vision switcher:    
# b'CRAT0007204Vtr1\n' # On connect
# b'CMDS00042001\n' # Play
# b'CMDS0004A016\n' # Cue
# b'CMDS000541421\n' # Lp On
# b'CMDS000541420\n' # Lp Off
# b'CMDS00042000\n' # Stop

# Example:
# CMDS00042001 (Play)
# MSG |Bytes|CMD |Byte |CMD |
# Type|to \n|Type|Count|Code| NL
# -------------------------------
# CMDS|0004 | 2  | 0   | 01 | \n

# MSG Type and Bytes to \n is specific to AMP over IP. Bytes to \n will in
# 4 digits denote the number of bytes between byte 9 and the newline character.
# CMD Type is the category of AMP command to be executed.
# Byte count refers to the number of extra bytes insert between
# the CMD Code and the newline character. These extra bytes are arguments for
# the AMP command.
# Command code is a 2-byte ID number for the AMP command the client
# tries to run. Together with the CMD Type this identifier is unique.
