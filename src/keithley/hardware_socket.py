# This program implements .....
# It does it by ...
#
# (c)
# ver
#
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
        self._compliance = False
        self._current_comliance = 0.05              # 50 mA default current compliance
        self._voltage_compliance = 15.0             # 15 V default voltage compliance

        # measurement state tracking
        self._last_measurement = {
            "voltage_measured": 0.0,
            "current_measured": 0.0,
            "voltage_setpoint": 0.0,
            "current_setpoint": 0.0,
            "mode": None,
            "resistance": 0,
            "compliance": self._compliance
         }

    # --------------------
    # Lifecycle
    # --------------------
    def connect(self) -> None:
        """ establish raw socket connection to instrument """

        self.rm = pyvisa.ResourceManager()

        self.inst = self.rm.open_resource(
            self.resource_string,
            read_termination = '\n',
            write_termination = '\n'
        )

        self._write("*RST")
        self._write("*CLS")                                             # removes old queue errors
        self._write("FORM:DATA ASC")
        self.inst.timeout = 3000
        self.inst.expect_termination = False

    def disconnect(self) -> None:
        """ close visa session """
        if self.inst:
            if self._output_on:
                self.inst.write(":OUTP OFF")
                self._output_on = False

            self.inst.close()
            self.inst = None

    def set_source_mode(self, mode: str) -> None:
        """ source mode configurations """

        if mode not in ("voltage", "current"):
            raise ValueError("Mode must be 'voltage' or 'current'")

        # safety turn output off if active
        if self._output_on:
            self.inst.write(":OUTP OFF")
            self._output_on = False

        #clear system
        self._write("*CLS")

        self._source_mode = mode

        if mode == "voltage":
            self._write(":SOUR:FUNC VOLT")

            # set safe default level, before enabling output
            self._current_setpoint = 0.0
            self._write(":SOUR:VOLT 0")

            self._write(f":SOUR:VOLT:ILIM {self._current_comliance}")       # setting current limit
            self._write(':SENS:FUNC CURR')
            self._write(":SENS:CURR:RANG:AUTO ON")

            time.sleep(0.05)

        elif mode == "current":
            self._write(":SOUR:FUNC CURR")

            self._voltage_setpoint = 0.0
            self._write(":SOUR:CURR 0")

            # Set voltage compliance once when mode is set
            self._write(f":SOUR:CURR:VLIM {self._voltage_compliance}")    # setting voltage limit
            self._write(':SENS:FUNC VOLT')
            self._write(":SENS:VOLT:RANG:AUTO ON")

            time.sleep(0.05)

        self._source_mode = mode

        # reset last measurent COMPLETELY
        self._last_measurement = {
            "voltage_measured": 0.0,
            "current_measured": 0.0,
            "voltage_setpoint": 0.0,
            "current_setpoint": 0.0,
            "mode": self._source_mode, # Corrected: Use self._source_mode
            "resistance": 0,
            "compliance": False
         }

    # ------------------
    # Measurement
    # -------------------
    def measure(self) -> Dict[str, float]:

        """ trigger measurement and return voltage,current,resistance """

        # stabalize measurement post configuration
        time.sleep(0.05)

        # Set sensing function, range, and protection based on source mode
        if self._source_mode == "voltage":
            self._write(':SENS:FUNC "CURR"')
            self._write(":SENS:CURR:RANG:AUTO ON")
            self._write(f":SENS:CURR:PROT {self._current_compliance}")

        elif self._source_mode == "current":
            self._write(':SENS:FUNC "VOLT"')
            self._write(":SENS:VOLT:RANG:AUTO ON")
            self._write(f":SENS:VOLT:PROT {self._voltage_compliance}")

        else:
            raise RuntimeError("Source mode is not set. Cannot perform measurement.")

        # --- KEY CHANGE STARTS HERE ---
        # You just need to separate “triggering a measurement”
        # from “asking for a value” and make sure both readings
        # correspond to the same operating point.
        # This is an attempt to measure the I/V of the same operating Setpoints
        # sequentially

        # Trigger ONE measurement
        reading = self.inst.query(":READ?")
        print(reading)
        # Parse returned values
        values = [float(x) for x in reading.split(',')]

        # Typical Keithley format: V, I, R, timestamp, status
        voltage = values[0]
        # current = values[1]  # the Keithley2450 does not I read in I mode

        # compliance detection
        if self._source_mode == "voltage":
            self._compliance = bool(int(self.inst.query(":SOUR:VOLT:ILIM:TRIP?")))
        elif self._source_mode == "current":
            self._compliance = bool(int(self.inst.query(":SOUR:CURR:VLIM:TRIP?")))

        current = self._current_setpoint

        self._write("*CLS")

        resistance = (
             voltage / current if abs(current) > 1e-12 else float('inf')
        )

        measurement = {
            "voltage_measured": voltage,
            "current_measured": current,
            "voltage_setpoint": self._voltage_setpoint,
            "current_setpoint": self._current_setpoint,
            "mode": self._source_mode,
            "resistance": resistance,
            "compliance": self._compliance
        }

        self._last_measurement = measurement



        self._write("*CLS")
        time.sleep(0.05)

        return measurement

    def _reinitialize_source(self):
        ''' reapplying source configurations'''

        if self._source_mode == "voltage":
            self._write(":SOUR:FUNC VOLT")
            self._write(':SENS:FUNC CURR')
            self._write(":SENS:CURR:RANG:AUTO ON")

        elif self._source_mode == "current":
            self._write(":SOUR:FUNC CURR")
            self._write(':SENS:FUNC VOLT')
            self._write(":SENS:VOLT:RANG:AUTO ON")

    def _prepare_voltage_sweep(self):
        self._write(":SOUR:FUNC VOLT")
        self._write(':SENS:FUNC CURR')

        self._write(f":SENS:CURR:PROT {self._current_comliance}")
        self._write(":SENS:CURR:RANG:AUTO ON")

    def voltage_sweep(self, start, stop, step, delay=0.5):

        """ perform a voltage sweep and measure current at each step.\n
        returns list of measurement dictionaries """

        self._prepare_voltage_sweep()
        self.output_on()

        results = []
        voltage = start

        if self.inst is None:
            raise RuntimeError("Device not connected")

        # accomodating negative sweep values
        if step > 0:
            condition = lambda v: v <= stop
        else:
            condition = lambda v: v >= stop

        while condition(voltage):

            # use API instead of direct SCPI
            self.set_voltage_setpoint(voltage)

            time.sleep(delay)

            measurement = self.measure()
            results.append(measurement)

            voltage += step

        return results

    #def current_sweep()


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

    def is_output_on(self):
        return self._output_on


    # instrument identification
    def identify(self):
        """ return instrument ID string """

        if self.inst is None:
            raise RuntimeError("Device not connected. Call connect() first.")

        self.inst.write("*IDN?")                        # send identify Command
        return self.inst.read()                         # read response until newline


    # accessing SMU errors
    #def read_error_queue(self):

    #    errors = []

    #    while True:
    #        err = self.inst.query(":SYST:ERR?")
    #        if err.startswith('0'):
    #            break
    #        errors.append(err)
    #    return errors

    # error checking
    def _check_error(self) -> None:

        """ Query instrument error queue. Raise RuntimeError if any error present """

        while True:

            self.inst.write(":SYST:ERR?")
            response = self.inst.read().strip()

            # response format code, message
            code_str, message = response.split(',',1)
            code = int(code_str)

            if code == 0:
                break

            raise RuntimeError(f"Instrument Error {code}: {message}")

    # write and error check helper
    def _write(self, cmd: str) -> None:
        # print(f"SCPI: {cmd}")
        self.inst.write(cmd)

        # termporal  code for debugging
        #self.inst.write(":SYST:ERR?")
        #err = self.inst.read()

        #print(f"ERR: {err}")

        #self._check_error()

    def debug_query(self, cmd):
        ''' running tests scripts, to test SMU commands and debugg'''
        response = self.inst.query(cmd)
        print(f"CMD: {cmd}")
        print(f"RES: {response}")
        return response
