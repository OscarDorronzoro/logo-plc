# Only for testing
'''
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'testing'))
import rfid.testing.serial as serial
'''

import serial
from serial.tools import list_ports
import socket

# Define the base class for readers
class Reader:
    def __init__(self):
        self.reader = None

    def read(self, size):
        raise NotImplementedError("Subclasses must implement this method")
    
    def write(self, data):
         raise NotImplementedError("Subclasses must implement this method")
    
    def close(self):
        if self.reader:
            self.reader.close()

# Define the SerialReader class
class SerialReader(Reader):
    def __init__(self, port):
        super().__init__()
        self.reader = serial.Serial(port=port, baudrate=9600, bytesize=8, timeout=5, stopbits=serial.STOPBITS_ONE)

    def read(self, size=14):
        return self.reader.read(size)

    def write(self, data):
        self.reader.write(data)

# Define the TCPReader class
class TCPReader(Reader):
    def __init__(self, port):
        super().__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('0.0.0.0', port))
        self.socket.listen(4) # Maximun 4 connections
    
    def read(self, size=14):
        conn, addr = self.socket.accept()
        self.reader = conn

        data = self.reader.recv(size) # test: nc localhost 10000 < tcp_rfid_probe.txt
        return data

    def write(self, data):
        self.reader.send(data)
        self.close()

# Define the ReaderFactory class
class ReaderFactory:
    serial_available_ports = []
    tcp_available_ports = []

    @staticmethod
    def autodetect_ports():
        #ports = [type('', (), {'name':'COM3', 'description': 'Port COM3', 'serial_number': 'A5069RR4A'})(), type('', (), {'name':'COM4', 'description': 'Port COM4', 'serial_number': 'A5069RR4A'})()]
        ports = list_ports.comports()

        for p in ports:
            print(f'{p.name} - {p.description} -- {p.serial_number}')

            port_name = ''
            if p.serial_number and p.serial_number.__contains__('A5069RR4'):
                if p.name.__contains__('ttyUSB'):
                    port_name = f'/dev/{p.name}'
                else:
                    port_name = p.name
                ReaderFactory.serial_available_ports.append(port_name)
   
        # TCP (default ports to listen on for exemys)
        ReaderFactory.tcp_available_ports.append(10000)
        ReaderFactory.tcp_available_ports.append(10001)

    @staticmethod
    def get_reader(reader_type):
        if reader_type == "serial":
            if len(ReaderFactory.serial_available_ports) == 0:
                raise Exception('No readers connected over serial port')
            return SerialReader(ReaderFactory.serial_available_ports.pop(0))
        elif reader_type == "tcp":
            if len(ReaderFactory.tcp_available_ports) == 0:
                raise Exception('No readers connected over TCP')
            return TCPReader(ReaderFactory.tcp_available_ports.pop(0))
        else:
            raise ValueError("Invalid reader type")

# Example usage
if __name__ == "__main__":
    # Create a SerialReader instance
    serial_reader = ReaderFactory.get_reader("serial")
    print(serial_reader.read())  # Output: Reading from serial port

    # Create a TCPReader instance
    tcp_reader = ReaderFactory.get_reader("tcp")
    print(tcp_reader.read())  # Output: Reading from TCP connection

    # Try to create an invalid reader type
    try:
        invalid_reader = ReaderFactory.get_reader("invalid")
    except ValueError as e:
        print(e)  # Output: Invalid reader type
