import tkinter as tk
from gui.gui import SourcemeterGUI
from keithley.hardware_socket import Keithley2450Hardware

def main():
    """
    entry point for launching the Sourcemeter GUI
    """
    # create Tkinter root window
    root = tk.Tk()

    # chooose device implementation
    device = Keithley2450Hardware("TCPIP0::192.168.50.200::5025::SOCKET")
    device.connect()

    #create GUI
    app = SourcemeterGUI(root, device)

    # start GUI loop
    root.mainloop()

if __name__ == "__main__":
    main()
