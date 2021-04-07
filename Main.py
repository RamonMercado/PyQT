from PyQt5 import QtCore, QtGui, QtWidgets
from test import Ui_Screen2
from Test1 import Ui_Screen1
import sys

class WindowsController:
    def __init__(self):
        pass

    def showScreen1(self):
        # self.screen1 = Ui_Screen1()
        # self.screen1.show()
        Screen1 = QtWidgets.QMainWindow()
        self.ui = Ui_Screen1()
        self.ui.setupUi(Screen1)
        Screen1.show()




def main():
    app = QtWidgets.QApplication(sys.argv)
    controller = WindowsController()
    controller.showScreen1()

    '''
    app = QtWidgets.QApplication(sys.argv)
    Screen1 = QtWidgets.QMainWindow()
    ui = Ui_Screen1()
    ui.setupUi(Screen1)
    Screen1.show()
    sys.exit(app.exec_())
    '''



if __name__ == "__main__":
  main()