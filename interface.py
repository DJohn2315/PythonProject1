from PySide6 import QtCore, QtWidgets, QtGui


class InterfacePage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        label = QtWidgets.QLabel(
            "Robot Interface Loaded",
            alignment=QtCore.Qt.AlignCenter
        )

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(label)
