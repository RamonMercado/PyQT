import numpy
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

    # Increase the number of measurements
    # Maximum number of measurements is 1000
    def IncreaseNumberOfMeasurements(self):
        if self.numberMeasurements < 1000:
            self.numberMeasurements += 50
            self.NumMeasurments_textBrowser.setText(self.numberMeasurements)

    # Decrease the number of measurements
    # Minimum number of measurements is 50
    def DecreaseNumberOfMeasurements(self):
        if self.numberMeasurements > 50:
            self.numberMeasurements -= 50
            self.NumMeasurments_textBrowser.setText(self.numberMeasurements)

    # Maximum Sweep Time is 10
    # Range 0.05 - 0.25 Increments by 0.05
    # Range 0.25 - 10.0 Increments by 0.25
    def IncreaseSweepTime(self):

        if 0.25 <= self.sweepTime < 10:
            self.sweepTime += 0.25

        elif self.sweepTime < 0.25:
            self.sweepTime += 0.05

        self.sweepTime = numpy.round(self.sweepTime, 2)
        self.sweepTimeLCD.display('%.2f' % self.sweepTime)

    # Minimum Sweep Time is 0.05
    # Range 0.05 - 0.25 Decrease by 0.05
    # Range 0.25 - 10.0 Decrease by 0.25
    def DecreaseSweepTime(self):

        if self.sweepTime > 0.25:
            self.sweepTime -= 0.25

        elif self.sweepTime > 0.05:
            self.sweepTime -= 0.05

        self.sweepTime = numpy.round(self.sweepTime, 2)
        self.sweepTimeLCD.display('%.2f' % self.sweepTime)

    # Returns to main window
    def back_button_handler(self):
        w = widget.currentWidget()
        widget.setCurrentIndex(widget.currentIndex() - 1)
        widget.removeWidget(w)

    # Executes measurement
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
