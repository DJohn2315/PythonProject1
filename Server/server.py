import socket
import struct
import threading
import time
import cv2

HOST = "0.0.0.0"
PORT = 12345
DEVICE = "/dev/video1"  # your USB cam node

TYPE_TEXT = b"T"
TYPE_FRAME = b"F"

def send_packet(conn: socket.socket, send_lock: threading.Lock, mtype: bytes, payload: bytes):
    header = mtype + struct.pack("!I", len(payload))
    with send_lock:
        conn.sendall(header)
        conn.sendall(payload)

def recv_exact(conn: socket.socket, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = conn.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("Socket closed")
        buf += chunk
    return buf

def open_camera():
    cap = cv2.VideoCapture(DEVICE, cv2.CAP_V4L2)
    if not cap.isOpened():

        #TODO: Add catch for this error

        raise RuntimeError(f"Could not open {DEVICE}")

    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    for _ in range(30):
        cap.grab()
        time.sleep(0.01)

    ok, frame = cap.read()
    if not ok or frame is None:
        cap.release()
        raise RuntimeError("Camera opened but no frames received.")
    return cap

def camera_send_loop(conn: socket.socket, send_lock: threading.Lock, stop_evt: threading.Event):
    cap = open_camera()
    jpeg_params = [int(cv2.IMWRITE_JPEG_QUALITY), 75]

    try:
        while not stop_evt.is_set():
            ok, frame = cap.read()
            if not ok or frame is None:
                time.sleep(0.01)
                continue

            ok, jpg = cv2.imencode(".jpg", frame, jpeg_params)
            if not ok:
                continue

            try:
                send_packet(conn, send_lock, TYPE_FRAME, jpg.tobytes())
            except (BrokenPipeError, ConnectionResetError, OSError):
                break
    finally:
        cap.release()

def recv_loop(conn: socket.socket, send_lock: threading.Lock, stop_evt: threading.Event):
    # Receives packets from client (mostly text commands/chat)
    try:
        while not stop_evt.is_set():
            mtype = recv_exact(conn, 1)
            (plen,) = struct.unpack("!I", recv_exact(conn, 4))
            payload = recv_exact(conn, plen)

            if mtype == TYPE_TEXT:
                msg = payload.decode("utf-8", errors="replace")
                print(f"Client> {msg}")

                # Example: echo back / ack
                reply = f"ACK: {msg}".encode("utf-8")
                send_packet(conn, send_lock, TYPE_TEXT, reply)

            # If you later send other packet types from client, handle here.
    except (ConnectionError, OSError):
        pass
    finally:
        stop_evt.set()

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
                conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                conn.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

                send_lock = threading.Lock()
                stop_evt = threading.Event()

                t_recv = threading.Thread(target=recv_loop, args=(conn, send_lock, stop_evt), daemon=True)
                t_cam  = threading.Thread(target=camera_send_loop, args=(conn, send_lock, stop_evt), daemon=True)

                t_recv.start()
                t_cam.start()

                # Keep connection alive until something stops
                while not stop_evt.is_set():
                    time.sleep(0.1)

                print("[Disconnected]\n")

if __name__ == "__main__":
    main()
