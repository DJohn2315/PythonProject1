import socket

HOST = "0.0.0.0"
PORT = 12345

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server listening on {HOST}:{PORT}")

    while True:  # accept clients forever
        conn, addr = s.accept()
        print(f"Connected by {addr}")
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:  # client disconnected
                    print(f"Client {addr} disconnected")
                    break
                msg = data.decode("utf-8", errors="replace")
                print(f"Received from client: {msg}")
                conn.sendall(b"Message received by server")
