import csv
from datetime import datetime

class MeasurementController:
    """
    Handles sweep execution, data collection, and export independent of GUI
    """

    def __init__(self, device):
        self.device = device
        self.data = []

    def clear_data(self):
        self.data = []

    def voltage_sweep(self, start, stop, step):
        """ perform a voltage sweep """
        self.clear_data()

        voltage = start
        self.device.output_on()

        while voltage <= stop:
            self.device.set_voltage_setpoint(voltage)
            measurement = self.device.measure()

            entry = {
                "timestamp": datetime.now(),
                "set_voltage": voltage,
                "measured_voltage": measurement["voltage"],
                "measured_current": measurement["current"],
                "measured_resistance": measurement["resistance"]
            }

            self.data.append(entry)
            voltage += step

        self.device.output_off()

        return self.data

    def save_csv(self, filename):
        """
        save collected data to csv file
        """

        if not self.data:
            return

        fieldnames = self.data[0].keys()

        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            write.writerows(self.data)
