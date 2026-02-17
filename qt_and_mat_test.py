import sys
import matplotlib
matplotlib.use('Qt5Agg')

from math import sin, cos, radians

from PySide6 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class FieldPlot(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=8, height=4, dpi=100, image_path="Field.png"):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

        self.img_path = image_path
        self.robot_pos = (32.0, 6.0)
        self.robot_dir = radians(180)

        self.robot_radius = 6.0

        self.setup_plot()
    
    def setup_plot(self):
        img = plt.imread(self.img_path)
        self.axes.imshow(img, extent=[0, 96, 0, 48])

        robot = plt.Circle(self.robot_pos, self.robot_radius, color='white')

        dx = 6*cos(self.robot_dir)
        dy = 6*sin(self.robot_dir)

        robot_dir = plt.Arrow(self.robot_pos[0], self.robot_pos[1],
                              dx, dy,
                              width=10, color='black')
        
        self.axes.add_patch(robot)
        self.axes.add_patch(robot_dir)

        

        self.draw()
    
    def update_robot_pos(self, x, y, dir):
        self.robot_pos = (x, y)
        self.robot_dir = radians(dir)
        self.axes.clear()
        self.setup_plot()


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create the maptlotlib FigureCanvas object,
        # which defines a single set of axes as self.axes.
        field = FieldPlot(self, width=5, height=4, dpi=100)
        self.setCentralWidget(field)

        self.show()


app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
app.exec_()