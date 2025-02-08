# mock_serial/tools/list_ports.py

from typing import List

class MockPortInfo:
    def __init__(self, name, description, serial_number):
        self.name = name
        self.description = description
        self.serial_number = serial_number

    def __repr__(self):
        return f"MockPortInfo(name={self.name}, description={self.description}, serial_number={self.serial_number})"

def comports() -> List[MockPortInfo]:
    # Simulate a list of available ports
    mock_ports = [
        ("COM3", "Mock USB Serial Port (COM3)", "A5069RR4"),
        ("COM4", "Mock USB Serial Port (COM4)", "A5069RR5"),
    ]
    return [MockPortInfo(*port) for port in mock_ports]
