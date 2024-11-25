# utils.py

import platform
import serial.tools.list_ports

def find_serial_port():
    """
    Automatically find the correct serial port for the device across different operating systems.

    Returns:
        str: The path of the detected serial port, or None if not found.
    """
    system = platform.system()
    ports = list(serial.tools.list_ports.comports())

    for port in ports:
        if system == "Darwin":  # macOS
            if any(identifier in port.device.lower() for identifier in ["usbserial", "cu.usbmodem", "tty.usbserial"]):
                return port.device
        elif system == "Windows":
            if "com" in port.device.lower():
                return port.device
        elif system == "Linux":
            if "ttyUSB" in port.device or "ttyACM" in port.device:
                return port.device

    return None