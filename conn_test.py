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

var = 'V0.0'
client.write(var, 0)
print(client.read(var))
       
print('ingreso A', client.read('V1.2'))
print('salida A', client.read('V1.4'))
print('ingreso B', client.read('V1.3'))
print('salida B', client.read('V1.5'))

print('ingreso A', client.read('V2.0'))
print('salida A', client.read('V2.1'))
print('ingreso B', client.read('V2.2'))
print('salida B', client.read('V2.3'))



