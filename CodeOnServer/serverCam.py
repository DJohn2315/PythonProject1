import socket
import struct
import cv2

HOST = "0.0.0.0"
PORT = 12345

def send_all(sock: socket.socket, data: bytes) -> None:
    view = memoryview(data)
    while view:
        n = sock.send(view)
        view = view[n:]

def main():
    # Open camera (usually /dev/video0)
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    if not cap.isOpened():
        raise RuntimeError("Could not open camera /dev/video0 (VideoCapture(0))")

    # Tune these as needed
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 20)

    # JPEG quality: 0-100 (higher = better quality + more bandwidth)
    jpeg_params = [int(cv2.IMWRITE_JPEG_QUALITY), 75]

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"Video server listening on {HOST}:{PORT}")

        conn, addr = s.accept()
        print(f"Client connected from {addr}")

        with conn:
            # Optional: reduce latency (may increase packets)
            conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

            while True:
                ok, frame = cap.read()
                if not ok:
                    print("Camera read failed; stopping.")
                    break

                ok, jpg = cv2.imencode(".jpg", frame, jpeg_params)
                if not ok:
                    continue

                data = jpg.tobytes()
                header = struct.pack("!I", len(data))  # 4-byte big-endian length
                try:
                    send_all(conn, header)
                    send_all(conn, data)
                except (BrokenPipeError, ConnectionResetError):
                    print("Client disconnected.")
                    break

    cap.release()

if __name__ == "__main__":
    main()
