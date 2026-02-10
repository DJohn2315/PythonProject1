import socket

HOST = '10.227.93.222' 
PORT = 12345  # match the port number used by server

# Create a socket object
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print(f"Connected to server at {HOST}:{PORT}")
    
    # Send data to the server
    message = "Hello from the client!"
    s.sendall(message.encode('utf-8'))
    
    # Receive the server's response
    data = s.recv(1024)

print(f"Received from server: {data.decode('utf-8')}")
