import socket
import threading
import queue

HOST = "10.227.93.222"
PORT = 12345

_socket = None
_recv_queue = queue.Queue()

def recv_loop(sock: socket.socket):
    """
    Receive newline-delimited messages and print them.
    """
    buf = b""
    try:
        while True:
            chunk = sock.recv(1024)
            if not chunk:
                _recv_queue.put("\n[Server disconnected]")
                break

            buf += chunk
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                msg = line.decode("utf-8", errors="replace")
                _recv_queue.put(f"Server> {msg}")
    except OSError:
        _recv_queue.put("\n[Receive loop ended]")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print(f"Connected to server at {HOST}:{PORT}")

        s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        t = threading.Thread(target=recv_loop, args=(s,), daemon=True)
        t.start()

        try:
            while True:
                msg = input("You> ")
                if msg.lower() in ("quit", "exit"):
                    print("[Closing connection]")
                    break
                s.sendall((msg + "\n").encode("utf-8"))
        except (BrokenPipeError, ConnectionResetError):
            print("\n[Server connection lost]")
        finally:
            try:
                s.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

def connect(ip, port=PORT):
    global _socket
    try:
        _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _socket.connect((ip, PORT))
        print(f"Connected to server at {ip}:{PORT}")

        _socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        t = threading.Thread(target=recv_loop, args=(_socket,), daemon=True)
        t.start()
        return f"Connection Successful"
    except Exception as e:
        return f"Error: {e}"

def disconnect():
    try:
        print("Attempting Disconnect...")
        _socket.shutdown(socket.SHUT_RDWR)
        print("Successfully Disconnected!")
    except Exception as e:
        return f"Error: {e}"

def get_message():
    messages = []
    while not _recv_queue.empty():
        messages.append(_recv_queue.get_nowait())
    return messages

def send_message(msg):
    try:
        _socket.sendall((msg + "\n").encode("utf-8"))
        _recv_queue.put(f"Client> {msg}")
    except Exception as e:
        return e

if __name__ == "__main__":
    main()