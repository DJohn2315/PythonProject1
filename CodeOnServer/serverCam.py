import socket
import struct
import time
import cv2

HOST = "0.0.0.0"
PORT = 12345
DEVICE = "/dev/video2"  

def send_all(sock: socket.socket, data: bytes) -> None:
    view = memoryview(data)
    while view:
        n = sock.send(view)
        view = view[n:]

def open_camera():
    cap = cv2.VideoCapture(DEVICE, cv2.CAP_V4L2)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera at {DEVICE}")

    # Reduce latency (may or may not be supported)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    # Request a known good mode (adjust based on v4l2-ctl output)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 20)

    # Force MJPG if available (often prevents select() timeouts)
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    cap.set(cv2.CAP_PROP_FOURCC, fourcc)

    # Warm up: many cams return a few empty frames initially
    for _ in range(20):
        cap.grab()
        time.sleep(0.02)

    return cap

def main():
    cap = open_camera()

    jpeg_params = [int(cv2.IMWRITE_JPEG_QUALITY), 75]

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"Video server listening on {HOST}:{PORT} using {DEVICE}")

        conn, addr = s.accept()
        print(f"Client connected from {addr}")

        with conn:
            conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

            consecutive_failures = 0

            while True:
                ok, frame = cap.read()

                if not ok or frame is None:
                    consecutive_failures += 1
                    # Don’t immediately kill everything—retry a bit
                    if consecutive_failures % 10 == 0:
                        print(f"[WARN] Camera read failed {consecutive_failures} times; retrying...")
                    time.sleep(0.05)

                    # If it’s failing for a long time, try reopening the camera
                    if consecutive_failures >= 100:
                        print("[WARN] Reopening camera...")
                        cap.release()
                        time.sleep(0.5)
                        cap = open_camera()
                        consecutive_failures = 0
                    continue

                consecutive_failures = 0

                ok, jpg = cv2.imencode(".jpg", frame, jpeg_params)
                if not ok:
                    continue

                data = jpg.tobytes()
                header = struct.pack("!I", len(data))

                try:
                    send_all(conn, header)
                    send_all(conn, data)
                except (BrokenPipeError, ConnectionResetError):
                    print("Client disconnected.")
                    break

    cap.release()

if __name__ == "__main__":
    main()
