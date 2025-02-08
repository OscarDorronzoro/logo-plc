import tkinter as tk
from tkinter import font
import snap7
from snap7.util import *
from snap7.types import *
import threading
import queue
import time
#from scapy.all import ARP, Ether, srp
#import pdb

# Instalar dependencias
# pip3 install python-snap7
# pip3 install scapy

# sudo add-apt-repository ppa:gijzelaar/snap7
# sudo apt update
# sudo apt install libsnap7-1 libsnap7-dev
# sudo apt-get install python3-tk

# Constantes
signals_writing = {
    # Escritura de pc a logo
    'hab_general': 'V0.0',
    'balanza_en_cero': 'V0.1',
    'hab_entrar_A': 'V0.2',
    'hab_entrar_B': 'V0.3',
    'camion_en_balanza': 'V0.4',
    'fin_pesada': 'V0.5'
}

signals_reading = {
    # Lectura de logo a pc
    #'en_servicio': 'V1.0',
    'listo': 'V1.1'
    ,'ingreso_A': 'V2.0'#'V1.2',
    ,'ingreso_B':'V2.2' #'V1.3',
    #'listo_para_pesar': 'V1.3',
    ,'salida_A': 'V2.1'#'V1.4',
    ,'salida_B': 'V2.3'#'V1.5'
    #,'I1_barrera_A': 'V1.6'
    #,'I2_barrera_B': 'V1.7'
    #,'Q1_semaforo_A1': 'V.2.0'
    #,'Q2_semaforo_A2': 'V.2.1'
    #,'Q3_semaforo_B1': 'V.2.2'
    #,'Q4_semaforo_B2': 'V.2.3'
}


PESO_CAMION = 4000 # Para calcular si hay un camion en la balanza

LOGO_MAC = '8C:F3:19:B5:40:16'
LOGO_IP = '192.168.0.5'
#LOGO_IP = '127.0.0.1'
RACK = 0
SLOT = 1
TCP_PORT = 102 # default

client = None

app = None
control_labels = {}
weight_scale = None
app_font = None
status_queue = None  # Thread-safe queue for status updates

def lookup_ip_address(mac_address):
    pass

def init():
    global client
    global app, app_font
    global status_queue
    
    # Connection with logo
    client = snap7.logo.Logo()
    client.connect(LOGO_IP, RACK, SLOT, TCP_PORT)
    print('Connection with logo... OK')
    
    # Threading
    status_queue = queue.Queue()

    # Initialize Tkinter UI
    app = tk.Tk()
    app.title('Control de Báscula')

    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()
    window_width = int(screen_width * 0.8)
    window_height = int(screen_height * 0.8)
    app.geometry(f"{window_width}x{window_height}+{int((screen_width - window_width) / 2)}+{int((screen_height - window_height) / 2)}")

    app_font = font.Font(size=14)

def read_memory(addr):
    return int(client.read(addr))

def write_memory(addr, bit_value):
    client.write(addr, int(bit_value))

def send_pulse(addr):
    write_memory(addr, 1)
    time.sleep(1)
    write_memory(addr, 0)

def toggle_memory(addr):
    value = read_memory(addr)
    write_memory(addr, not value)

def read_status():
    global signals_reading, signals_writing

    status = {}
    #pdb.set_trace()
    for r in signals_reading:
        status[r] = read_memory(signals_reading[r])
    
    for w in signals_writing:
        status[w] = read_memory(signals_writing[w])
    
    return status
    
def create_app_label(label_name, signal, row, column):
    control_label = tk.Label(app, text=label_name, fg='black', font=app_font)
    control_label.grid(row=row, column=column, padx=10, pady=5, sticky="ew")
    control_labels[signal] = control_label

def get_status_color(status, key):
    return 'green' if status[key] == 1 else 'red'

def read_logo_signals_status():
    global control_labels
    global status_queue

    while True:
        status = read_status()
        status_queue.put(status)  # Send status to the main thread
        time.sleep(0.5)

def update_ui_from_queue():
    #pdb.set_trace()
    try:
        status = status_queue.get_nowait()  # Get the latest status from the queue
        for key in control_labels.keys():
            text_color = get_status_color(status, key)
            control_labels[key].config(fg=text_color)
    except queue.Empty:
        pass  # No new status updates
    app.after(100, update_ui_from_queue)  # Schedule the next update

def on_weight_change(w):
    weight = int(w)
    if weight == 0:
        write_memory(signals_writing['camion_en_balanza'], 0)
        write_memory(signals_writing['balanza_en_cero'], 1)
    
    if weight > PESO_CAMION:
        write_memory(signals_writing['camion_en_balanza'], 1)
        write_memory(signals_writing['balanza_en_cero'], 0)

def main():
    global app
    global weight_scale
    
    init()
    
    # Centering widgets
    for c in range(2):
        app.grid_columnconfigure(c, weight=1)
    #for r in range(7):
    #    app.grid_rowconfigure(r, weight=1) # Row expands all columns

    # Create UI controls using grid
    create_app_label('Habilitacion general', 'hab_general', row=0, column=0)
    toggle_btn_hab_general = tk.Button(app, text='Activar/Desactivar', command=lambda: toggle_memory(signals_writing['hab_general']))
    toggle_btn_hab_general.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

    create_app_label('Fin pesada', 'fin_pesada', row=0, column=1)
    toggle_btn_fin_pesada = tk.Button(app, text='Activar/Desactivar', command=lambda: toggle_memory(signals_writing['fin_pesada']))
    toggle_btn_fin_pesada.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

    create_app_label('Balanza en cero', 'balanza_en_cero', row=2, column=0)
    create_app_label('Camion en balanza', 'camion_en_balanza', row=2, column=1)
    weight_scale = tk.Scale(app, from_=0, to=65000, orient=tk.HORIZONTAL, command=on_weight_change)
    weight_scale.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

    # Readings from LOGO
    create_app_label('Listo', 'listo', row=4, column=0)
    create_app_label('Semaforo entrada A', 'ingreso_A', row=5, column=0)
    create_app_label('Semaforo entrada B', 'ingreso_B', row=5, column=1)
    create_app_label('Semaforo salida A', 'salida_A', row=6, column=0)
    create_app_label('Semaforo salida B', 'salida_B', row=6, column=1)

    # Start the thread for reading LOGO signals
    read_signals_thread = threading.Thread(target=read_logo_signals_status, daemon=True)
    read_signals_thread.start()

    # Start updating the UI from the queue
    app.after(100, update_ui_from_queue)

    # Start the Tkinter main loop
    app.mainloop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        client.disconnect()
