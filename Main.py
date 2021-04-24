import numpy
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
from MainScreen import Ui_Menu_Window
from SensorScreen import Ui_Config_Window
from GraphScreen import Ui_Graphic_Window
from RealTimeScreen import Ui_RealTimeMeasurement_Window
import sys


class MainScreen(QtWidgets.QMainWindow, Ui_Menu_Window):

    def __init__(self):
        super(MainScreen, self).__init__()
        self.setupUi(self)

        # Button actions on click
        self.SLP_Btn.clicked.connect(self.slp_button_handler)
        self.DLP_Btn.clicked.connect(self.dlp_button_handler)
        self.HEA_Btn.clicked.connect(self.hea_button_handler)

    # Creates Sensor Screen for Single Langmuir Probe
    def slp_button_handler(self):
        sensor_screen = SensorScreen('SLP')
        widget.addWidget(sensor_screen)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    # Creates Sensor Screen for Double Langmuir Probe
    def dlp_button_handler(self):
        sensor_screen = SensorScreen('DLP')
        widget.addWidget(sensor_screen)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    # Creates Sensor Screen for Hyperbolic Energy Analyzer
    def hea_button_handler(self):
        sensor_screen = SensorScreen('HEA')
        widget.addWidget(sensor_screen)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class SensorScreen(QtWidgets.QMainWindow, Ui_Config_Window):

    def __init__(self, sensor_name: str):
        super(SensorScreen, self).__init__()
        self.setupUi(self)

        # Initialize invalid voltage range dialog screen
        self.dlg = InvalidVoltageRangeDialogBox()

        # Initialize variables
        self.name = sensor_name
        self.sweepTime = 0
        self.numberMeasurements = 0
        self.minus_voltage = ''
        self.plus_voltage = ''

        if self.name == 'SLP':
            text = "Single Langmuir Probe"
        elif self.name == 'DLP':
            text = 'Double Langmuir Probe'
        elif self.name == 'HEA':
            text = 'Hyperbolic Energy Analyzer'

        # Set label text to name of probe chosen
        self.ProbeName_label.setText(text)

        # Button actions on click
        self.Back_Btn.clicked.connect(self.back_button_handler)
        self.Run_Btn.clicked.connect(self.run_button_handler)
        self.Graph_Btn.clicked.connect(self.graph_button_handler)
        self.DownVolt_Btn.clicked.connect(self.decrease_sweep_time)
        self.UpVolt_Btn.clicked.connect(self.increase_sweep_time)
        self.UpNumberMeasurements_Btn.clicked.connect(self.increase_number_of_measurements)
        self.DownNumberMeasurements_Btn.clicked.connect(self.decrease_number_of_measurements)

    # Increase the number of measurements
    # Maximum number of measurements is 1000
    def increase_number_of_measurements(self):
        if self.numberMeasurements < 1000:
            self.numberMeasurements += 50
            self.NumberMeasurements_Lcd.display(self.numberMeasurements)

    # Decrease the number of measurements
    # Minimum number of measurements is 50
    def decrease_number_of_measurements(self):
        if self.numberMeasurements > 50:
            self.numberMeasurements -= 50
            self.NumberMeasurements_Lcd.display(self.numberMeasurements)

    # Maximum Sweep Time is 10
    # Range 0.05 - 0.25 Increments by 0.05
    # Range 0.25 - 10.0 Increments by 0.25
    def increase_sweep_time(self):

        if 0.25 <= self.sweepTime < 10:
            self.sweepTime += 0.25

        elif self.sweepTime < 0.25:
            self.sweepTime += 0.05

        self.sweepTime = numpy.round(self.sweepTime, 2)
        self.VoltageSweepTimes_Lcd.display('%.2f' % self.sweepTime)

    # Minimum Sweep Time is 0.05
    # Range 0.05 - 0.25 Decrease by 0.05
    # Range 0.25 - 10.0 Decrease by 0.25
    def decrease_sweep_time(self):

        if self.sweepTime > 0.25:
            self.sweepTime -= 0.25

        elif self.sweepTime > 0.05:
            self.sweepTime -= 0.05

        self.sweepTime = numpy.round(self.sweepTime, 2)
        self.VoltageSweepTimes_Lcd.display('%.2f' % self.sweepTime)

    def back_button_handler(self):
        w = widget.currentWidget()
        widget.setCurrentIndex(widget.currentIndex() - 1)
        widget.removeWidget(w)

    # Displays Real Time Screen
    def run_button_handler(self):
        self.minus_voltage = self.VoltageRangeMinus_comboBox.currentText()
        self.plus_voltage = self.VoltageRangePlus_comboBox.currentText()

        # If either are empty or both are 0 show invalid voltage range dialog
        if (self.minus_voltage == '' or self.plus_voltage == '') or \
           (self.minus_voltage == '0' and self.plus_voltage == '0'):
            self.dlg.exec_()

        # Else create real time and graph screen
        # Go to real time screen
        else:
            real_time_screen = RealTimeScreen()
            graph_screen = GraphicScreen()
            widget.addWidget(real_time_screen)
            widget.addWidget(graph_screen)
            widget.setCurrentIndex(widget.currentIndex() + 1)

    # Displays Graph Screen
    def graph_button_handler(self):
        graph_screen = GraphicScreen()
        widget.addWidget(graph_screen)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class RealTimeScreen(QtWidgets.QMainWindow, Ui_RealTimeMeasurement_Window):

    def __init__(self):
        super(RealTimeScreen, self).__init__()
        self.setupUi(self)

        # Hide Run button on startup
        self.RealTimeRun_Btn.hide()

        # Button actions on click
        # self.RealTimeRun_Btn.clicked.connect(self.run_button_handler)
        self.Stop_Btn.clicked.connect(self.stop_button_handler)

    # Starts graph generation? Correct me on this
    def run_button_handler(self):
        self.RealTimeRun_Btn.hide()
        # Start Measurements
        self.Stop_Btn.show()

    # Stops graph generation
    def stop_button_handler(self):
        # Stop Measurements
        pass

    def graph_button_handler(self):
        widget.setCurrentIndex(widget.currentIndex() + 1)


