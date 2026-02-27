from abc import ABC, abstractmethod
import math

class LoadModel(ABC):
    """ abstract physical for DUT behavior"""

    @abstractmethod
    def current(self, voltage: float) -> float:
        """ return the current through DUT given voltage"""
        pass

class OhmicLoad(LoadModel):
    def __init__(self, resistance: float):
        self.resistance = resistance

    def current(self, voltage: float) -> float:
        return voltage / self.resistance

class NonlinearLoad(LoadModel):
    """
    I = aV + BV^2
    Models weak non-linearity
    """

    def __init__(self, a: float, b: float):
        self.a = a
        self.b = b

    def current(self, voltage: float) -> float:
        return self.a * voltage + self.b * voltage**2

class DiodeLoad(LoadModel):
    """
    shockley diode equation:'
    I = Is (exp(V / (nVt)) - 1)
    """

    def __init__(self, Is: float = 1e-12, n:float = 1.8, Vt: float = 0.02585):
        self.Is = Is
        self.n  =  n
        self.Vt = Vt

    def current(self, voltage: float) -> float:
        return self.Is * (math.exp(voltage / (self.n * self.Vt)) - 1)
