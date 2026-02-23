import random
from src.keithley.device_interface import KeithleyDevice
from src.keithley.load_model import OhmicLoad
from src.keithley.error_model import GaussianNoise

class Keithley2450Simulator(KeithleyDevice):
    """
    deterministic + noise ohmic simulator for development and validation
    """

    def __init__(
        self,
        load_model = None,
        voltage_noise = 0.001,
        current_noise = 1e-6
    ):
        self._voltage_setpoint = 0.0
        self._current_setpoint = 0.0
        self._output_on = False

        self._measured_voltage = 0.0
        self._measured_current = 0.0


        self._last_measurement = {
        "voltage": 0.0,
        "current": 0.0,
        "resistance": float("inf")
        }

        # physical model
        self.load_model = load_model or OhmicLoad(1000)

        # error models
        self.voltage_error = GaussianNoise(voltage_noise)
        self.current_error = GaussianNoise(current_noise)

    # ----------------
    # lifecyle
    # ----------------

    def connect(self):
        pass                    # no hardware to connect

    def disconnect(self):
        pass                    # no hardware to release


    # ---------------
    # Setpoints
    # ---------------

    def set_voltage_setpoint(self, voltage: float):
        self._voltage_setpoint = voltage

    def get_voltage_setpoint(self) -> float:
        return self._voltage_setpoint

    def set_current_setpoint(self, current: float):
        self._current_setpoint = current

    def get_current_setpoint(self) -> float:
        return self._current_setpoint

    # -------------
    # outputs
    # --------------

    def output_on(self):
        self._output_on = True

    def output_off(self):
        self._output_on = False

    def is_output_on(self) -> bool:
        return self._output_on


    # ---------------------
    # Measurement
    # ---------------------

    def measure(self):
        if not self._output_on:
            self._last_measurement = {
                "voltage": 0.0,
                "current": 0.0,
                "resistance": float("inf")
            }
            return self._last_measurement

        true_voltage = self._voltage_setpoint
        true_current = self.load_model.current(true_voltage)

        measured_voltage = self.voltage_error.apply(true_voltage)
        measured_current = self.current_error.apply(true_current)

        if abs(measured_current) > 1e-12:
            resistance = measured_voltage / measured_current
        else:
            resistance = float("inf")

        self._last_measurement = {
            "voltage": measured_voltage,
            "current": measured_current,
            "resistance": resistance
        }

        return self._last_measurement

    def get_last_measurement(self):
        """Returns the last simulated measurement values."""
        return self._last_measurement
