import random
import csv
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import AutoMinorLocator
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
        ''' Main frame to house all the GUI objects'''

        main_frame = tk.Frame(self.master, padx=10, pady=10)
        main_frame.pack(fill='both', expand=True)

        source_frame = tk.LabelFrame(
            main_frame,
            text="SOURCE CONFIGURE",
            padx=10,
            pady=10
        )

        source_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # create a mode selection toggle
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
        control_frame = tk.LabelFrame(main_frame, text="CONTROLS", padx=10, pady=10)
        control_frame.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

        tk.Button(control_frame, text="Set Voltage", command=self._set_voltage_cmd, state="disabled").grid(row=0, column=0, padx=5, pady=2, sticky='ew')
        tk.Button(control_frame, text="Set Current", command=self._set_current_cmd).grid(row=1, column=0, padx=5, pady=2, sticky='ew')


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

        ''' version 0.01 of voltage sweep. Will integrate it to standards of current sweep.
            After finalizing current source mode
        '''
        # sweep controls
        # sweep_frame = tk.LabelFrame(main_frame, text="Voltage Sweep", padx=10, pady=10)
        # sweep_frame.grid(row=0, column=2, padx=5, pady=5, sticky='ew')
        #
        # tk.Label(sweep_frame, text="Start (V):").grid(row=0, column=0)
        # tk.Label(sweep_frame, text="Stop (V):").grid(row=1, column=0)
        # tk.Label(sweep_frame, text="Step (V):").grid(row=2, column=0)
        #
        # self.sweep_start_var = tk.StringVar(value="0.0")
        # self.sweep_stop_var = tk.StringVar(value="0.0")
        # self.sweep_step_var = tk.StringVar(value="0.0")
        #
        # tk.Entry(sweep_frame, textvariable=self.sweep_start_var).grid(row=0, column=1)
        # tk.Entry(sweep_frame, textvariable=self.sweep_stop_var).grid(row=1, column=1)
        # tk.Entry(sweep_frame, textvariable=self.sweep_step_var).grid(row=2, column=1)
        #
        # self.sweep_button = tk.Button(
        #     sweep_frame,
        #     text="Run Sweep",
        #     command=self._run_sweep_cmd,
        #     bg="blue",
        #     fg="white"
        # )
        # self.sweep_button.grid(row=3, column=0, columnspan=2, pady=2, sticky="ew")
        #
        # # saving data button
        # tk.Button(
        #     sweep_frame,
        #     text="Save Data",
        #     command=self._save_data_cmd,
        #     bg="blue",
        #     fg="white"
        # ).grid(row=4, column=0, columnspan=2, pady=2, sticky="ew")

        sweep_frame = tk.LabelFrame(main_frame, text="SWEEP", padx=10, pady=10)
        sweep_frame.grid(row=0, column=2, rowspan=2, padx=5, pady=5, sticky="nsew")

        # -------------------------------------
        # VOLTAGE SWEEP
        # -------------------------------------
        v_sweep_frame = tk.LabelFrame(sweep_frame, text="Voltage Sweep", padx=8, pady=8)
        v_sweep_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.start_voltage_var = tk.StringVar(value="0.0")
        self.stop_voltage_var = tk.StringVar(value="0.0")
        self.step_voltage_var = tk.StringVar(value="0.0")

        tk.Label(v_sweep_frame, text="Start (V):").grid(row=0, column=0, sticky="w")
        tk.Entry(v_sweep_frame, textvariable=self.start_voltage_var, width=10).grid(row=0, column=1, pady=2)

        tk.Label(v_sweep_frame, text="Stop (V):").grid(row=1, column=0, sticky="w")
        tk.Entry(v_sweep_frame, textvariable=self.stop_voltage_var, width=10).grid(row=1, column=1, pady=2)

        tk.Label(v_sweep_frame, text="Step (V):").grid(row=2, column=0, sticky="w")
        tk.Entry(v_sweep_frame, textvariable=self.step_voltage_var, width=10).grid(row=2, column=1, pady=2)

        # VOLTAGE SWEEP button
        tk.Button(
            v_sweep_frame,
            text="Run V Sweep",
            command=self._run_voltage_sweep_cmd
        ).grid(row=3, column=0, columnspan=2, pady=5, sticky="ew" )

        # -------------------------------------
        # CURRENT SWEEP
        # -------------------------------------

        i_sweep_frame = tk.LabelFrame(sweep_frame, text="Current Sweep", padx=8, pady=8)
        i_sweep_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.start_current_var = tk.StringVar(value="0.0")                                                 # current sweep parameters
        self.stop_current_var = tk.StringVar(value="0.0")
        self.step_current_var = tk.StringVar(value="0.0")

        tk.Label(i_sweep_frame, text="Start (A):").grid(row=0, column=0, sticky="w")
        tk.Entry(i_sweep_frame, textvariable=self.start_current_var, width=10).grid(row=0, column=1, pady=2)

        tk.Label(i_sweep_frame, text="Stop (A):").grid(row=1, column=0, sticky="w")
        tk.Entry(i_sweep_frame, textvariable=self.stop_current_var, width=10).grid(row=1, column=1, pady=2)

        tk.Label(i_sweep_frame, text="Step (A):").grid(row=2, column=0, sticky="w")
        tk.Entry(i_sweep_frame, textvariable=self.step_current_var, width=10).grid(row=2, column=1, pady=2)

        # current sweep button
        self.current_sweep_button = tk.Button(
            i_sweep_frame,
            text="Run I Sweep",
            command=self._run_current_sweep_cmd
        )
        self.current_sweep_button.grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")

        # -------------------------------
        # SHARED SAVE BUTTON
        # ------------------------------

        self.save_button = tk.Button(
            sweep_frame,
            text="Save Data",
            bg = "blue",
            command=self._save_data_cmd
        )
        self.save_button.grid(row=1, column=0, columnspan=2, pady=8, sticky="ew")

        # -----------------
        # RESIZE CONFIG
        # -----------------
        sweep_frame.grid_columnconfigure(0, weight=1)
        sweep_frame.grid_columnconfigure(1, weight=1)

        control_frame.grid_columnconfigure(0, weight=1)

        # -----------------------------------
        # SINGLE MEASUREMENT FRAME, OUTPUT LOG
        # -----------------------------------
        status_frame = tk.LabelFrame(main_frame, text="SINGLE MEASUREMENT", padx=10, pady=10)
        status_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='ew')

        tk.Label(status_frame, textvariable=self.output_status_var, font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        tk.Label(status_frame, textvariable=self.measured_voltage_var, font=('Arial', 10)).grid(row=1, column=0, padx=5, pady=2, sticky='w')
        tk.Label(status_frame, textvariable=self.measured_current_var, font=('Arial', 10)).grid(row=2, column=0, padx=5, pady=2, sticky='w')
        tk.Label(status_frame, textvariable=self.measured_resistance_var, font=('Arial', 10)).grid(row=3, column=0, padx=5, pady=2, sticky='w')

        status_frame.grid_columnconfigure(0, weight=1)

        output_frame = tk.LabelFrame(main_frame, text="OUTPUT LOG", padx=5, pady=5)
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

        # ---------------------------------
        # PLOT FRAMEWORK
        # ----------------------------------
        plot_frame = tk.LabelFrame(main_frame, text="I-V PLOT", padx=5, pady=5)
        plot_frame.grid(row=1, column=2, rowspan=2, padx=5, pady=5, sticky="nsew")
        self.fig, self.ax = plt.subplots(figsize=(5,4))                         # creating the Figure and embedding into GUI

        self.fig.patch.set_facecolor("black")                                   # make plot background dark
        self.ax.set_facecolor("black")

        # Main trace; keithley green style
        self.line, = self.ax.plot([], [], color="lime", marker="o", markerfacecolor="lime", markeredgecolor="lime", markersize=4, linewidth=1.5)
        # labels
        self.ax.set_title("I-V Characteristic", color="white")
        self.ax.set_xlabel("Voltage (V)", color="white")
        self.ax.set_ylabel("Current (A)", color="white")

        # tick colors
        self.ax.tick_params(axis="both", colors="white")

        # spines (border)
        for spine in self.ax.spines.values():
            spine.set_color("white")

        # minor ticks
        self.ax.xaxis.set_minor_locator(AutoMinorLocator(5))
        self.ax.yaxis.set_minor_locator(AutoMinorLocator(5))

        # grid
        self.ax.grid(True, which="major", linestyle="--", linewidth=0.5, alpha=0.35)
        self.ax.grid(True, which="minor",linestyle=":", linewidth=0.3, alpha=0.20)

        # zero reference lines
        self.ax.axhline(0, linewidth=0.8)
        self.ax.axvline(0, linewidth=0.8)

        self.fig.tight_layout()                                                 # tight layout

        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    # --------------------------
    # VARIABLE SETTERS
    # ---------------------------
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

    # ----------------------------------------------
    # OUTPUT SYSTEM STATE
    # -----------------------------------------------

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

    # ---------------------------------------
    # GUI MEASURE
    # ----------------------------------------
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

    # ----------------------------
    # SWEEPS: VOLTAGE AND CURRENT
    # --------------------------
    def _run_voltage_sweep_cmd(self):
        ''' Sweep the voltage based on start, step and stop values'''

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

        self.line, = self.ax.plot([], [], marker="o", color="green")
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

    def _run_current_sweep_cmd(self):
        ''' GUI handler for Current Sweep button.
            Reads entry fields, calls backend current_sweep(),
            updates plot, log and status.
        '''
        try:
            start = float(self.start_current_var.get())
            stop = float(self.stop_current_var.get())
            step = float(self.step_current_var.get())

            # store sweep parameters
            self.last_sweep_params = {
                "start": start,
                "stop": stop,
                "step": step
            }

            if step <= 0:
                self._log_message("GUI: Step must be greater than zero")
                return

            # log start of sweep
            self._log_message(
                f"GUI: Starting current sweep "
                f"from {start:.6f} A to {stop:.6f} A "
                f"in steps of {step:.6f} A"
            )

            self.current_sweep_button.config(state="disabled")                  # disable sweep button while sweeping

            results = self.simulator.current_sweep(start, stop, step)           # run backend sweep

            self.last_sweep_data = results

            # extract plot data X = voltage, Y = current
            voltages = [m["voltage_measured"] for m in results]
            currents = [m["current_measured"] for m in results]

            # update live plot
            self.line.set_data(voltages, currents)
            self.ax.relim()
            self.ax.autoscale_view()
            self.ax.margins(x=0.08, y=0.08)                                     # slight margin
            self.canvas.draw()

            self._update_gui_status()                                           # update UGI status

            # log completion
            self._log_message(
                f"GUI: Current sweep complete "
                f"({len(results)} points acquired)")

            # reset input boxes
            self.start_current_var.set("0.0")
            self.stop_current_var.set("0.0")
            self.step_current_var.set("0.0")
        except ValueError:
            self._log_message(
                "GUI: Invalid current sweep input. "
                "Please enter numeric values"
            )

        except Exception as e:
            self._log_message(f"GUI error: {str(e)}")

        finally:
            # re-enable button and set OUTPUT OFF
            self.current_sweep_button.config(state="normal")
            self.simulator.output_off()
            pass

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
                    print(point)
                    writer.writerow([
                        point["voltage_measured"],
                        point["current_measured"],
                        point["resistance"]
                    ])
            self._log_message(f"GUI: Data saved to {file_path}")

        except Exception as e:
            self._log_message(f"GUI: Error saving data {e}")

        # clearing variable input after saving data, was for initial VOLTAGE MODE
        #self.sweep_start_var.set("0.0")
        #self.sweep_stop_var.set("0.0")
        #self.sweep_step_var.set("0.0")

    def _update_gui_status(self):

        if self.simulator.is_output_on():
            self.output_status_var.set("Output: ON (Active)")

            self.output_button.config(
                text="OUTPUT ON",
                bg="blue",
                fg="black"
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
            self.output_status_var.set("Output: OFF (Compliance Limit)")
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


    def _log_message(self, message):
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        log_entry = f"{timestamp} {message}\n"
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, log_entry)
        self.output_text.see(tk.END)
        self.output_text.config(state='disabled')
