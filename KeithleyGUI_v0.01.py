import tkinter as tk
import random
from datetime import datetime

# --- Placeholder for PyVISA Hardware Integration (Commented Out) ---
# To enable hardware control, install pyvisa: pip install pyvisa
# Uncomment the following block to integrate with actual hardware.

# import pyvisa as visa

# class Keithley2450Hardware:
#     """A placeholder class to demonstrate PyVISA integration for a Keithley 2450."""

#     def __init__(self, resource_name='GPIB0::24::INSTR'):
#         self._resource_name = resource_name
#         self._instrument = None
#         self._voltage_setpoint = 0.0
#         self._current_setpoint = 0.0
#         self._output_on = False
#         self._measured_voltage = 0.0
#         self._measured_current = 0.0
#         self._measured_resistance = 0.0
#         print(f"Attempting to connect to {self._resource_name} (commented out).")
#         try:
#             # self.rm = visa.ResourceManager()
#             # self._instrument = self.rm.open_resource(resource_name)
#             # self._instrument.write('*RST') # Reset instrument
#             # self._instrument.query('*IDN?') # Identify instrument
#             print(f"Successfully initialized placeholder for {resource_name}.")
#         except Exception as e:
#             print(f"Failed to connect to hardware: {e} (simulated error).")
#             self._instrument = None

#     def _send_command(self, command):
#         if self._instrument:
#             # self._instrument.write(command)
#             print(f"Hardware command sent (simulated): {command}")
#         else:
#             print(f"Hardware not connected. Command skipped: {command}")

#     def _query_command(self, command):
#         if self._instrument:
#             # response = self._instrument.query(command)
#             response = "0.0"
#             print(f"Hardware query (simulated): {command} -> {response}")
#             return float(response)
#         else:
#             print(f"Hardware not connected. Query skipped: {command}")
#             return 0.0

#     def set_voltage(self, voltage_value):
#         try:
#             self._voltage_setpoint = float(voltage_value)
#             # self._send_command(f':SOUR:VOLT {self._voltage_setpoint}')
#             print(f"Hardware: Set voltage to {self._voltage_setpoint:.3f} V (simulated).")
#             return True
#         except ValueError:
#             return False

#     def set_current(self, current_value):
#         try:
#             self._current_setpoint = float(current_value)
#             # self._send_command(f':SOUR:CURR {self._current_setpoint}')
#             print(f"Hardware: Set current to {self._current_setpoint:.3f} A (simulated).")
#             return True
#         except ValueError:
#             return False

#     def output_on(self):
#         self._output_on = True
#         # self._send_command(':OUTP ON')
#         print("Hardware: Output ON (simulated).")

#     def output_off(self):
#         self._output_on = False
#         # self._send_command(':OUTP OFF')
#         print("Hardware: Output OFF (simulated).")

#     def measure(self):
#         if self._output_on:
#             # self._measured_voltage = self._query_command(':MEAS:VOLT?')
#             # self._measured_current = self._query_command(':MEAS:CURR?')
#             # For placeholder, simulate values around setpoints
#             self._measured_voltage = self._voltage_setpoint + random.uniform(-0.002, 0.002)
#             self._measured_current = self._current_setpoint + random.uniform(-0.00005, 0.00005)

#             if abs(self._measured_current) > 1e-9: # Avoid division by zero
#                 self._measured_resistance = self._measured_voltage / self._measured_current
#             else:
#                 self._measured_resistance = float('inf') if abs(self._measured_voltage) > 1e-9 else 0.0
#         else:
#             self._measured_voltage = 0.0
#             self._measured_current = 0.0
#             self._measured_resistance = 0.0
#         print(f"Hardware measurement (simulated): V={self._measured_voltage:.3f} V, I={self._measured_current:.3f} A")

#         return {
#             'voltage': self._measured_voltage,
#             'current': self._measured_current,
#             'resistance': self._measured_resistance
#         }

