import socket

# Use '0.0.0.0' to listen on all available interfaces
HOST = '0.0.0.0' 
PORT = 12345  

# Create socket object
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server listening on {HOST}:{PORT}")

    # Accept incoming connections
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            # Receive data from the client
            data = conn.recv(1024)
            if not data:
                break
            print(f"Received from client: {data.decode('utf-8')}")
            # Send a response back to client
            conn.sendall(b'Message received by server')