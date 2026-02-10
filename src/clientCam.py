import socket
import struct
import numpy as np
import cv2

HOST = "10.227.93.222"  # Pi IP
PORT = 12345

def recv_exact(sock: socket.socket, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("Socket closed")
        buf += chunk
    return buf

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        print(f"Connected to video server at {HOST}:{PORT}")

        while True:
            # Read 4-byte frame size
            header = recv_exact(s, 4)
            (frame_len,) = struct.unpack("!I", header)

            # Read frame bytes
            frame_bytes = recv_exact(s, frame_len)

            # Decode JPEG -> image
            arr = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if frame is None:
                continue

            cv2.imshow("Pi Camera Stream", frame)

            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
