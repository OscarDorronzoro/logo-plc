import snap7
from snap7.util import *
#from snap7.type import *


client = snap7.logo.Logo()
LOGO_MAC = '' # Buscar IP via ARP 
LOGO_IP = '192.168.0.5'
RACK = 0
SLOT = 1
TCP_PORT = 102

client.connect(LOGO_IP, RACK, SLOT, TCP_PORT)
print("connection OK")

#while True:
#    print(client.read('I1'))
#    time.sleep(1)

# Is 923

#Qs 942

#Ms 948
data = 0b11111001
var = 'V0'
client.write(var, data)

for i in range(8):
    print(f'Variable {var}.{i} vale:', client.read(f'{var}.{i}'))



