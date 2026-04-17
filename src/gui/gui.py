import random
import csv
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog
from datetime import datetime


class SourcemeterGUI:
    """Manages the GUI elements for the Keithley 2450 Sourcemeter Simulator."""

    def __init__(self, master, simulator):
        self.master = master
        self.simulator = simulator # This will be either Keithley2450Simulator or Keithley2450Hardware
        self.master.title('Keithley 2450 Control Interface')
        self.master.geometry('900x700')

        self.voltage_setpoint_var = tk.StringVar(value=str(self.simulator.get_voltage_setpoint()))
        self.current_setpoint_var = tk.StringVar(value=str(self.simulator.get_current_setpoint()))
        self.output_status_var = tk.StringVar(value="Output: OFF")
        self.measured_voltage_var = tk.StringVar(value="Measured V: 0.000 V")
        self.measured_current_var = tk.StringVar(value="Measured I: 0.000 A")
        self.measured_resistance_var = tk.StringVar(value="Measured R: 0.000 Ohm")

        self._create_widgets()
        self._update_gui_status()
        self._log_message("SMU Hardware-GUI initialized.")

    def _create_widgets(self):
        main_frame = tk.Frame(self.master, padx=10, pady=10)
        main_frame.pack(fill='both', expand=True)

        source_frame = tk.LabelFrame(
            main_frame,
            text="Source Configure",
            padx=10,
            pady=10
        )

        source_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        # creating a mode selection toggle
        mode_frame = tk.LabelFrame(source_frame, text="Source Mode")
        mode_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        setpoint_frame = tk.LabelFrame(source_frame, text="Setpoints")
        setpoint_frame.grid(row=1, column=0, padx=5, pady=5, sticky='ew')

        setpoint_frame.grid_columnconfigure(0, weight=1)


        tk.Label(setpoint_frame, text="Voltage (V):").grid(row=0, column=0, padx=5, pady=2, sticky='w')
        self.voltage_entry = tk.Entry(setpoint_frame, textvariable=self.voltage_setpoint_var, width=15, state= "disabled")
        self.voltage_entry.grid(row=0, column=1, padx=5, pady=2, sticky='ew')

        tk.Label(setpoint_frame, text="Current (A):").grid(row=1, column=0, padx=5, pady=2, sticky='w')
        self.current_entry = tk.Entry(setpoint_frame, textvariable=self.current_setpoint_var, width=15)
        self.current_entry.grid(row=1, column=1, padx=5, pady=2, sticky='ew')


        self.source_mode_var = tk.StringVar(value="current") # set the default Radiobutton

        tk.Radiobutton(
            mode_frame,
            text="Voltage Source",
            variable=self.source_mode_var,
            value="voltage",
            command=self._set_source_mode_cmd,
            state= "disabled"
        ).grid(row=0, column=0, sticky="w")

        tk.Radiobutton(
            mode_frame,
            text="Current Source",
            variable=self.source_mode_var,
            value="current",
            command=self._set_source_mode_cmd
        ).grid(row=1, column=0, sticky="w")


        """ control center """
        control_frame = tk.LabelFrame(main_frame, text="Controls", padx=10, pady=10)
        control_frame.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

        tk.Button(control_frame, text="Set Voltage", command=self._set_voltage_cmd).grid(row=0, column=0, padx=5, pady=2, sticky='ew', state="disabled")
        tk.Button(control_frame, text="Set Current", command=self._set_current_cmd).grid(row=1, column=0, padx=5, pady=2, sticky='ew')


        # self.output_on_button = tk.Button(
        #     control_frame,
        #     text="Output ON",
        #     command=self._output_on_cmd,
        #     bg='green',
        #     fg='white'
        #     )
        # self.output_on_button.grid(row=2, column=0, padx=5, pady=2, sticky='ew')
        #
        # self.output_off_button = tk.Button(
        #     control_frame,
        #     text="Output OFF",
        #     command=self._output_off_cmd,
        #     bg='red',
        #     fg='yellow'
        #     )
        # self.output_off_button.grid(row=3, column=0, padx=5, pady=2, sticky='ew')

        # update from two to single button output indicator
        # when sweeping temporarily disable the button.
        self.output_button = tk.Button(
            control_frame,
            text="OUTPUT OFF",
            bg="red",
            fg="white",
            command=self._toggle_output_cmd
        )
        self.output_button.grid(row=2, column=0, padx=5, pady=2, sticky="ew")

        self.measure_button = tk.Button(
            control_frame,
            text="Measure",
            command=self._measure_cmd
        )
        self.measure_button.grid(row=4, column=0, padx=5, pady=2, sticky='ew')

        # sweep controls
        sweep_frame = tk.LabelFrame(main_frame, text="Voltage Sweep", padx=10, pady=10)
        sweep_frame.grid(row=0, column=2, padx=5, pady=5, sticky='ew')

        tk.Label(sweep_frame, text="Start (V):").grid(row=0, column=0)
        tk.Label(sweep_frame, text="Stop (V):").grid(row=1, column=0)
        tk.Label(sweep_frame, text="Step (V):").grid(row=2, column=0)

        self.sweep_start_var = tk.StringVar(value="0.0")
        self.sweep_stop_var = tk.StringVar(value="0.0")
        self.sweep_step_var = tk.StringVar(value="0.0")

        tk.Entry(sweep_frame, textvariable=self.sweep_start_var).grid(row=0, column=1)
        tk.Entry(sweep_frame, textvariable=self.sweep_stop_var).grid(row=1, column=1)
        tk.Entry(sweep_frame, textvariable=self.sweep_step_var).grid(row=2, column=1)

        self.sweep_button = tk.Button(
            sweep_frame,
            text="Run Sweep",
            command=self._run_sweep_cmd,
            bg="blue",
            fg="white"
        )
        self.sweep_button.grid(row=3, column=0, columnspan=2, pady=2, sticky="ew")

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
        output_frame.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky='nsew')

        self.output_text = tk.Text(output_frame, height=10, state='disabled', wrap='word', font=('Consolas', 9))
        self.output_text.pack(side='left', fill='both', expand=True)

        output_scrollbar = tk.Scrollbar(output_frame, command=self.output_text.yview)
        output_scrollbar.pack(side='right', fill='y')
        self.output_text['yscrollcommand'] = output_scrollbar.set

        main_frame.grid_columnconfigure(0, weight=2)
        main_frame.grid_columnconfigure(1, weight=1)
        # dedicated column for the plot_frame
        main_frame.grid_columnconfigure(2, weight=2)
        main_frame.grid_rowconfigure(1, weight=2)
        main_frame.grid_rowconfigure(2, weight=2)

        # setting current source as default mode
        self.simulator.set_source_mode("current")
        self._log_message("Default source mode set to current")

        """ creating a plot frame """
        plot_frame = tk.LabelFrame(main_frame, text="Live IV Plot", padx=5, pady=5)
        plot_frame.grid(row=1, column=2, rowspan=2, padx=5, pady=5, sticky="nsew")
            # creating the Figure and embedding into GUI
        self.fig, self.ax = plt.subplots(figsize=(5,4))

        self.ax.set_title("I-V Characteristic")
        self.ax.set_xlabel("Voltage (V)")
        self.ax.set_ylabel("Cuurent (A)")

        self.line, = self.ax.plot([], [], marker="o")

        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    # command handler
    def _set_source_mode_cmd(self):
        mode = self.source_mode_var.get()

        self._last_measurement = {
            "voltage_measured": 0.0,
            "current_measured": 0.0,
            "voltage_setpoint": 0.0,
            "current_setpoint": 0.0,
            "mode": mode,
            "resistance": 0.0,
            "compliance": False
        }
        try:
            self.simulator.set_source_mode(mode)
            self._log_message(f"GUI: Source mode set to {mode}")

        except Exception as e:
            self._log_message(f"Error setting source mode: {e}")

        # label updates for user to know which parameter is active
        if mode == "voltage":
            self._current_setpoint = 0.0
            self.voltage_entry.config(state="normal")
            self.current_entry.config(state="disabled")

            self.sweep_button.config(state="normal")

        else:
            self._voltage_setpoint = 0.0
            self.voltage_entry.config(state="disabled")
            self.current_entry.config(state="normal")

            # eliminating the sweep option in Current Source mode
            self.sweep_button.config(state="disabled")

        # resetting setpoints values
        self._update_gui_status()

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
            self._log_message("Turn OUTPUT ON to measure.")
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

    def _toggle_output_cmd(self):
        ''' controls new single button OUTPUT indicator '''
        if self.simulator.is_output_on():
            self.simulator.output_off()
            self._log_message("GUI: Output OFF command sent.")
        else:
            self.simulator.output_on()
            self._log_message("GUI: Output ON command sent.")

        self._update_gui_status()

    def _measure_cmd(self):

        # ensuring output ON before every measurement
        if not self.simulator.is_output_on():
            self._log_message("Warning: Output is OFF, Enable output before a measurement. ")
            return

        measurements = self.simulator.measure()

        self.simulator.output_off()
        self._update_gui_status()

        self.measured_voltage_var.set(
            f"Measured V: {measurements['voltage_measured']:.6f} V"
        )
        self.measured_current_var.set(
            f"Measured I: {measurements['current_measured']:.10f} A"
        )

        if measurements['resistance'] == float('inf'):
            self.measured_resistance_var.set("Measured R: INF Ohm")
        else:
            self.measured_resistance_var.set(
                f"Measured R: {measurements['resistance']:.2f} Ohm"
            )

        self._update_gui_status()

        self._log_message(
            f"GUI: Measurement - "
            f"Vset={measurements['voltage_setpoint']:.6f} V | "
            f"Vmeas={measurements['voltage_measured']:.6f} V, "
            f"Iset={measurements['current_setpoint']:.10f} A |"
            f"Imeas={measurements['current_measured']:.10f} A "
            f"R={measurements['resistance']:.2f} Ohm"
        )

        # resetting variables label to 0
        self.voltage_setpoint_var.set(0.0)
        self.current_setpoint_var.set(0.0)

        self._last_measurement = {
            "voltage_measured": 0.0,
            "current_measured": 0.0,
            "voltage_setpoint": 0.0,
            "current_setpoint": 0.0,
            "mode": None,
            "resistance": 0.0,
            "compliance": False
        }

        # for safety, automatically turn output OFF post measurement
        self.simulator.output_off()
        self._update_gui_status()

    # sweep command
    def _run_sweep_cmd(self):

        # ensuring sweep is ran in the correct source mode
        if self.source_mode_var.get() != "voltage":
            self._log_message("Sweep requires Voltage Source mode. Please change mode and try again.")

        # ensuring output ON before every measurement
        if not self.simulator.is_output_on():
            self._log_message("Warning: Output is OFF, Enable output before voltage sweep. ")
            return

        # disabling a sweep if parameters are empty
        if not self.sweep_start_var.get():
            self._log_message("GUI: Sweep start not set.")
            return


        # prevents old data from staying on the screen
        self.ax.clear()
        self.ax.set_title("I-V Characteristic")
        self.ax.set_xlabel("Voltage (V)")
        self.ax.set_ylabel("Current (A)")

        self.line, = self.ax.plot([], [], marker="o")
        self.canvas.draw()

        self._update_gui_status()
        self._log_message("GUI: Output ON for sweep.")

        try:
            start = float(self.sweep_start_var.get())
            stop = float(self.sweep_stop_var.get())
            step = float(self.sweep_step_var.get())

            #debugging
            print("STORING SWEEP PARAMS:", start, stop, step)

            # storing sweep parameters at execution time
            self.last_sweep_params = {
                "start": start,
                "stop": stop,
                "step": step
            }

            self._log_message(
                f"GUI: Starting sweep {start} -> {stop} V step {step}"
            )

            # safety measures pre and post a sweep
            self.simulator.output_on()
            self._update_gui_status()

            data = self.simulator.voltage_sweep(start, stop, step)

            self.simulator.output_off()
            self._update_gui_status()

            self.last_sweep_data = data

            self._log_message("GUI: Sweep complete")

            voltages = []
            currents = []

            for point in data:
                v = point["voltage_measured"]
                i = point["current_measured"]

                voltages.append(v)                              # append actual read_in_voltage and read_in_current and use those for plotting
                currents.append(i)
                # set and update plot
                self.line.set_data(voltages, currents)
                self.ax.relim()
                self.ax.autoscale_view()

                self.canvas.draw()

                self._log_message(
                    f"Sweep: V={v:.6f}V , I={i:.10f}A "
                )
                self.master.update()

        except ValueError:
            self._log_message("GUI: Invalid sweep parameters")

        # clearing variable input after a sweep
        self.sweep_start_var.set("0.0")
        self.sweep_stop_var.set("0.0")
        self.sweep_step_var.set("0.0")

        # turning output off post sweep
        self.simulator.output_off()
        self._update_gui_status()
        self._log_message("GUI: Output OFF after sweep")

    def _update_gui_status(self):

        if self.simulator.is_output_on():
            self.output_status_var.set("Output: ON (Active)")

            self.output_button.config(
                text="OUTPUT ON",
                bg="green",
                fg="white"
            )

        else:
            self.output_status_var.set("Output: OFF (Inactive)")

            self.output_button.config(
                text="OUTPUT OFF",
                bg="red",
                fg="white"
            )

        last_meas = self.simulator.get_last_measurement()

        # indicate compliance processes
        if last_meas['compliance']:
            self.output_status_var.set("Output: OFF (Compliance Activated)")
            self._log_message(f"GUI: {last_meas['mode']} compliance limit reached. Adjusted {last_meas['mode']} used.")

        self.measured_voltage_var.set(
            f"Vset: {last_meas['voltage_setpoint']:.6f} V | "
            f"Vmeas: {last_meas['voltage_measured']:.6f} V"
            )
        self.measured_current_var.set(
                f"Iset: {last_meas['current_setpoint']:.6f} A | "
                f"Imeas: {last_meas['current_measured']:.6f} A"
            )

        if last_meas['resistance'] == float('inf'):
            self.measured_resistance_var.set("Measured R: INF Ohm")
        else:
            self.measured_resistance_var.set(
                f"Measured R: {last_meas['resistance']:.6f} Ohm"
            )


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

                params = getattr(self, "last_sweep_params", None)
                if params:
                    start = params["start"]
                    stop = params["stop"]
                    step = params["step"]
                else:
                    start = stop = step = "N/A"

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

        # clearing variable input after saving data
        self.sweep_start_var.set("0.0")
        self.sweep_stop_var.set("0.0")
        self.sweep_step_var.set("0.0")

    def _log_message(self, message):
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        log_entry = f"{timestamp} {message}\n"
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, log_entry)
        self.output_text.see(tk.END)
        self.output_text.config(state='disabled')
