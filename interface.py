from PySide6 import QtCore, QtWidgets, QtGui

from client import disconnect

class InterfacePage(QtWidgets.QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack

        label = QtWidgets.QLabel(
            f"Robot Interface Loaded",
            alignment=QtCore.Qt.AlignCenter
        )

        disconnect = QtWidgets.QPushButton("Disconnect")

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(label)
        layout.addWidget(disconnect)

        disconnect.clicked.connect(self.disconnect)
    
    def disconnect(self):
        disconnect()
        self.stack.setCurrentIndex(0)
