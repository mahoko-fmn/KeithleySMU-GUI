import tkinter as tk
from tkinter import filedialog
import random
from datetime import datetime
import csv

class SourcemeterGUI:
    """Manages the GUI elements for the Keithley 2450 Sourcemeter Simulator."""

    def __init__(self, master, simulator):
        self.master = master
        self.simulator = simulator # This will be either Keithley2450Simulator or Keithley2450Hardware
        self.master.title('Keithley 2450 Control Interface')
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

        # creating a mode selection panel
        mode_frame = tk.LabelFrame(main_frame, text="Source Mode", padx=10, pady=10)
        mode_frame.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.source_mode_var = tk.StringVar(value="voltage")

        tk.Radiobutton(
            mode_frame,
            text="Voltage Source",
            variable=self.source_mode_var,
            value="voltage",
            command=self._set_source_mode_cmd
        ).grid(row=1, column=0, sticky="w")

        tk.Radiobutton(
            mode_frame,
            text="Current Source",
            variable=self.source_mode_var,
            value="current",
            command=self._set_source_mode_cmd
        ).grid(row=1, column=0, sticky="w")

        # sweep controls
        sweep_frame = tk.LabelFrame(main_frame, text="Voltage Sweep", padx=10, pady=10)
        sweep_frame.grid(row=0, column=2, padx=2, pady=5, sticky='nsew')

        tk.Label(sweep_frame, text="Start (V):").grid(row=0, column=0)
        tk.Label(sweep_frame, text="Stop (V):").grid(row=1, column=0)
        tk.Label(sweep_frame, text="Step (V):").grid(row=2, column=0)

        self.sweep_start_var = tk.StringVar(value="0")
        self.sweep_stop_var = tk.StringVar(value="1")
        self.sweep_step_var = tk.StringVar(value="0.1")

        tk.Entry(sweep_frame, textvariable=self.sweep_start_var).grid(row=0, column=1)
        tk.Entry(sweep_frame, textvariable=self.sweep_stop_var).grid(row=1, column=1)
        tk.Entry(sweep_frame, textvariable=self.sweep_step_var).grid(row=2, column=1)

        tk.Button(
            sweep_frame,
            text="Run Sweep",
            command=self._run_sweep_cmd,
            bg="blue",
            fg="white"
        ).grid(row=3, column=0, columnspan=2, pady=2, sticky="ew")

        # saving data button
        tk.Button(
            sweep_frame,
            text="Save Data",
            command=self._save_data_cmd,
            bg="blue",
            fg="white"
        ).grid(row=4, column=0, columnspan=2, pady=2, sticky="ew")

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

        # setting voltage source as default mode
        self.simulator.set_source_mode("voltage")
        self._log_message("Default source mode set to voltage")

    # command handler
    def _set_source_mode_cmd(self):
        mode = self.source_mode_var.get()
        try:
            self.simulator.set_source_mode(mode)
            self._log_message(f"GUI: Source mode set to {mode}")

        except Exception as e:
            self._log_message(f"Error setting source mode: {e}")

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

    # sweep command
    def _run_sweep_cmd(self):
        try:
            start = float(self.sweep_start_var.get())
            stop = float(self.sweep_stop_var.get())
            step = float(self.sweep_step_var.get())

            self._log_message(
                f"GUI: Starting sweep {start} -> {stop} V step {step}"
            )

            data = self.simulator.voltage_sweep(start, stop, step)
            self.last_sweep_data = data

            self._log_message("GUI: Sweep complete")

            for point in data:
                self._log_message(
                    f"Sweep: V={point['voltage']:.3f}"
                    f" I={point['current']:.6f}"
                )

        except ValueError:
            self._log_message("GUI: Invalid sweep parameters")

    def _update_gui_status(self):
        if self.simulator.output_on():
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

    # def _save_sweep_to_csv(self, data):
    #     timestamp = datetime.now().strtime("%Y-%m-%d_%H-%M-%S")
    #
    #     file_path = filedialog.asksaveasfilename(
    #         initialfile = f"iv_sweep_{timestamp}.csv,
    #         defaultextension =".csv",
    #         filetypes = [("CSV files", "*.csv")],
    #         title = "Save sweep data"
    #     )
    #     if not file_path:
    #         self._log_message("GUI: Save cancelled")
    #         return
    #     try:
    #         with open(file_path, mode="w", newline="") as file:
    #             writer = csv.writer(file)
    #             writer.writerow(["Voltage (V)", "Current (A)", "Resistance (Ohm)"])
    #
    #             for point in data:
    #                 writer.writerow([
    #                     point["voltage"],
    #                     point["current"],
    #                     point["resistance"]
    #                 ])
    #
    #         self._log_message(f"GUI: Data saved to {file_path}")
    #     except Exception as e:
    #         self._log_message(f"GUI: Error saving file: {e}")

    def _save_data_cmd(self):

        if not hasattr(self, "last_sweep_data"):
            self._log_message("GUI: No sweep data to save")
            return

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = filedialog.asksaveasfilename(
            initialfile = f"iv_sweep_{timestamp}.csv",
            defaultextension = ".csv",
            filetypes = [("CSV files", "*.csv")],
            title = "Save sweep data"
        )

        if not file_path:
            self._log_message("GUI: Save cancelled")
            return
        try:
            with open(file_path, "w", newline="") as f:
                # ----------- METADATA ----------------
                now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

                f.write(f"# Instrument: Keithley2450 Source Measure Unit\n")
                f.write(f"# Date: {now} \n")

                source_mode = self.source_mode_var.get()
                f.write(f"# Source Mode: {source_mode}\n")

                start = self.sweep_start_var.get()
                stop = self.sweep_stop_var.get()
                step = self.sweep_step_var.get()

                f.write(f"# Sweep Start: {start} V\n")
                f.write(f"# Sweep Stop: {stop} V\n")
                f.write(f"# Sweep Step: {step} V\n")

                # ------------ DATA TABLE --------------
                writer = csv.writer(f)
                writer.writerow(["Voltage (V)", "Current (A)", "Resistance (Ohm)"])

                for point in self.last_sweep_data:
                    writer.writerow([
                        point["voltage"],
                        point["current"],
                        point["resistance"]
                    ])
            self._log_message(f"GUI: Data saved to {file_path}")

        except Exception as e:
            self._log_message(f"GUI: Error saving data {e}")

    def _log_message(self, message):
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        log_entry = f"{timestamp} {message}\n"
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, log_entry)
        self.output_text.see(tk.END)
        self.output_text.config(state='disabled')
