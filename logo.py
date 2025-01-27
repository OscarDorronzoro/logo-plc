import tkinter as tk
import snap7
from snap7.util import *
from snap7.type import *
import threading
import time

# Instalar dependencias
# pip install tkinder python-snap7

# Contantes
signals_mem = {
            'hab_entrar_A': 0,
            'hab_entrar_B': 1,
            'lista_pesada': 2,
            'camion_a_balanza': 3,
            'balanza_en_cero': 4,
            'listo': 5,
            'listo_pesar': 6
        }


client = snap7.client.Client()
LOGO_MAC = '' # Buscar IP via ARP 
LOGO_IP = '192.168.0.4'
RACK = 0
SLOT = 1
PORT = 102

client.connect(LOGO_IP, RACK, SLOT)

def write_memory(marker, state):
  memory = client.read_area(Areas.MK, 0, 0, 1)
  memory = set_bool(memory, 0, marker, state)
  client.write_area(Areas.MK, 0, 0, memory)

def read_status():
    return client.read_area(Areas.PA, 0, 0, 1)

# Definicion de UI
app = tk.TK()
app.title('Control de bascula')

control_labels = []

def create_app_control(label_name, mem_index)
    control_label = tk.Label(app, text=label_name, fg='black')
    control_label.pack()
    control_labels.append(control_label)

    on_button = tk.Button(app, text=f'Activar {label_name}', command=lambda: write_memory(mem_index, True), bg='lime')
    on_button.pack()

    off_button = tk.Button(app, text=f'Desactivar {label_name}', command=lambda: write_memory(mem_index, False), bg='red')
    off_button.pack()

def read_logo_signals_status():
    while True:
        status = read_status()

create_app_control('Hab. entrar A', signals_mem['hab_entrar_A'])
create_app_control('Hab. entrar B', signals_mem['hab_entrar_B'])
create_app_control('Lista pesada', signals_mem['listo_pesada'])
create_app_control('Camion a balanza', signals_mem['camion_a_balanza'])
create_app_control('Balanza en cero', signals_mem['balanza_en_cero'])
create_app_control('Listo', signals_mem['listo'])
create_app_control('Listo pesar', signals_mem['listo_pesar'])

read_signals_thread = threading.Thread(target=read_logo_signals_status, daemon=True)
read_signals_thread.start()

app.mainloop()

client.disconnect()

