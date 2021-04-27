# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GraphScreen.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Graphic_Window(object):
    def setupUi(self, Graphic_Window):
        Graphic_Window.setObjectName("Graphic_Window")
        Graphic_Window.resize(800, 480)
        Graphic_Window.setMinimumSize(QtCore.QSize(800, 480))
        Graphic_Window.setMaximumSize(QtCore.QSize(800, 480))
        Graphic_Window.setStyleSheet("background-color: rgb(0, 85, 127);\n"
"")
        self.centralwidget = QtWidgets.QWidget(Graphic_Window)
        self.centralwidget.setObjectName("centralwidget")
        self.Graph_Widget = PlotWidget(self.centralwidget)
        self.Graph_Widget.setGeometry(QtCore.QRect(30, 30, 741, 361))
        self.Graph_Widget.setObjectName("Graph_Widget")
        self.BackGraph_Btn = QtWidgets.QPushButton(self.centralwidget)
        self.BackGraph_Btn.setGeometry(QtCore.QRect(340, 410, 111, 41))
        font = QtGui.QFont()
        font.setFamily("Rockwell")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.BackGraph_Btn.setFont(font)
        self.BackGraph_Btn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.BackGraph_Btn.setStyleSheet(" background-color: rgb(236, 70, 70);\n"
"color: rgb(255, 255, 255);")
        self.BackGraph_Btn.setObjectName("BackGraph_Btn")
        Graphic_Window.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(Graphic_Window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        Graphic_Window.setMenuBar(self.menubar)

        self.retranslateUi(Graphic_Window)
        QtCore.QMetaObject.connectSlotsByName(Graphic_Window)

    def retranslateUi(self, Graphic_Window):
        _translate = QtCore.QCoreApplication.translate
        Graphic_Window.setWindowTitle(_translate("Graphic_Window", "MainWindow"))
        self.BackGraph_Btn.setText(_translate("Graphic_Window", "Back"))
from pyqtgraph import PlotWidget


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Graphic_Window = QtWidgets.QMainWindow()
    ui = Ui_Graphic_Window()
    ui.setupUi(Graphic_Window)
    Graphic_Window.show()
    sys.exit(app.exec_())
