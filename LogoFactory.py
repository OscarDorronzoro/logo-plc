import snap7
from snap7.util import *
from snap7.types import *
from pymodbus.client.sync import ModbusTcpClient

# Define the base class for Logo! connections
class LogoConn:
    def __init__(self):
        self.client = None

    def connect(self, ip_address, port):
        raise NotImplementedError("Subclasses must implement this method")
    
    def read(self, addr):
        raise NotImplementedError("Subclasses must implement this method")

    def write(self, addr, data):
         raise NotImplementedError("Subclasses must implement this method")

    def close(self):
        if self.client:
            self.client.close()

# Define the SerialReader class
class S7(LogoConn):
    signals_writing = {
        'hab_general': 'V0.0', # Continous signal
        'balanza_en_cero': 'V0.1', # Continoues signal
        'hab_entrar_A': 'V0.2', # Pulse, RFID by A
        'hab_entrar_B': 'V0.3', # Pulse, RFID by B
        'camion_en_balanza': 'V0.4', # Continuos signal
        'fin_pesada': 'V0.5' # Pulse
    }

    signals_reading = {
        'en_servicio': 'V1.0'
        ,'listo': 'V1.1'
        ,'ingreso_A': 'V1.2'
        ,'ingreso_B': 'V1.3'
        ,'salida_A': 'V1.4'
        ,'salida_B': 'V1.5'
        ,'I1_barrera_A': 'V1.6'
        ,'I2_barrera_B': 'V1.7'
        ,'Q1_semaforo_A1': 'V.2.0'
        ,'Q2_semaforo_A2': 'V.2.1'
        ,'Q3_semaforo_B1': 'V.2.2'
        ,'Q4_semaforo_B2': 'V.2.3'
    }

    def __init__(self):
        super().__init__()
        self.rack = 0
        self.slot = 1
        self.client = snap7.logo.Logo()

    def connect(self, ip_address, port=102):
        try:
            self.client.connect(ip_address, self.rack, self.slot, port)
        except Exception as e:
            raise Exception(f'Unable to connect via S7 to {ip_address}:{port}')

    def read(self, addr):
        return int(self.client.read(addr))

    def write(self, addr, data):
        self.client.write(addr, int(data))

    def close(self):
        if self.client:
            self.client.disconnect()

# Define the TCPReader class
class Modbus(LogoConn):
    signals_writing = {
        'hab_general': '1', # Continous signal
        'balanza_en_cero': '2', # Continoues signal
        'hab_entrar_A': '3', # Pulse, RFID by A
        'hab_entrar_B': '4', # Pulse, RFID by B
        'camion_en_balanza': '5', # Continuos signal
        'fin_pesada': '6' # Pulse
    }

    signals_reading = {
        'en_servicio': '20'
        ,'listo': '21'
        ,'ingreso_A': '22'
        ,'ingreso_B': '23'
        ,'salida_A': '24'
        ,'salida_B': '25'
        ,'I1_barrera_A': '26'
        ,'I2_barrera_B': '27'
        ,'Q1_semaforo_A1': '28'
        ,'Q2_semaforo_A2': '29'
        ,'Q3_semaforo_B1': '30'
        ,'Q4_semaforo_B2': '31'
    }

    s7_to_modbus_mapping = {
        'V0.0': '1'
        ,'V0.1': '2'
        ,'V0.2': '3'
        ,'V0.3': '4'
        ,'V0.4': '5'
        ,'V0.5': '6'
        ,'V1.0': '20'
        ,'V1.1': '21'
        ,'V1.2': '22'
        ,'V1.3': '23'
        ,'V1.4': '24'
        ,'V1.5': '25'
        ,'V1.6': '26'
        ,'V1.7': '27'
        ,'V2.0': '28'
        ,'V2.1': '29'
        ,'V2.2': '30'
        ,'V2.3': '31'
    }
    
    def __init__(self):
        super().__init__()

    def connect(self, ip_address, port=502):
        self.client = ModbusTcpClient(ip_address, port=port)
        is_conn_OK = self.client.connect()
        if not is_conn_OK:
            raise Exception(f'Unable to connect via modbus to {ip_address}:{port}')

    def read(self, addr):
        response = self.client.read_coils(int(Modbus.s7_to_modbus_mapping[addr]), 1)
        # if not response.isError():
        return response.bits[0]

    def write(self, addr, data):
        self.client.write_coil(int(Modbus.s7_to_modbus_mapping[addr]), bool(data))

# Define the ReaderFactory class
class LogoFactory:
    @staticmethod
    def get_logo_conn(conn_type):
        if conn_type == "s7":
            return S7()
        elif conn_type == "modbus":
            return Modbus()
        else:
            raise ValueError("Invalid connection type")


if __name__ == '__main__':
    IP_ADDRESS = '127.0.0.1'
    
    # Create a Modbus TCP client
    client = LogoFactory.get_logo_conn('s7')
    client.connect(IP_ADDRESS)
    
    # Connect to the LOGO! PLC
    if True:
        print("Connected to LOGO! PLC")
    
        # Read a coil (e.g., V0.0 mapped to coil address 1)
        address = 'V0.0'
        response = client.read(address)
        print(f"Coil value at address {address}: {response}")
    
        # Write to a coil (e.g., set V0.0 to True)
        client.write(address, 1)
        print(f"Coil at address {address} set to True")
    
        # Read a coil (e.g., V0.0 mapped to coil address 1)
        address = 'V0.0'
        response = client.read(address)
        print(f"Coil value at address {address}: {response}")

        # Close the connection
        client.close()
        print("Disconnected from LOGO! PLC")
    else:
        print("Failed to connect to LOGO! PLC")
