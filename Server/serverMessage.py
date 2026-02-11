import socket
import threading

HOST = "0.0.0.0"
PORT = 12345

def recv_loop(conn: socket.socket):
    buf = b""
    try:
        while True:
            chunk = conn.recv(1024)
            if not chunk:
                print("\n[Client disconnected]")
                break

            buf += chunk
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                msg = line.decode("utf-8", errors="replace")
                print(f"\nClient> {msg}\nYou> ", end="", flush=True)
    except OSError:
        print("\n[Receive loop ended]")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"Server listening on {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            print(f"Connected by {addr}")

            with conn:
                # Optional: keepalive helps detect dead peers on some networks
                conn.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

                t = threading.Thread(target=recv_loop, args=(conn,), daemon=True)
                t.start()

                try:
                    while True:
                        msg = input("You> ")
                        if msg.lower() in ("quit", "exit"):
                            print("[Closing connection]")
                            break
                        conn.sendall((msg + "\n").encode("utf-8"))
                except (BrokenPipeError, ConnectionResetError):
                    print("\n[Client connection lost]")
                finally:
                    try:
                        conn.shutdown(socket.SHUT_RDWR)
                    except OSError:
                        pass
                    # conn closes automatically by "with conn"
                    print("[Disconnected]\n")

if __name__ == "__main__":
    main()