#     def get_voltage_setpoint(self):
#         # return self._query_command(':SOUR:VOLT?') if self._instrument else self._voltage_setpoint
#         return self._voltage_setpoint

#     def get_current_setpoint(self):
#         # return self._query_command(':SOUR:CURR?') if self._instrument else self._current_setpoint
#         return self._current_setpoint

#     def is_output_on(self):
#         # return bool(self._query_command(':OUTP?')) if self._instrument else self._output_on
#         return self._output_on

#     def get_last_measurement(self):
#         return {
#             'voltage': self._measured_voltage,
#             'current': self._measured_current,
#             'resistance': self._measured_resistance
#         }

#     def close(self):
#         if self._instrument:
#             # self._instrument.close()
#             # self.rm.close()
#             print("Hardware connection closed (simulated).")
#         else:
#             print("No hardware connection to close (simulated).")
# ------------------------------------------------------------------

class Keithley2450Simulator:
    """A simulator for the Keithley 2450 Sourcemeter."""

    def __init__(self):
        self._voltage_setpoint = 0.0  # Volts
        self._current_setpoint = 0.0  # Amperes
        self._output_on = False
        self._measured_voltage = 0.0
        self._measured_current = 0.0
        self._measured_resistance = 0.0

    def set_voltage(self, voltage_value):
        """Sets the voltage setpoint."""
        try:
            self._voltage_setpoint = float(voltage_value)
            return True
        except ValueError:
            return False

    def set_current(self, current_value):
        """Sets the current setpoint."""
        try:
            self._current_setpoint = float(current_value)
            return True
        except ValueError:
            return False

    def output_on(self):
        """Turns the output on."""
        self._output_on = True

    def output_off(self):
        """Turns the output off."""
        self._output_on = False

    def measure(self):
        """Simulates a measurement and updates internal measured values."""
        if self._output_on:
            self._measured_voltage = self._voltage_setpoint + random.uniform(-0.005, 0.005)
            if self._current_setpoint == 0:
                self._measured_current = random.uniform(-1e-6, 1e-6)
            else:
                self._measured_current = self._current_setpoint + random.uniform(-0.0005, 0.0005)

            if abs(self._measured_current) > 1e-9:
                self._measured_resistance = self._measured_voltage / self._measured_current
            else:
                self._measured_resistance = float('inf') if abs(self._measured_voltage) > 1e-9 else 0.0
        else:
            self._measured_voltage = 0.0
            self._measured_current = 0.0
            self._measured_resistance = 0.0

        return {
            'voltage': self._measured_voltage,
            'current': self._measured_current,
            'resistance': self._measured_resistance
        }

    def get_voltage_setpoint(self):
        """Returns the current voltage setpoint."""
        return self._voltage_setpoint

    def get_current_setpoint(self):
        """Returns the current current setpoint."""
        return self._current_setpoint

    def is_output_on(self):
        """Returns True if the output is on, False otherwise."""
        return self._output_on

    def get_last_measurement(self):
        """Returns the last simulated measurement values."""
        return {
            'voltage': self._measured_voltage,
            'current': self._measured_current,
            'resistance': self._measured_resistance
        }


