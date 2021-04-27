import threading
import numpy
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
from MenuScreen import Ui_Menu_Window
from SensorScreen import Ui_Config_Window
from GraphScreen import Ui_Graphic_Window
from RealTimeScreen import Ui_RealTimeMeasurement_Window
from HistoryScreen import Ui_HistoryScreen
from plasma_meter import run_example, server
from plasma_meter.server import DataServer
from plasma_meter.database import DatabaseManager
import sys


class MainScreen(QtWidgets.QMainWindow, Ui_Menu_Window):

    def __init__(self):
        super(MainScreen, self).__init__()
        self.setupUi(self)

        # Button actions on click
        self.SLP_Btn.clicked.connect(self.slp_button_handler)
        self.DLP_Btn.clicked.connect(self.dlp_button_handler)
        self.HEA_Btn.clicked.connect(self.hea_button_handler)
        self.History_Btn.clicked.connect(self.history_button_handler)

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

    # Shows History Screen
    def history_button_handler(self):
        history_screen = HistoryScreen()
        widget.addWidget(history_screen)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class SensorScreen(QtWidgets.QMainWindow, Ui_Config_Window):

    def __init__(self, sensor_name: str):
        super(SensorScreen, self).__init__()
        self.setupUi(self)

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

            # Initialize invalid voltage range dialog screen
            self.dlg = InvalidParameterDialogBox('Voltage Range')
            self.dlg.exec_()

        elif self.VoltageSweepTimes_Lcd.value() == 0:

            # Initialize invalid voltage sweep time dialog screen
            self.dlg = InvalidParameterDialogBox('Sweep Time')
            self.dlg.exec_()

        elif self.NumberMeasurements_Lcd.value() == 0:

            # Initialize invalid number of measurements dialog screen
            self.dlg = InvalidParameterDialogBox('Number of Measurements')
            self.dlg.exec_()

        # Else create real time and graph screen
        # Go to real time screen
        else:
            self.Worker1 = Worker1()
            self.Worker1.start()
            real_time_screen = RealTimeScreen(self.Worker1)
            graph_screen = GraphicScreen(self.Worker1)
            widget.addWidget(real_time_screen)
            widget.addWidget(graph_screen)
            widget.setCurrentIndex(widget.currentIndex() + 1)


class RealTimeScreen(QtWidgets.QMainWindow, Ui_RealTimeMeasurement_Window):
    #  voltage_range, voltage_sweep_time, number_of_measurements, sensor_to_use, gas
    def __init__(self, worker):
        super(RealTimeScreen, self).__init__()
        self.setupUi(self)

        # Run measurement

        worker.real_time_value_update.connect(self.values_update)

        # Button actions on click
        # self.RealTimeRun_Btn.clicked.connect(self.run_button_handler)
        self.Back_Btn.clicked.connect(self.back_button_handler)
        self.Graph_Btn.clicked.connect(self.graph_button_handler)

    # Starts graph generation? Correct me on this
    def run_button_handler(self):
        self.RealTimeRun_Btn.hide()
        # Start Measurements
        self.Stop_Btn.show()

    # Stops graph generation
    def back_button_handler(self):
        #Stop measurements
        w1 = widget.currentWidget()
        w2 = widget.widget(widget.currentIndex() + 1)
        widget.setCurrentIndex(widget.currentIndex() - 1)
        widget.removeWidget(w2)
        widget.removeWidget(w1)


    def graph_button_handler(self):
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def values_update(self, debye_length, density, lamor_radius, temperature_ev, mean_free_path, temperature, plasma_potential, floating_potential):
        self.DebeyLength_ValueLCD.display('%.2f' % debye_length)
        self.Density_ValueLCD.display('%.2f' % density)
        self.LarmorRadius_ValueLCD.display('%.2f' % lamor_radius)
        self.KTe_eV_ValueLCD.display('%.2f' % temperature_ev)
        self.MeanFreePath_ValueLCD.display('%.2f' % mean_free_path)
        self.KTe_ValueLCD.display('%.2f' % temperature)
        self.PlasmaPotential_ValueLCD.display('%.2f' % plasma_potential)
        self.FloatingPotential_ValueLCD.display('%.2f' % floating_potential)


class GraphicScreen(QtWidgets.QMainWindow, Ui_Graphic_Window):

    def __init__(self, worker):
        super(GraphicScreen, self).__init__()
        self.setupUi(self)

        worker.graph_update.connect(self.graph_update)
        # Test values
        hour = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        temperature = [30, 32, 34, 32, 33, 31, 29, 32, 35, 45]

        # Button action on click
        self.BackGraph_Btn.clicked.connect(self.back_button_handler)

        # Set Graph Styling
        self.Graph_Widget.setBackground('w')

        self.Graph_Widget.setTitle('<span style=\"color:black;font-size:20pt\">Voltage vs Current Characteristic</span>')
        self.Graph_Widget.setLabel('left', '<span style=\"color:black;font-size:20px\">Current (I)</span>')
        self.Graph_Widget.setLabel('bottom', '<span style=\"color:black;font-size:20px\">Voltage (V)</span>')
        self.Graph_Widget.showGrid(x=True, y=True)

    def back_button_handler(self):
        widget.setCurrentIndex(widget.currentIndex() - 1)

    def graph_update(self, voltage_list, current_list):
        # PLot graph from values
        pen = pg.mkPen(color=(255, 0, 0))  # (255, 0, 0) is red
        self.Graph_Widget.plot(voltage_list[:len(current_list)], current_list, pen=pen)


