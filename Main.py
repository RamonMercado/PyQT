from PyQt5 import QtCore, QtGui, QtWidgets
from MainScreen import Ui_Menu_Window
from SensorScreen import Ui_Config_Window
import sys


class MainScreen(QtWidgets.QMainWindow, Ui_Menu_Window):

    def __init__(self):
        super(MainScreen, self).__init__()
        self.setupUi(self)
        self.SLP_Btn.clicked.connect(self.slp_button_handler)
        self.DLP_Btn.clicked.connect(self.dlp_button_handler)
        self.HEA_Btn.clicked.connect(self.hea_button_handler)

    def slp_button_handler(self):
        sensor_screen = SensorScreen('SLP')
        widget.addWidget(sensor_screen)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def dlp_button_handler(self):
        sensor_screen = SensorScreen('DLP')
        widget.addWidget(sensor_screen)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def hea_button_handler(self):
        sensor_screen = SensorScreen('HEA')
        widget.addWidget(sensor_screen)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class SensorScreen(QtWidgets.QMainWindow, Ui_Config_Window):

    def __init__(self, sensor_name):
        super(SensorScreen, self).__init__()
        self.name = sensor_name
        self.setupUi(self)

        if self.name == 'SLP':
            text = "Single Langmuir Probe"
        elif self.name == 'DLP':
            text = 'Double Langmuir Probe'
        elif self.name == 'HEA':
            text = 'Hyperbolic Energy Analyzer'

        self.ProbeName_label.setText(text)

        self.Back_Btn.clicked.connect(self.back_button_handler)
        self.Run_Btn.clicked.connect(self.run_button_handler)

    def back_button_handler(self):
        w = widget.currentWidget()
        widget.setCurrentIndex(widget.currentIndex() - 1)
        widget.removeWidget(w)

    def run_button_handler(self):
        pass


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()
    main_screen = MainScreen()
    widget.addWidget(main_screen)
    widget.setFixedHeight(480)
    widget.setFixedWidth(800)
    widget.show()
    sys.exit(app.exec_())
