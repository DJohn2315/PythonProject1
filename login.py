import sys
import ipaddress
from PySide6 import QtCore, QtWidgets

from Client.client import connect

class LoginPage(QtWidgets.QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack

        self.text = QtWidgets.QLabel(
            "Enter Robot IP",
            alignment=QtCore.Qt.AlignCenter
        )

        self.ip_enter = QtWidgets.QLineEdit()
        self.ip_enter.setPlaceholderText("192.168.1.10")

        self.button = QtWidgets.QPushButton("Connect")

        self.error = QtWidgets.QLabel(
            "",
            alignment=QtCore.Qt.AlignCenter
        )
        self.error.setStyleSheet("color: red")

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.text)
        layout.addWidget(self.ip_enter)
        layout.addWidget(self.button)
        layout.addWidget(self.error)

        self.button.clicked.connect(self.connect)

    @QtCore.Slot()
    def connect(self):
        ip_text = self.ip_enter.text()

        try:
            ipaddress.ip_address(ip_text)
            connection = connect(ip_text)

            if "Error" in connection:
                self.error.setText(connection)
            if "Connection Successful" in connection:
                self.stack.setCurrentIndex(1)
        except ValueError:
            self.error.setText("Invalid IP address")
