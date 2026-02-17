from PySide6 import QtCore, QtWidgets

class RobotDataDisplay(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignTop)

        self.labels = {}
    
    def updateLabels(self, robot_data):
        for key, value in robot_data.items():
            if key not in self.labels:
                label = QtWidgets.QLabel(f"{key}: {value}")
                self.labels[key] = label
                self.layout.addWidget(label)
            else:
                self.labels[key].setText(f"{key}: {value}")