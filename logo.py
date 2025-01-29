import tkinter as tk
import snap7
from snap7.util import *
from snap7.types import *
import threading
import time

# Instalar dependencias
# pip install python-snap7
# sudo add-apt-repository ppa:gijzelaar/snap7
# sudo apt update
# sudo apt install libsnap7-1 libsnap7-dev
# sudo apt-get install python3-tk

# Levantar servidor falso s7
# python3 -m snap7.server --port 102

# Configurar red
# sudo ip address flush dev enp9s0
# sudo ip route flush dev enp9s0
# sudo ip address add 192.168.0.5/24 brd + dev enp9s0
# sudo ip route add 192.168.0.1 dev enp9s0
# sudo ip route add default via 192.168.0.1 dev enp9s0
# ip a s dev enp9s0


# Constantes
signals_M = {
            # Escritura de pc a logo
            'hab_general': 'V0.0', #M1
            'reajuste': 'V0.1', #M2 (reservada)
            'hab_entrar_A': 'V0.2', #M3
            'hab_entrar_B': 'V0.3', #M4
            'camion_en_balanza': 'V948.4', #M5
            'fin_pesada': 'V948.5', #M6
            'balanza_en_cero': 'V948.6', #M7
            
            # Uso interno
            'uso_interno_1': 'V948.7', #M8
            
            # Lectura de logo a pc
            'listo': 'V949.0', #M9
            'ingreso_A': 'V949.1', #M10
            'ingreso_B': 'V949.2', #M11
            'listo_para_pesar': 'V949.3', #M12
            'salida_A': 'V948.4', #M13
            'salida_B': 'V948.5' #M14
        }

signals_I = {
            'barrera_A': 'V923.0', #I1
            'barrera_B': 'V923.1' #I2
        }

signals_Q = {
            'semaforo_ingreso_A': 'V942.0', #Q1
            'semaforo_salida_A': 'V942.1', #Q2
            'semaforo_ingreso_B': 'V942.2', #Q3
            'semaforo_salida_B': 'V942.3', #Q4
        }

PESO_CAMION = 5000 # Para calcular si hay un camion en la balanza

client = snap7.logo.Logo()
LOGO_MAC = '8C:F3:19:B5:40:16' # Buscar IP via ARP?
LOGO_IP = '192.168.0.5'
#LOGO_IP = '127.0.0.1'
RACK = 0
SLOT = 1
TCP_PORT = 102 # default

client.connect(LOGO_IP, RACK, SLOT, TCP_PORT)
print('Conexion con logo... OK')

def write_memory(addr, bit_pos, value):
    current_byte = client.read(addr)

    if value == 0: # and 
        bit_mask = 255 - 2**bit_pos
        current_byte = current_byte & bit_mask

    if value == 1: # or
        bit_mask = 2**bit_pos
        current_byte = current_byte | bit_mask
    
    client.write(addr, bit_mask)

def write_memory_2(addr_bit, value):
    addr = addr_bit.split('.')[0]
    bit_pos = addr_bit.split('.')[1]
    write_memory(addr, bit_pos, value)

def read_status():
    # Ms V948
    status = {}
    for var in signals_M:
        status[var] = client.read(f'{var}')
    
    return status
    
def read_status_print():
    # Is V923
    for var in signals_I:
        print(f'Variable {var}:', client.read(f'{var}'))
    
    # Qs V942
    for var in signals_Q:
        print(f'Variable {var}:', client.read(f'{var}'))
    
    # Ms V948
    for var in signals_M:
        print(f'Variable {var}:', client.read(f'{var}'))

# Definicion de UI
app = tk.Tk()
app.title('Control de Bascula')

control_labels = {}

def create_app_control(label_name, signal):
    control_label = tk.Label(app, text=label_name, fg='black')
    control_label.pack()
    control_labels[signal] = control_label

    signal_byte = signals_M[signal].split('.')
    addr = signal_byte[0]
    bit_pos= signal_byte[1]

    on_button = tk.Button(app, text=f"Activar {label_name}", command=lambda: write_memory(addr, bit_pos, 1), bg='lime')
    on_button.pack()

    off_button = tk.Button(app, text=f"Desactivar {label_name}", command=lambda: write_memory(addr, bit_pos, 0), bg='red')
    off_button.pack()

def read_logo_signals_status():
    while True:
        status = read_status()
        for key in control_labels.keys():
            text_color = 'lime'
            if status[key] == 0:
                text_color = 'red'
            control_labels[key].config(fg=text_color)
        time.sleep(1)

def on_spin_change():
    valor_pesaje = int(spin_pesaje.get())
    if valor_pesaje == 0:
        print('balanza en cero')
        client.write(signals_M['camion_en_balanza'], 0)
        client.write(signals_M['balanza_en_cero'], 1)
    if valor_pesaje > PESO_CAMION:
        print('cambion en balanza')
        client.write(signals_M['camion_en_balanza'], 1)
        client.write(signals_M['balanza_en_cero'], 0)

create_app_control('Hab. general', 'hab_general')
create_app_control('Hab. entrar A', 'hab_entrar_A')
create_app_control('Hab. entrar B', 'hab_entrar_B')
create_app_control('Camion en balanza', 'camion_en_balanza')
create_app_control('Fin pesada', 'fin_pesada')
create_app_control('Balanza en cero', 'balanza_en_cero')

spin_pesaje = tk.Spinbox(app, from_=0, to=65000, command=on_spin_change)
spin_pesaje.pack()

read_signals_thread = threading.Thread(target=read_logo_signals_status, daemon=True)
read_signals_thread.start()

app.mainloop()

client.disconnect()

