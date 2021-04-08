from PyQt5 import QtCore, QtGui, QtWidgets
from test import Ui_Screen2
from Test1 import Ui_Screen1
import sys

class Screen_1(QtWidgets.QWidget, Ui_Screen1):
    switch_window = QtCore.pyqtSignal()

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setupUi(self)

        self.pushButton.clicked.connect(self.pushbutton_handler)

    def pushbutton_handler(self):
        self.switch_window.emit()
