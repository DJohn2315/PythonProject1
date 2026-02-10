import socket

s = socket.socket()
print("Socket created!")

port = 8080

s.bind(('', port))
print("Socket bound to %s" %(port))

s.listen(5)
print("Socket is listening")

while True:
    c, addr = s.accept()
    print("Got connection from ", addr)

    c.send("Connection established".encode())

    c.close()

    break