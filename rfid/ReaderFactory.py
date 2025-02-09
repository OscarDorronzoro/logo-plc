import serial
import socket

# Define the base class for readers
class Reader:
    def __int__(self):
        self.reader = None

    def read(self, size):
        raise NotImplementedError("Subclasses must implement this method")
    
    def write(self, data):
         raise NotImplementedError("Subclasses must implement this method")
    
    def close(self)
        print(type(self.reader))
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

    #def close(self):
    #    reader.close()

# Define the TCPReader class
class TCPReader(Reader):
    def __init__(self, port):
        super().__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('localhost', port))
        self.socket.listen(4) # Maximun 4 connections
    
    def read(self, size=14):
        conn, addr = self.socket.accept()
        self.reader = conn

        return self.reader.recv(size)

    def write(self, data):
        self.reader.send(data)
    
    #def close(self):
    #    self.reader.close()

# Define the ReaderFactory class
class ReaderFactory:
    
    @staticmethod
    def get_reader(reader_type):
        if reader_type == "serial":
            return SerialReader()
        elif reader_type == "tcp":
            return TCPReader()
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
