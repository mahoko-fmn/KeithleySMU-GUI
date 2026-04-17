import sys
import os
import time

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from keithley.hardware_socket import Keithley2450Hardware

device = Keithley2450Hardware("TCPIP0::192.168.50.200::inst0::INSTR")

device.connect()

# --- test commands here ------
device.debug_query("*IDN?")

#device.debug_query("READ?")

# try measurement
print(device.debug_query(":MEAS:ALL?"))

device.disconnect()