class HistoryScreen(QtWidgets.QMainWindow, Ui_HistoryScreen):
    def __init__(self):
        super(HistoryScreen, self).__init__()
        self.setupUi(self)

        self.Back_Btn.clicked.connect(self.back_button_handler)
        self.Filter_Combobox.currentTextChanged.connect(self.display_data)
        self.db = DatabaseManager()
        self.display_data()

    def display_data(self):
        if self.Filter_Combobox.currentText() == 'All':
            self.display_all_measurements()

        elif self.Filter_Combobox.currentText() == 'SLP':
            self.display_slp_measurements()

        elif self.Filter_Combobox.currentText() == 'DLP':
            self.display_dlp_measurements()

        elif self.Filter_Combobox.currentText() == 'HEA':
            self.display_hea_measurements()

    def back_button_handler(self):
        w = widget.currentWidget()
        widget.setCurrentIndex(widget.currentIndex() - 1)
        widget.removeWidget(w)

    def display_all_measurements(self):

        self.Single_History_TableWidget.hide()
        results = self.db.get_all_measurements()

        self.All_History_TableWidget.setRowCount(0)
        for row_number, row_data in enumerate(results):
            self.All_History_TableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.All_History_TableWidget.setItem(row_number, column_number,
                                                     QtWidgets.QTableWidgetItem(str(row_data[data])))

        for i in range(self.All_History_TableWidget.columnCount()):
            self.All_History_TableWidget.resizeColumnToContents(i)

        self.All_History_TableWidget.show()

    def display_slp_measurements(self):

        self.All_History_TableWidget.hide()
        results = self.db.get_all_SLP_measurements()

        self.Single_History_TableWidget.setRowCount(0)
        for row_number, row_data in enumerate(results):
            self.Single_History_TableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.Single_History_TableWidget.setItem(row_number, column_number,
                                                     QtWidgets.QTableWidgetItem(str(row_data[data])))

        for i in range(self.All_History_TableWidget.columnCount()):
            self.Single_History_TableWidget.resizeColumnToContents(i)

        self.Single_History_TableWidget.show()

    def display_dlp_measurements(self):
        # self.All_History_TableWidget.hide()
        # results = self.db.get_all_DLP_measurements()
        #
        # self.Single_History_TableWidget.setRowCount(0)
        # for row_number, row_data in enumerate(results):
        #     self.Single_History_TableWidget.insertRow(row_number)
        #     for column_number, data in enumerate(row_data):
        #         self.Single_History_TableWidget.setItem(row_number, column_number,
        #                                                 QtWidgets.QTableWidgetItem(str(row_data[data])))
        #
        # for i in range(self.All_History_TableWidget.columnCount()):
        #     self.Single_History_TableWidget.resizeColumnToContents(i)
        #
        # self.Single_History_TableWidget.show()
        pass

    def display_hea_measurements(self):
        # self.All_History_TableWidget.hide()
        # results = self.db.get_all_HEA_measurements()
        #
        # self.Single_History_TableWidget.setRowCount(0)
        # for row_number, row_data in enumerate(results):
        #     self.Single_History_TableWidget.insertRow(row_number)
        #     for column_number, data in enumerate(row_data):
        #         self.Single_History_TableWidget.setItem(row_number, column_number,
        #                                                 QtWidgets.QTableWidgetItem(str(row_data[data])))
        #
        # for i in range(self.All_History_TableWidget.columnCount()):
        #     self.Single_History_TableWidget.resizeColumnToContents(i)
        #
        # self.Single_History_TableWidget.show()
        pass

class InvalidParameterDialogBox(QtWidgets.QDialog):
    def __init__(self, error_type):
        super(InvalidParameterDialogBox, self).__init__()

        if error_type == 'Voltage Range':
            self.title = 'Invalid Voltage Range!'
            self.message = 'Please choose a valid voltage range'

        elif error_type == 'Number of Measurements':
            self.title = 'Invalid Number of Measurements!'
            self.message = 'Please choose a valid number of measurements'

        elif error_type == 'Sweep Time':
            self.title = 'Invalid Voltage Sweep Time!'
            self.message = 'Please choose a valid voltage sweep time'

        # Set title on window
        self.setWindowTitle(self.title)

        # Set buttons to include in dialog box
        # Set Ok button
        q_btn = QtWidgets.QDialogButtonBox.Ok

        # Add button to button box
        self.buttonBox = QtWidgets.QDialogButtonBox(q_btn)
        self.buttonBox.accepted.connect(self.accept)

        # Initialize Layout
        self.layout = QtWidgets.QVBoxLayout()

        # Set Message included in dialog box
        box_message = QtWidgets.QLabel(self.message)

        # Add message and buttons to layout
        self.layout.addWidget(box_message)
        self.layout.addWidget(self.buttonBox)

        # Set layout
        self.setLayout(self.layout)

        # Set fixed size
        self.setFixedWidth(400)
        self.setFixedHeight(100)


class Worker1(QtCore.QThread):
    real_time_value_update = QtCore.pyqtSignal(float, float, float, float, float, float, float, float)
    graph_update = QtCore.pyqtSignal(list, list)

    def run(self):
        run_example.run_in_separate_thread([-300, 300], .5, 500, 'SLP', 'Air',
                                           self.real_time_value_update, self.graph_update)
        self.quit()


def run_server():
    """
    Runs plasma server indefinitely
    :return: None
    """
    data_server = DataServer()
    data_server.start_server_task()

if __name__ == '__main__':
    # making server thread
    server = threading.Thread(target=run_server)
    server.start()

    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()
    main_screen = MainScreen()
    widget.addWidget(main_screen)
    widget.setFixedHeight(480)
    widget.setFixedWidth(800)
    widget.show()
    sys.exit(app.exec_())