class GraphicScreen(QtWidgets.QMainWindow, Ui_Graphic_Window):

    def __init__(self):
        super(GraphicScreen, self).__init__()
        self.setupUi(self)

        # Test values
        hour = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        temperature = [30, 32, 34, 32, 33, 31, 29, 32, 35, 45]

        # Button action on click
        self.BackGraph_Btn.clicked.connect(self.back_button_handler)

        # Set Graph Styling
        self.Graph_Widget.setBackground('w')
        pen = pg.mkPen(color=(255, 0, 0))  # (255, 0, 0) is red
        self.Graph_Widget.setTitle('<span style=\"color:black;font-size:20pt\">Voltage vs Current Characteristic</span>')
        self.Graph_Widget.setLabel('left', '<span style=\"color:black;font-size:20px\">Current (I)</span>')
        self.Graph_Widget.setLabel('bottom', '<span style=\"color:black;font-size:20px\">Voltage (V)</span>')

        # PLot graph from values
        self.Graph_Widget.plot(hour, temperature, pen=pen)


    def back_button_handler(self):
        widget.setCurrentIndex(widget.currentIndex() - 1)

class InvalidVoltageRangeDialogBox(QtWidgets.QDialog):
    def __init__(self):
        super(InvalidVoltageRangeDialogBox, self).__init__()

        # Set title on window
        self.setWindowTitle('Invalid Voltage Range!')

        # Set buttons to include in dialog box
        # Set Ok button
        q_btn = QtWidgets.QDialogButtonBox.Ok

        # Add button to button box
        self.buttonBox = QtWidgets.QDialogButtonBox(q_btn)
        self.buttonBox.accepted.connect(self.accept)

        # Initialize Layout
        self.layout = QtWidgets.QVBoxLayout()

        # Set Message included in dialog box
        message = QtWidgets.QLabel('Please choose a valid voltage range')

        # Add message and buttons to layout
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)

        # Set layout
        self.setLayout(self.layout)

        # Set fixed size
        self.setFixedWidth(300)
        self.setFixedHeight(100)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()
    main_screen = MainScreen()
    widget.addWidget(main_screen)
    widget.setFixedHeight(480)
    widget.setFixedWidth(800)
    widget.show()
    sys.exit(app.exec_())
