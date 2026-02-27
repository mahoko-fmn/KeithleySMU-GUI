from abc import ABC, abstractmethod
import random

class ErrorModel(ABC):
    @abstractmethod
    def apply(self, value: float) -> float:
        """ apply error to a true value """
        pass


class GaussianNoise(ErrorModel):

    def __init__(self, sigma: float):
        self.sigma = sigma

    def apply(self, value: float) -> float:
        return value + random.gauss(0, self.sigma)

class NoError(ErrorModel):
    def apply(self, value: float) -> float:
        return value
