import tkinter as tk
import random
from datetime import datetime

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
        try:
            value = float(self.voltage_setpoint_var.get())
            self.simulator.set_voltage_setpoint(value)
            self._log_message(f"GUI: Set voltage to {value:.3f} V")
        except ValueError:
            self._log_message("GUI: Invalid voltage input. Please enter a number.")

    def _set_current_cmd(self):
        try:
            value = float(self.current_setpoint_var.get())
            self.simulator.set_current_setpoint(value)
            self._log_message(f"GUI: Set current to {value:.6f} A")
        except ValueError:
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

        self.measured_voltage_var.set(
            f"Measured V: {measurements['voltage']:.3f} V"
        )
        self.measured_current_var.set(
            f"Measured I: {measurements['current']:.6f} A"
        )

        if measurements['resistance'] == float('inf'):
            self.measured_resistance_var.set("Measured R: INF Ohm")
        else:
            self.measured_resistance_var.set(
                f"Measured R: {measurements['resistance']:.3f} Ohm"
            )

        self._update_gui_status()

        self._log_message(
            f"GUI: Measurement - "
            f"V={measurements['voltage']:.3f} V, "
            f"I={measurements['current']:.6f} A, "
            f"R={measurements['resistance']:.3f} Ohm"
        )

    def _update_gui_status(self):
        if self.simulator.is_output_on():
            self.output_status_var.set("Output: ON")
        else:
            self.output_status_var.set("Output: OFF")

        last_meas = self.simulator.get_last_measurement()

        self.measured_voltage_var.set(
            f"Measured V: {last_meas['voltage']:.3f} V"
            )
        self.measured_current_var.set(
                f"Measured I: {last_meas['current']:.6f} A"
            )

        if last_meas['resistance'] == float('inf'):
            self.measured_resistance_var.set("Measured R: INF Ohm")
        else:
            self.measured_resistance_var.set(
                f"Measured R: {last_meas['resistance']:.3f} Ohm"
            )

    def _log_message(self, message):
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        log_entry = f"{timestamp} {message}\n"
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, log_entry)
        self.output_text.see(tk.END)
        self.output_text.config(state='disabled')
