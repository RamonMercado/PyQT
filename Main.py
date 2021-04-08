from PyQt5 import QtCore, QtGui, QtWidgets
from Test1 import Ui_Screen1
from test import Ui_Screen2
import sys



class Screen_1(QtWidgets.QWidget, Ui_Screen1):

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setupUi(self)

        self.pushButton.clicked.connect(self.pushbutton_handler)

    def pushbutton_handler(self):
        widget.setCurrentIndex(widget.currentIndex()+1)

class Screen_2(QtWidgets.QWidget, Ui_Screen2):

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setupUi(self)

        self.pushButton.clicked.connect(self.pushbutton_handler)

    def pushbutton_handler(self):
        widget.setCurrentIndex(widget.currentIndex() - 1)


app = QtWidgets.QApplication(sys.argv)
widget = QtWidgets.QStackedWidget()
screen1 = Screen_1()
screen2 = Screen_2()
widget.addWidget(screen1)
widget.addWidget(screen2)
widget.setFixedHeight(400)
widget.setFixedWidth(300)
widget.show()
sys.exit(app.exec_())