class SourcemeterGUI:
    """Manages the GUI elements for the Keithley 2450 Sourcemeter Simulator."""

    def __init__(self, master, simulator):
        self.master = master
        self.simulator = simulator # This will be either Keithley2450Simulator or Keithley2450Hardware
        self.master.title('Keithley 2450 Sourcemeter Simulator')
        self.master.geometry('800x600')

        self.voltage_setpoint_var = tk.StringVar(value=str(self.simulator.get_voltage_setpoint()))
        self.current_setpoint_var = tk.StringVar(value=str(self.simulator.get_current_setpoint()))
        self.output_status_var = tk.StringVar(value="Output: OFF")
        self.measured_voltage_var = tk.StringVar(value="Measured V: 0.000 V")
        self.measured_current_var = tk.StringVar(value="Measured I: 0.000 A")
        self.measured_resistance_var = tk.StringVar(value="Measured R: 0.000 Ohm")

        self._create_widgets()
        self._update_gui_status()
        self._log_message("Simulator GUI initialized.")
        self._log_message("Set Voltage and Current, then turn Output ON.")

    def _create_widgets(self):
        main_frame = tk.Frame(self.master, padx=10, pady=10)
        main_frame.pack(fill='both', expand=True)

        setpoint_frame = tk.LabelFrame(main_frame, text="Setpoints", padx=10, pady=10)
        setpoint_frame.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

        tk.Label(setpoint_frame, text="Voltage (V):").grid(row=0, column=0, padx=5, pady=2, sticky='w')
        self.voltage_entry = tk.Entry(setpoint_frame, textvariable=self.voltage_setpoint_var, width=15)
        self.voltage_entry.grid(row=0, column=1, padx=5, pady=2, sticky='ew')

        tk.Label(setpoint_frame, text="Current (A):").grid(row=1, column=0, padx=5, pady=2, sticky='w')
        self.current_entry = tk.Entry(setpoint_frame, textvariable=self.current_setpoint_var, width=15)
        self.current_entry.grid(row=1, column=1, padx=5, pady=2, sticky='ew')

        setpoint_frame.grid_columnconfigure(1, weight=1)

        control_frame = tk.LabelFrame(main_frame, text="Controls", padx=10, pady=10)
        control_frame.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

        tk.Button(control_frame, text="Set Voltage", command=self._set_voltage_cmd).grid(row=0, column=0, padx=5, pady=2, sticky='ew')
        tk.Button(control_frame, text="Set Current", command=self._set_current_cmd).grid(row=1, column=0, padx=5, pady=2, sticky='ew')
        tk.Button(control_frame, text="Output ON", command=self._output_on_cmd, bg='green', fg='white').grid(row=2, column=0, padx=5, pady=2, sticky='ew')
        tk.Button(control_frame, text="Output OFF", command=self._output_off_cmd, bg='red', fg='white').grid(row=3, column=0, padx=5, pady=2, sticky='ew')
        tk.Button(control_frame, text="Measure", command=self._measure_cmd).grid(row=4, column=0, padx=5, pady=2, sticky='ew')

        control_frame.grid_columnconfigure(0, weight=1)

        status_frame = tk.LabelFrame(main_frame, text="Status and Measurements", padx=10, pady=10)
        status_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='ew')

        tk.Label(status_frame, textvariable=self.output_status_var, font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        tk.Label(status_frame, textvariable=self.measured_voltage_var, font=('Arial', 10)).grid(row=1, column=0, padx=5, pady=2, sticky='w')
        tk.Label(status_frame, textvariable=self.measured_current_var, font=('Arial', 10)).grid(row=2, column=0, padx=5, pady=2, sticky='w')
        tk.Label(status_frame, textvariable=self.measured_resistance_var, font=('Arial', 10)).grid(row=3, column=0, padx=5, pady=2, sticky='w')

        status_frame.grid_columnconfigure(0, weight=1)

        output_frame = tk.LabelFrame(main_frame, text="Output Log", padx=5, pady=5)
        output_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

        self.output_text = tk.Text(output_frame, height=10, state='disabled', wrap='word', font=('Consolas', 9))
        self.output_text.pack(side='left', fill='both', expand=True)

        output_scrollbar = tk.Scrollbar(output_frame, command=self.output_text.yview)
        output_scrollbar.pack(side='right', fill='y')
        self.output_text['yscrollcommand'] = output_scrollbar.set

        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_rowconfigure(2, weight=2)

    def _set_voltage_cmd(self):
        if self.simulator.set_voltage(self.voltage_setpoint_var.get()):
            self._log_message(f"GUI: Set voltage to {self.simulator.get_voltage_setpoint():.3f} V")
        else:
            self._log_message("GUI: Invalid voltage input. Please enter a number.")

    def _set_current_cmd(self):
        if self.simulator.set_current(self.current_setpoint_var.get()):
            self._log_message(f"GUI: Set current to {self.simulator.get_current_setpoint():.3f} A")
        else:
            self._log_message("GUI: Invalid current input. Please enter a number.")

    def _output_on_cmd(self):
        self.simulator.output_on()
        self._update_gui_status()
        self._log_message("GUI: Output ON command sent.")

    def _output_off_cmd(self):
        self.simulator.output_off()
        self._update_gui_status()
        self._log_message("GUI: Output OFF command sent.")

    def _measure_cmd(self):
        measurements = self.simulator.measure()
        self.measured_voltage_var.set(f"Measured V: {measurements['voltage']:.3f} V")
        self.measured_current_var.set(f"Measured I: {measurements['current']:.3f} A")
        if measurements['resistance'] == float('inf'):
            self.measured_resistance_var.set("Measured R: INF Ohm")
        else:
            self.measured_resistance_var.set(f"Measured R: {measurements['resistance']:.3f} Ohm")
        self._update_gui_status()
        self._log_message(f"GUI: Measurement - V={measurements['voltage']:.3f}V, I={measurements['current']:.3f}A, R={measurements['resistance']:.3f}Ohm")

    def _update_gui_status(self):
        if self.simulator.is_output_on():
            self.output_status_var.set("Output: ON")
        else:
            self.output_status_var.set("Output: OFF")

        last_meas = self.simulator.get_last_measurement()
        self.measured_voltage_var.set(f"Measured V: {last_meas['voltage']:.3f} V")
        self.measured_current_var.set(f"Measured I: {last_meas['current']:.3f} A")
        if last_meas['resistance'] == float('inf'):
            self.measured_resistance_var.set("Measured R: INF Ohm")
        else:
            self.measured_resistance_var.set(f"Measured R: {last_meas['resistance']:.3f} Ohm")

    def _log_message(self, message):
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        log_entry = f"{timestamp} {message}\n"
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, log_entry)
        self.output_text.see(tk.END)
        self.output_text.config(state='disabled')


