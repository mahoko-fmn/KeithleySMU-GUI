from abc import ABC, abstractmethod
from typing import Dict

class KeithleyDevice(ABC):
    """
    abstract contract for a keithley 2450-like

    Implementations:
        - Keithley2450Simulator
        - Keithley2450Hardware
    """

    # -----------------
    # Lifecycle
    # -----------------

    @abstractmethod
    def connect(self) -> None:
        """ establish connection to device (no-op for simulator)"""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """ release device resources cleanly"""
        pass

    # --------------
    # Setpoints
    # --------------

    @abstractmethod
    def set_voltage_setpoint(self, voltage: float) -> None:
        pass

    @abstractmethod
    def get_voltage_setpoint(self) -> float:
        pass

    @abstractmethod
    def set_current_setpoint(self, current:float) -> None:
        pass

    @abstractmethod
    def get_current_setpoint(self) -> float:
        pass

    # ---------------------
    # Output control
    # ---------------------

    @abstractmethod
    def output_on(self) -> bool:
        pass

    # ----------------
    # measurement
    # -----------------

    @abstractmethod
    def measure(self) -> Dict[str, float]:
        """
        returns:
            {
                "voltage": float,
                "current": float,
                "resistance": float
            }
        """
        pass
