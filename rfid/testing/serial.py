# mock_serial/serial.py
import time
import random

STOPBITS_ONE = 1

class Serial:

    def __init__(self, port=None, baudrate=9600, bytesize=8, timeout=5, stopbits=1):
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.timeout = timeout
        self.stopbits = stopbits
        self.is_open = True
        self._data_buffer = bytearray()

    def write(self, data):
        print(f"MockSerial: Writing data - {data.hex()}")
        # Simulate a response based on the input data
        '''
        if data == bytes.fromhex('a6 00 00 00 00 23 00 00 00 c8 00 00 00 4d'):
            self._data_buffer = bytearray.fromhex('a6 00 00 00 00 23 00 00 00 c8 00 00 00 4d')
        else:
            self._data_buffer = bytearray.fromhex('a6 00 00 00 00 23 00 00 01 c8 00 00 00 4c')
        '''

    def read(self, size=1):
        if not self._data_buffer:
            # Simulate reading an RFID card
            self._data_buffer = bytearray.fromhex('a6 00 0c 01 40 01 04 00 46 79 34 00 00 e5')
        data = self._data_buffer[:size]
        self._data_buffer = self._data_buffer[size:]
        time.sleep(5 + int(random.random()*10))
        return data

    def close(self):
        self.is_open = False
        print("MockSerial: Port closed")

    def is_open(self):
        return self.is_open
