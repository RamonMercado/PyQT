from PyQt5 import QtCore, QtGui, QtWidgets
from GraphScreen import Ui_Graphic_Window
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys


class GraphicScreen(QtWidgets.QMainWindow, Ui_Graphic_Window):

    def __init__(self):
        super(GraphicScreen, self).__init__()
        self.setupUi(self)
        hour = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        temperature = [30, 32, 34, 32, 33, 31, 29, 32, 35, 45]

        self.BackGraph_Btn.clicked.connect(self.BackGraph_Btn_handler)
        self.Graph_Widget.plot(hour, temperature)




    def BackGraph_Btn_handler(self):
        self.close()








if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()
    main_screen = GraphicScreen()
    widget.addWidget(main_screen)
    widget.setFixedHeight(480)
    widget.setFixedWidth(800)
    widget.show()
    sys.exit(app.exec_())
