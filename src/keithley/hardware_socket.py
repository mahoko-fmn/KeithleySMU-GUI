import pyvisa
import time

from typing import Dict
from keithley.device_interface import KeithleyDevice

class Keithley2450Hardware(KeithleyDevice):
    """
    minimal raw-socket harware interface. no auto reset, no auto config. Just transport stability first
    """

    def __init__(self, resource_string: str):
        self.resource_string = resource_string
        self.rm = None
        self.inst = None

        self._voltage_setpoint = 0.0
        self._current_setpoint = 0.0

    # --------------------
    # Lifecycle
    # --------------------

    def connect(self) -> None:
        """ establish raw socket connection to instrument"""

        self.rm = pyvisa.ResourceManager()

        self.inst = self.rm.open_resource(
            self.resource_string,
            read_termination = '\n',
            write_termination = '\n'
        )

        self.inst.timeout = 3000
        self.inst.expect_termination = False

        self.inst.write("*CLS")
        time.sleep(0.2)

    def disconnet(self) -> None:
        """ close visa session cleanly"""

        if self.inst:
            self.inst.write(":OUTP OFF")
            self.inst.close()
            self.inst = None

    # ---------------
    # Setpoints
    # ---------------------

    def set_voltage_setpoint(self, voltage: float) -> None:
        self._voltage_setpoint = voltage

        self.inst.write(":SOUR:FUNC VOLT")
        self.inst.write(f":SOUR:VOLT {voltage}")

    def get_voltage_setpoint(self) -> float:
        return self._voltage_setpoint

    def set_current_setpoint(self, current: float) -> None:
        self._current_setpoint = current

        self.inst.write(":SOUR:FUNC CURR")
        self.inst.write(f":SOUR:CURR {current}")

    def get_current_setpoint(self) -> float:
        return self._current_setpoint

    # --------------------
    # output control
    # ----------------------------

    def output_on(self) -> bool:
        self.inst.write(":OUTP ON")
        return True


    # ------------------
    # Measurement
    # -------------------

    def measure(self) -> Dict[str, float]:
        """
        trigger measurement and return voltage/current/resistance
        """

        self.inst.write("READ?")
        response = self.inst.read()

        values = response.split(",")

        voltage = float(values[0])
        current = float(values[1])

        resistance = (
            voltgae / current is abs(current) > 1e-12 else float("inf")
        )

        return {
            "voltage": voltage,
            "current": current,
            "resistance": resistance
        }

#    def identify(self):
#        """ return instrument ID string """
#        self.inst.write("*IDN?")                        # send identify Command
#        return self.inst.read()                         # read response until newline

#    def close(self):
#        """ close visa session """
#        self.inst.close()
