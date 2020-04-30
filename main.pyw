from PyQt5 import QtCore, QtGui, QtWidgets
import serial, time
from sa2005 import Ui_MainWindow
import serial.tools.list_ports

class Window(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.setupUi(self)
        
        # connect buttons defined in sa2005.py to methods
        self.button_hot_open.clicked.connect(self.hot_open)
        self.button_hot_closed.clicked.connect(self.hot_closed)
        self.button_neutral_open.clicked.connect(self.neutral_open)
        self.button_neutral_closed.clicked.connect(self.neutral_closed)
        self.button_ground_closed.clicked.connect(self.ground_closed)
        self.button_ground_open.clicked.connect(self.ground_open)
        self.button_polarity_rev.clicked.connect(self.polarity_rev)
        self.button_polarity_fwd.clicked.connect(self.polarity_fwd)
        self.button_mains_voltage.clicked.connect(self.meas_mains_voltage)
        self.button_device_current.clicked.connect(self.meas_device_current)
        self.button_earth_resistance.clicked.connect(self.meas_earth_resistance)
        self.button_earth_ground.clicked.connect(self.meas_earth_ground)
        self.button_enclosure.clicked.connect(self.meas_enclosure)
        self.button_lead_to_earth.clicked.connect(self.meas_lead_to_earth)
        self.button_lead_to_lead.clicked.connect(self.meas_lead_to_lead)
        self.button_lead_isolation.clicked.connect(self.meas_lead_isolation)
        self.button_external.clicked.connect(self.meas_external)
        self.button_console_clear.clicked.connect(self.clear_log)
        self.button_port_connect.clicked.connect(self.com_connect)
        self.button_port_refresh.clicked.connect(self.com_refresh)
        
        # set LCD timer update interval, should be non-blocking
        self.lcd_timer = QtCore.QTimer()
        self.lcd_timer.timeout.connect(self.lcd_update)

        # connection status
        self.ser = None
        self.com_port = ''
        
        # lock control panel until connected
        self.main_control_frame.setDisabled(True)
        
        # perform an initial port check
        self.com_refresh()
        
    # populate port combo box
    def com_refresh(self):
        self.port_combo_box.clear()
        self.available_ports = serial.tools.list_ports.comports()
        for i in self.available_ports:
            self.port_combo_box.addItem(i.device)  
        com_count = self.port_combo_box.count()
        if(com_count == 0):
            self.append_log("No available COM ports found! Check the connections and click refresh.")
        else: 
            self.append_log("Found " + str(com_count) + " ports available.")
            
    # connect to com port
    def com_connect(self):
        if(self.ser == None):
            self.com_port = self.port_combo_box.currentText()
            if(self.com_port == ''):
                self.append_log("No COM port selected!")
                return
            try:
                self.ser = serial.Serial(self.com_port, 115200)
                self.lcd_timer.start(3000)
                self.port_combo_box.setDisabled(True)
                self.button_port_refresh.setDisabled(True)
                self.main_control_frame.setDisabled(False)
                self.button_port_connect.setText("Disconnect")
                self.setWindowTitle("SA-2005 Control Panel - *" + self.com_port)
                self.append_log("Connected to " + self.com_port + ".")
            except Exception as e:
                self.append_log("Error connecting to serial port")
                self.com_port = ''
                error_message = QtWidgets.QMessageBox()
                error_message.setWindowTitle("Connection Error")
                error_message.setText(str(e))
                error_message.exec_()
        else:
            self.lcd_timer.stop()
            self.ser.close()
            self.ser = None
            self.port_combo_box.setDisabled(False)
            self.button_port_refresh.setDisabled(False)
            self.main_control_frame.setDisabled(True)
            self.append_log("Disconnected")
            self.com_port = ''
            self.button_port_connect.setText("Connect")  
            self.lcdNumber.display(0)    
            self.setWindowTitle("SA-2005 Control Panel")            
            
        
        
    # lcd display update
    def lcd_update(self):
        self.write_command("SYSTEM MEAS?", 0)
        self.lcdNumber.display(self.get_input())
    
    # power control methods
    def hot_open(self):
        self.write_command("CONF HOT OPEN")
    
    def hot_closed(self):
        self.write_command("CONF HOT CLOSED")
        
    def neutral_open(self):
        self.write_command("CONF NEUTRAL OPEN")
    
    def neutral_closed(self):
        self.write_command("CONF NEUTRAL CLOSED")
        
    def ground_open(self):
        self.write_command("CONF GROUND OPEN")
    
    def ground_closed(self):
        self.write_command("CONF GROUND CLOSED")
        
    def polarity_fwd(self):
        self.write_command("CONF POLARITY FWD")
    
    def polarity_rev(self):
        self.write_command("CONF POLARITY REV")
        
    # measurement control methods
    
    def meas_mains_voltage(self):
        self.write_command("CONF MODE MVOL")
    
    def meas_device_current(self):
        self.write_command("CONF MODE DCUR")
    
    def meas_earth_resistance(self):
        self.write_command("CONF MODE ERES")
        
    def meas_earth_ground(self):
        self.write_command("CONF MODE ERGO")
        
    def meas_enclosure(self):
        self.write_command("CONF MODE ENCL")
        
    def meas_lead_to_earth(self):
        self.write_command("CONF MODE LEAR")
        
    def meas_lead_to_lead(self):
        self.write_command("CONF MODE LLEA")
    
    def meas_lead_isolation(self):
        self.write_command("CONF MODE LISO")
    
    def meas_external(self):
        self.write_command("CONF MODE EXT")
        
    
    #internal methods
    def append_log(self, message):
        self.console_output.appendPlainText(message)
        
    def clear_log(self):
        self.console_output.clear()
        
    def control_lock(self, state):
        self.main_control_frame.setDisabled(state)
        self.button_port_connect.setDisabled(state)
        
    def write_command(self, command, delay = 2):
        if delay > 0:
            self.control_lock(True)
        if self.checkbox_show_commands.isChecked() == True:
            self.append_log(command)
        command = command + "\n\r"
        self.ser.write(command.encode())
        if delay > 0:
            QtCore.QTimer.singleShot(delay * 1000, lambda: self.control_lock(False))

    def get_input(self):
        buf = ''
        while self.ser.inWaiting() > 0:
            num = self.ser.read().decode("utf-8").strip('\n')
            num.strip('\r')
            num.strip(' ')
            num.strip('\0')
            buf = buf + num
        try:
            return(float(buf))
        except:
            print(type(buf))
            print(buf)
            return(-1)
        
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec_()
