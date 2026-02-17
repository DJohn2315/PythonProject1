from PySide6 import QtCore, QtWidgets, QtGui
import cv2
import numpy as np

from map_plotting import FieldPlot
from robot_data_display import RobotDataDisplay
from client import disconnect, send_message, get_message, get_latest_frame, send_command, get_latest_position, get_latest_robot_data

class InterfacePage(QtWidgets.QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack

        label = QtWidgets.QLabel("Robot Interface Loaded", alignment=QtCore.Qt.AlignCenter)

        self.robot_data = {}

        # Field Plot
        self.field = FieldPlot(self)

        # Video display
        self.video_label = QtWidgets.QLabel("No video")
        self.video_label.setAlignment(QtCore.Qt.AlignCenter)
        self.video_label.setMinimumHeight(300)
        self.video_label.setStyleSheet("background: #111; color: #ddd;")

        # Field and Camera Feed Row
        field_and_cam_row = QtWidgets.QHBoxLayout()
        field_and_cam_row.addWidget(self.field, 1)
        field_and_cam_row.addWidget(self.video_label, 1)

        # Robot Data Display
        self.robot_data_display = RobotDataDisplay(self)

        # Robot Controls
        start_sm = QtWidgets.QPushButton("Start")
        stop_sm = QtWidgets.QPushButton("Stop")
        pause_sm = QtWidgets.QPushButton("Pause")
        resume_sm = QtWidgets.QPushButton("Resume")
        disconnect_btn = QtWidgets.QPushButton("Disconnect")

        start_stop_row = QtWidgets.QHBoxLayout()
        start_stop_row.addWidget(start_sm)
        start_stop_row.addWidget(stop_sm)

        pause_resume_row = QtWidgets.QHBoxLayout()
        pause_resume_row.addWidget(pause_sm)
        pause_resume_row.addWidget(resume_sm)

        control_buttons = QtWidgets.QVBoxLayout()
        control_buttons.addLayout(start_stop_row)
        control_buttons.addLayout(pause_resume_row)

        # Chat Commands
        self.chat_box = QtWidgets.QTextEdit()
        self.chat_box.setReadOnly(True)

        self.message_line = QtWidgets.QLineEdit()
        submit_message = QtWidgets.QPushButton("Send")

        message_row = QtWidgets.QHBoxLayout()
        message_row.addWidget(self.message_line)
        message_row.addWidget(submit_message)

        text_comm = QtWidgets.QVBoxLayout()
        text_comm.addWidget(self.chat_box)
        text_comm.addLayout(message_row)
    
        # Controls Layout
        controls_layout = QtWidgets.QHBoxLayout()
        controls_layout.addLayout(control_buttons)
        controls_layout.addLayout(text_comm)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(label)
        layout.addLayout(field_and_cam_row)
        layout.addWidget(self.robot_data_display)
        layout.addLayout(controls_layout)
        layout.addWidget(disconnect_btn)

        self._last_frame_ptr = None  # cheap “did frame change?” check
        self._last_position = None
        self._last_robot_data = None

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.poll_updates)
        self.timer.start(30)  # ~33 fps polling (display rate; network rate may be lower)

        start_sm.clicked.connect(lambda: self.send_msg_button("START"))
        stop_sm.clicked.connect(lambda: self.send_msg_button("STOP"))
        pause_sm.clicked.connect(lambda: self.send_msg_button("PAUSE"))
        resume_sm.clicked.connect(lambda: self.send_msg_button("RESUME"))

        submit_message.clicked.connect(self.send_msg)
        disconnect_btn.clicked.connect(self.disconnect)

    def poll_updates(self):
        # Chat messages
        for msg in get_message():
            self.chat_box.append(msg)

        # Position updates
        position = get_latest_position()
        if position and position != self._last_position:
            print(f"position: {position['y']}")
            print("Updating Field POS")
            self._last_position = position.copy()
            self.field.update_robot_pos(position['x'], position['y'], position['degrees'])

        # Robot Data updates
        new_rdata = get_latest_robot_data()
        if new_rdata and new_rdata != self._last_robot_data:
            self._last_robot_data = new_rdata.copy()
            for key in new_rdata:
                if key in self.robot_data:
                    print(f"Key {key} already in dict")
                    if self.robot_data[key] != new_rdata[key]:
                        print(f"Updated {key} with new value {new_rdata[key]}")
                        self.robot_data[key] = new_rdata[key]
                else:
                    print(f"Creating new key, {key}, with value {new_rdata[key]}")
                    self.robot_data[key] = new_rdata[key]
            self.robot_data_display.updateLabels(self.robot_data)
            print(f"new_rdata: {self.robot_data}")

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
        send_command(msg)
        self.message_line.clear()
    
    def send_msg_button(self, textin):
        msg = textin
        send_command(msg)

    def disconnect(self):
        disconnect()
        self.stack.setCurrentIndex(0)
