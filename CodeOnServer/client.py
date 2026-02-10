import socket
import threading

HOST = "10.227.93.222"
PORT = 12345

def recv_loop(sock: socket.socket):
    """
    Receive newline-delimited messages and print them.
    """
    buf = b""
    try:
        while True:
            chunk = sock.recv(1024)
            if not chunk:
                print("\n[Server disconnected]")
                break

            buf += chunk
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                msg = line.decode("utf-8", errors="replace")
                print(f"\nServer> {msg}\nYou> ", end="", flush=True)
    except OSError:
        print("\n[Receive loop ended]")

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

if __name__ == "__main__":
    main()