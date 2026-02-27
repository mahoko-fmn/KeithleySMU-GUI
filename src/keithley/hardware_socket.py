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

        # state variables
        self._source_mode = None
        self._output_on = False
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
        # upon measurement data return, only send voltage and current
        self.inst.write(':FORM:ELEM VOLT, CURR')
        time.sleep(0.2)

    def disconnect(self) -> None:
        """ close visa session """
        if self.inst:
            if self._output_on:
                self.inst.write(":OUTP OFF")
                self._output_on = False

            self.inst.close()
            self.inst = None

    # ---------------
    # Setpoints
    # ---------------------

    def set_voltage_setpoint(self, voltage: float) -> None:
        if self._source_mode != "voltage":
            raise RuntimeError("Device not in voltage source mode")

        self._voltage_setpoint = voltage
        self.inst.write(f":SOUR:VOLT {voltage}")

    def set_current_setpoint(self, current: float) -> None:
        if self._source_mode != "current":
            raise RuntimeError("Device not in current source mode")

        self._current_setpoint = current
        self.inst.write(f":SOUR:CURR {current}")

    # ----------------------
    # Getters
    # ----------------------


    def get_voltage_setpoint(self) -> float:
        return self._voltage_setpoint

    def get_current_setpoint(self) -> float:
        return self._current_setpoint

    """Safe mode switching """
    def set_source_mode(self, mode: str) -> None:

        if mode not in ("voltage", "current"):
            raise ValueError("Mode must be 'voltage' or 'current'")

        # safety: turn output off if active
        if self._output_on:
            self.inst.write("OUTP OFF")
            self._output_on = False

        if mode == "voltage":
            self.inst.write(":SOUR:FUNC VOLT")
        else:
            self.inst.write(":SOUR:FUNC CURR")

        self._source_mode = mode

    def get_source_mode(self) -> str:
        return self._source_mode

    # --------------------
    # output control
    # ----------------------------

    def output_on(self) -> bool:
        if self._source_mode is None:
            raise RuntimeError("Source mode must be set before enabling output")

        self.inst.write(":OUTP ON")
        self._output_on = True

        return True

    def output_off(self) -> None:
        self.inst.write(":OUTP OFF")
        self._output_on = False


    # ------------------
    # Measurement
    # -------------------

    def measure(self) -> Dict[str, float]:
        """
        trigger measurement and return voltage/current/resistance
        """

        if self._source_mode == "voltage":
            self.inst.write("MEAS:CURR?")
            current = float(self.inst.read())
            voltage = self._voltage_setpoint

        elif self._source_mode == "current":
            self.inst.write("MEAS:VOLT?")
            voltage = float(self.inst.read())
            current = self._current_setpoint

        else:
            raise RuntimeError("Source mode not set")

        resistance = (
             voltage / current if abs(current) > 1e-12 else float("inf")
        )

        return {
            "voltage": voltage,
            "current": current,
            "resistance": abs(resistance)
        }

    def identify(self):
        """ return instrument ID string """
        self.inst.write("*IDN?")                        # send identify Command
        return self.inst.read()                         # read response until newline
