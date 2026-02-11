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
        raise RuntimeError(f"Could not open {DEVICE}")

    # IMPORTANT: request a mode that the camera explicitly supports
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    # Helps reduce latency (may be ignored by driver)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    # Warm-up: let exposure/stream settle
    for _ in range(30):
        cap.grab()
        time.sleep(0.01)

    # Verify we actually get a frame
    ok, frame = cap.read()
    if not ok or frame is None:
        cap.release()
        raise RuntimeError("Camera opened but no frames received. "
                           "Close other camera apps and try again.")

    print("Camera OK: MJPG 640x480 @ 30fps")
    return cap

def main():
    cap = open_camera()

    # Since the camera is already outputting MJPG, OpenCV returns decoded frames.
    # We'll JPEG encode for streaming. (Still fine; CPU usage is modest at 640x480)
    jpeg_params = [int(cv2.IMWRITE_JPEG_QUALITY), 75]

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"Video server listening on {HOST}:{PORT}")

        conn, addr = s.accept()
        print(f"Client connected from {addr}")

        with conn:
            conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

            while True:
                ok, frame = cap.read()
                if not ok or frame is None:
                    # Don’t immediately kill the stream on a transient glitch
                    time.sleep(0.01)
                    continue

                ok, jpg = cv2.imencode(".jpg", frame, jpeg_params)
                if not ok:
                    continue

                payload = jpg.tobytes()
                header = struct.pack("!I", len(payload))

                try:
                    send_all(conn, header)
                    send_all(conn, payload)
                except (BrokenPipeError, ConnectionResetError):
                    print("Client disconnected.")
                    break

    cap.release()

if __name__ == "__main__":
    main()

