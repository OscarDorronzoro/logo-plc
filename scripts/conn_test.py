import snap7
from snap7.util import *
#from snap7.type import *
from pymodbus.client.sync import ModbusTcpClient

#client = snap7.logo.Logo()
LOGO_MAC = '' # Buscar IP via ARP 
LOGO_IP = '192.168.0.5'
#LOGO_IP = '127.0.0.1'
RACK = 0
SLOT = 1
TCP_PORT = 102

print(LOGO_IP, '-------------------------------------')
#client.connect(LOGO_IP, RACK, SLOT, TCP_PORT)
#print("connection OK")

#while True:
#    print(client.read('I1'))
#    time.sleep(1)

# Is 923

#Qs 942

#Ms 948


# Constants
signals_writing = {
    # Write from PC to Logo!
    'hab_general': 'V0.0', # Continous signal
    'balanza_en_cero': 'V0.1', # Continoues signal
    'hab_entrar_A': 'V0.2', # Pulse, RFID by A
    'hab_entrar_B': 'V0.3', # Pulse, RFID by B
    'camion_en_balanza': 'V0.4', # Continuos signal
    'fin_pesada': 'V0.5' # Pulse
}

client = ModbusTcpClient(LOGO_IP, port=510)
is_conn_OK = client.connect()

def s7_to_modbus_coil(addr):
    modbus_offset = 0
    addr_splitted = addr.replace('V', '').split('.')
    coil_number = int(addr_splitted[0])*8 + int(addr_splitted[1]) + modbus_offset
    return coil_number

def read(client, addr):
    coil = int(addr) #s7_to_modbus_coil(addr)
    response = client.read_coils(coil, 1)
    return response.bits[0]

def write(client, addr, data):
    coil = int(addr) #s7_to_modbus_coil(addr)
    client.write_coil(coil, bool(data))


write(client, '0', False)
write(client, '1', False)
write(client, '2', True)
write(client, '3', True)
write(client, '4', True)
write(client, '5', True)

print('ingreso A', read(client, 'V0.0'))
print('salida A', read(client, 'V0.1'))
print('ingreso B', read(client, 'V0.2'))
print('salida B', read(client, 'V0.3'))
print('ingreso B', read(client, 'V0.4'))
print('salida B', read(client, 'V0.5'))



