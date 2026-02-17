import socket
import struct
import threading
import time
import cv2
import json

import sys
sys.path.insert(1, '../../capstone_project_S26')
from game import StateMachine
from StateControllers import State, Command, StateController, ClientController


HOST = "0.0.0.0"
PORT = 12345
DEVICE = "/dev/video0"  # your USB cam node

TYPE_TEXT = b"T"
TYPE_FRAME = b"F"
TYPE_COMMAND = b"C"

state_controller = None

# GAME CONTROLS
def game_thread(conn: socket.socket, send_lock: threading.Lock, stop_evt: threading.Event):
    global state_controller
    
    try:
        sm = StateMachine(state_controller)
        sm.run()
    except Exception as e:
        print(f"Game Thread Error: {e}")
    finally:
        stop_evt.set()

# SERVER COMM CONTROLS

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
    global state_controller
    
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
            
            elif mtype == TYPE_COMMAND:
                try:
                    cmd_data = json.loads(payload.decode("utf-8"))
                    command = cmd_data.get("command")
                    data = cmd_data.get("data")

                    print(f"COMMAND Received: {command} (data: {data})")

                    if command == "GOTO_STATE" and data:
                        try:
                            data = State[data]
                        except KeyError:
                            raise ValueError(f"Invalid State Name: {data}")

                    response = {"status": "ok", "message": f"Command {command} processed!"}

                    cmd_enum = Command(command)
                    state_controller.handle_command(cmd_enum, data)

                    response_payload =  json.dumps(response).encode("utf-8")
                    send_packet(conn, send_lock, TYPE_COMMAND, response_payload)

                except json.JSONDecodeError as e:
                    error_response = json.dumps({
                        "status": "error",
                        "message": f"Invalid JSON: {e}"
                    }).encode("utf-8")
                    send_packet(conn, send_lock, TYPE_COMMAND, error_response)

                except (ValueError, KeyError) as e:
                    error_response = json.dumps({
                        "status": "error",
                        "message": str(e)
                    }).encode("utf-8")
                    send_packet(conn, send_lock, TYPE_COMMAND, error_response)

                except Exception as e:
                    print(f"Command error: {e}")
                    error_response = json.dumps({
                        "status": "error",
                        "message": str(e)
                    }).encode("utf-8")
                    send_packet(conn, send_lock, TYPE_COMMAND, error_response)


            # If you later send other packet types from client, handle here.
    except (ConnectionError, OSError):
        pass
    finally:
        stop_evt.set()

def main():
    global state_controller

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"Server listening on {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            print(f"Connected by {addr}")

            state_controller = ClientController()

            with conn:
                conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                conn.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

                send_lock = threading.Lock()
                stop_evt = threading.Event()

                print("t")
                t_recv = threading.Thread(target=recv_loop, args=(conn, send_lock, stop_evt), daemon=True)
                t_cam  = threading.Thread(target=camera_send_loop, args=(conn, send_lock, stop_evt), daemon=True)
                t_game = threading.Thread(target=game_thread, args=(conn, send_lock, stop_evt), daemon=True)

                t_recv.start()
                t_cam.start()
                t_game.start()

                # Keep connection alive until something stops
                while not stop_evt.is_set():
                    time.sleep(0.1)

                print("[Disconnected]\n")

if __name__ == "__main__":
    main()
