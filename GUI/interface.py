from PySide6 import QtCore, QtWidgets, QtGui
import cv2
import numpy as np

from Client.client import disconnect, send_message, get_message, get_latest_frame

class InterfacePage(QtWidgets.QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack

        label = QtWidgets.QLabel("Robot Interface Loaded", alignment=QtCore.Qt.AlignCenter)

        # Video display
        self.video_label = QtWidgets.QLabel("No video")
        self.video_label.setAlignment(QtCore.Qt.AlignCenter)
        self.video_label.setMinimumHeight(300)
        self.video_label.setStyleSheet("background: #111; color: #ddd;")

        self.chat_box = QtWidgets.QTextEdit()
        self.chat_box.setReadOnly(True)

        self.message_line = QtWidgets.QLineEdit()
        submit_message = QtWidgets.QPushButton("Send")

        message_row = QtWidgets.QHBoxLayout()
        message_row.addWidget(self.message_line)
        message_row.addWidget(submit_message)

        disconnect_btn = QtWidgets.QPushButton("Disconnect")

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(label)
        layout.addWidget(self.video_label)
        layout.addWidget(self.chat_box)
        layout.addLayout(message_row)
        layout.addWidget(disconnect_btn)

        self._last_frame_ptr = None  # cheap “did frame change?” check

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.poll_updates)
        self.timer.start(30)  # ~33 fps polling (display rate; network rate may be lower)

        submit_message.clicked.connect(self.send_msg)
        disconnect_btn.clicked.connect(self.disconnect)

    def poll_updates(self):
        # Chat messages
        for msg in get_message():
            self.chat_box.append(msg)

        # Video frame
        jpg_bytes = get_latest_frame()
        if not jpg_bytes:
            return

        # Avoid re-decoding identical buffer objects (optional micro-opt)
        if jpg_bytes is self._last_frame_ptr:
            return
        self._last_frame_ptr = jpg_bytes

        arr = np.frombuffer(jpg_bytes, dtype=np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if frame is None:
            return

        # Convert BGR -> RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w

        qimg = QtGui.QImage(frame_rgb.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        pix = QtGui.QPixmap.fromImage(qimg)

        # Fit to label
        pix = pix.scaled(self.video_label.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.video_label.setPixmap(pix)

    def send_msg(self):
        msg = self.message_line.text()
        if not msg.strip():
            return
        send_message(msg)
        self.message_line.clear()

    def disconnect(self):
        disconnect()
        self.stack.setCurrentIndex(0)
