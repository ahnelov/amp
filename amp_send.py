import socket

# Mockup aplication to test the AMP server. 
# Should be replaced with real unit testing.

TCP_IP = '127.0.0.1'
TCP_PORT = 3811

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

while True:
    c = input("--> ")

    #s.send(c.encode())
    
    if c == "1": # Connect
        s.send(b'CRAT0007204Vtr1\n')
    
    elif c == "2": # Play
        s.send(b'CMDS00042001\n')
    
    elif c == "3": # Cue
        s.send(b'CMDS0004A016\n')
    
    elif c == "4": # Lp On
        s.send(b'CMDS000541421\n')
        
    elif c == "5": # Lp Off
        s.send(b'CMDS000541420\n')
    
    elif c == "6": # Stop
        s.send(b'CMDS00042000\n')
    
    elif c == "q":
        break
    
    else:
        continue # Go to the start of the loop.
        
    print(s.recv(1024))

s.close()
