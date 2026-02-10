from PySide6 import QtCore, QtWidgets, QtGui

from client import disconnect, send_message, get_message

class InterfacePage(QtWidgets.QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack

        label = QtWidgets.QLabel(
            f"Robot Interface Loaded",
            alignment=QtCore.Qt.AlignCenter
        )

        self.chat_box = QtWidgets.QTextEdit()
        self.chat_box.setReadOnly(True)

        self.message_line = QtWidgets.QLineEdit()
        submit_message = QtWidgets.QPushButton("Send")

        message_row = QtWidgets.QHBoxLayout()
        message_row.addWidget(self.message_line)
        message_row.addWidget(submit_message)

        disconnect = QtWidgets.QPushButton("Disconnect")

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(label)
        layout.addWidget(self.chat_box)
        layout.addLayout(message_row)
        layout.addWidget(disconnect)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.poll_msg)
        self.timer.start(50)

        submit_message.clicked.connect(self.send_msg)
        disconnect.clicked.connect(self.disconnect)
    
    def poll_msg(self):
        for msg in get_message():
            self.chat_box.append(msg)

    def send_msg(self):
        msg = self.message_line.text()

        if not msg.strip():
            return

        send_message(msg)
        self.message_line.clear()

    def disconnect(self):
        disconnect()
        self.stack.setCurrentIndex(0)
