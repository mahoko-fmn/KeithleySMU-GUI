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

        # internal compliance states
        self._current_comliance = 0.01              # 10mA default
        self._voltage_compliance = 10.0             # 10V default

        # measurement state tracking
        self._last_measurement = {
            "voltage": 0.0,
            "current": 0.0,
            "resistance": 0.0
        }

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

        self.inst.write("*CLS")                     # removes old queue errors
        self.inst.timeout = 3000
        self.inst.expect_termination = False

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
        self._write(f":SOUR:VOLT {voltage}")


    def set_current_setpoint(self, current: float) -> None:
        if self._source_mode != "current":
            raise RuntimeError("Device not in current source mode")

        self._current_setpoint = current
        self._write(f":SOUR:CURR {current}")

    # ----------------------
    # Getters
    # ----------------------


    def get_voltage_setpoint(self) -> float:
        return self._voltage_setpoint

    def get_current_setpoint(self) -> float:
        return self._current_setpoint

    def get_last_measurement(self):
        return self._last_measurement

    """Safe mode switching """
    def set_source_mode(self, mode: str) -> None:

        if mode not in ("voltage", "current"):
            raise ValueError("Mode must be 'voltage' or 'current'")

        # safety: turn output off if active
        if self._output_on:
            self.inst.write("OUTP OFF")
            self._output_on = False

        if mode == "voltage":
            self._write(":SOUR:FUNC:MODE VOLT")
            self._write(':SENS:FUNC "CURR"')
            self._write(f":SOUR:VOLT:ILIM {self._current_comliance}")                   # setting current limit to 10 mA

        else:
            self._write(":SOUR:FUNC CURR")
            self._write(':SENS:FUNC "VOLT"')
            self._write(f":SOUR:CURR:VLIM {self._voltage_compliance}")                   # setting voltage limit to 10 V

        self._source_mode = mode

    def get_source_mode(self) -> str:
        return self._source_mode

    # --------------------
    # output control
    # ----------------------------

    def output_on(self) -> bool:
        if self._source_mode is None:
            raise RuntimeError("Source mode must be set before enabling output")

        self._write(":OUTP ON")

        self._output_on = True

        return True

    def output_off(self) -> None:
        self._write(":OUTP OFF")
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

        measurement = {
            "voltage": voltage,
            "current": current,
            "resistance": abs(resistance)
        }

        self._last_measurement = measurement

        return measurement

    # voltage sweep
    def voltage_sweep(self, start, stop, step, delay=0.1):
        """
        perform a voltage sweep and measure current at each step.
        returns list of measurement dictionaries
        """
        results = []
        voltage = start

        if self.inst is None:
            raise RuntimeError("Device not connected")

        while voltage <= stop:

            # use API instead of direct SCPI
            self.set_voltage_setpoint(voltage)

            time.sleep(delay)

            measurement = self.measure()

            results.append(measurement)

            voltage += step

        return results

    # instrument identification
    def identify(self):
        """ return instrument ID string """

        if self.inst is None:
            raise RuntimeError("Device not connected. Call connect() first.")

        self.inst.write("*IDN?")                        # send identify Command
        return self.inst.read()                         # read response until newline

    # error checking
    def _check_error(self) -> None:
        """
        Query instrument error queue. Raise RuntimeError if any error present
        """
        while True:

            self.inst.write(":SYST:ERR?")
            response = self.inst.read().strip()

            # response format: <code>, "message"
            code_str, message = response.split(",",1)
            code = int(code_str)

            if code == 0:
                break

            raise RuntimeError(f"Instrument Error {code}: {message}")

    # write and error check helper
    def _write(self, cmd:str) -> None:
        # print("SCPI >>", cmd)
        self.inst.write(cmd)

        # termporal  code for debugging
        self.inst.write(":SYST:ERR?")
        err = self.inst.read()

        print("ERR <", err)

        self._check_error()
