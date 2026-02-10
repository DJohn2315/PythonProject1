import socket

def connect_client(ip, port=8080):
    s = socket.socket()
    try:
        
        s.connect((ip, port))

        print(s.recv(1024).decode())
        return f"{s.recv(1024).decode()}"
        
    except Exception as e:
        print(e)
        return f"Error: {e}"
    s.close()