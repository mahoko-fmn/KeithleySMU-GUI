import random
from src.keithley.device_interface import KeithleyDevice

class Keithley2450Simulator(KeithleyDevice):
    """
    deterministic + noise ohmic simulator for development and validation
    """

    def __init__(self, load_resistance: float = 1000.0):
        self._voltage_setpoint = 0.0
        self._current_setpoint = 0.0
        self._output_on = False

        self._measured_voltage = 0.0
        self._measured_current = 0.0
        self._measured_resistance = load_resistance

        self._load_resistance = load_resistance

        self._last_measurement = {
        "voltage": 0.0,
        "current": 0.0,
        "resistance": float("inf")
        }

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
            return{
                "voltage": 0.0,
                "current": 0.0,
                "resistance": float("inf")
            }

        # ohmic model
        ideal_current = self._voltage_setpoint / self._load_resistance

        # adding noise
        voltage = self._voltage_setpoint + random.uniform(-0.005, 0.005)
        current = ideal_current + random.uniform(-1e-6, 1e-6)

        resistance = (
            voltage / current if abs(current) > 1e-12 else float("inf")
        )

        self._last_measurement = {
            "voltage": voltage,
            "current": current,
            "resistance": resistance
        }

        return self._last_measurement

    def get_last_measurement(self):
        """Returns the last simulated measurement values."""
        return self._last_measurement
