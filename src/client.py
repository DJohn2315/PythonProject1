import socket

HOST = "10.227.93.222"
PORT = 12345

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print(f"Connected to server at {HOST}:{PORT}")

    while True:
        message = input("Send> ")  # type messages forever
        if message.lower() in ("quit", "exit"):
            break

        s.sendall(message.encode("utf-8"))
        data = s.recv(1024)
        if not data:
            print("Server closed the connection.")
            break
        print(f"Received from server: {data.decode('utf-8', errors='replace')}")