# --- Integration and Local Execution Instructions (with Hardware Placeholder) ---
# The following block demonstrates how to integrate and run the GUI locally.
# It is commented out because this environment does not support GUI display.
# To see the functional GUI, copy this entire code block into a local Python file
# (e.g., `sourcemeter_app.py`) and run it from your terminal using `python sourcemeter_app.py`.

if __name__ == '__main__':
#     # Flag to switch between simulator and actual hardware
#     # Set to True to attempt connection to a physical device (requires PyVISA and device connected)
     USE_HARDWARE = False
     HARDWARE_RESOURCE = 'GPIB0::24::INSTR' # Update with your instrument's VISA resource string

     root = tk.Tk()

     if USE_HARDWARE:
#         # Make sure pyvisa is installed (pip install pyvisa) and uncomment the Keithley2450Hardware class above.
#         # simulator_instance = Keithley2450Hardware(HARDWARE_RESOURCE)
         print("Hardware mode selected (functionality commented out).")
         simulator_instance = Keithley2450Simulator() # Fallback to simulator if hardware is commented out
     else:
         simulator_instance = Keithley2450Simulator()
         print("Simulator mode selected.")

     app = SourcemeterGUI(root, simulator_instance)

#     # Handle window closing to ensure proper hardware resource release
#     # def on_closing():
#     #     if USE_HARDWARE and isinstance(simulator_instance, Keithley2450Hardware):
#     #         simulator_instance.close()
#     #     root.destroy()
#     # root.protocol("WM_DELETE_WINDOW", on_closing)

     root.mainloop()

print("Keithley2450Hardware class added as a commented-out placeholder for PyVISA integration.")
print("The SourcemeterGUI `__init__` has a commented-out section to switch between simulator and hardware.")
print("All necessary imports for hardware are also commented out. Please run locally to test GUI features.")
