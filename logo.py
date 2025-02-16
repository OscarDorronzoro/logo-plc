import tkinter as tk
from tkinter import font
from LogoFactory import LogoFactory
import threading
import queue
import time
#from scapy.all import ARP, Ether, srp
import pdb
from rfid import read_rfid as rfid


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

signals_reading = {
    # Read from Logo! to PC
    'en_servicio': 'V1.0'
    ,'listo': 'V1.1'
    ,'ingreso_A': 'V1.2'
    ,'ingreso_B': 'V1.3'
    ,'salida_A': 'V1.4'
    ,'salida_B': 'V1.5'
    ,'I1_barrera_A': 'V1.6'
    ,'I2_barrera_B': 'V1.7'
    ,'Q1_semaforo_A1': 'V2.0'
    ,'Q2_semaforo_A2': 'V2.1'
    ,'Q3_semaforo_B1': 'V2.2'
    ,'Q4_semaforo_B2': 'V2.3'
}


TRUCK_WEIGHT = 4000 # Threshold to calculate if there is a truck on the scale
PULSE_WIDTH = 1 # Pulse duration in seconds
UI_DELAY = 1 # Seconds to wait for reading logo status

LOGO_MAC = '8C:F3:19:B5:40:16'
LOGO_IP = '192.168.0.5'

logo_client = None

app = None
control_labels = {}
weight_scale = None
semaphore_ui = {}
app_font = None

# Thread-safe queue for status updates
status_queue = None
rfid_A_queue = None
rfid_B_queue = None


def lookup_ip_address(mac_address):
    pass

def init():
    global logo_client
    global app, app_font
    global status_queue, rfid_A_queue, rfid_B_queue
    
    # Connection with logo
    logo_client = LogoFactory.get_logo_conn('modbus')
    # Trying testing local server
    try:
        logo_client.connect('127.0.0.1')
    except Exception as e:
        # Real Logo!
        print(e)
        try:
            logo_client.connect(LOGO_IP)
        except Exception as e:
            print(e)
            quit()

    # Threading
    status_queue = queue.Queue()
    rfid_A_queue = queue.Queue()
    rfid_B_queue = queue.Queue()

    # RFID Reader
    options = {
        'db_root_folder': './db/'
        ,'reader_type': 'serial'
    }
    rfid.init(options)

    # Initialize Tkinter UI
    app = tk.Tk()
    app.title('Control de Báscula')

    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()
    window_width = int(screen_width * 0.8)
    window_height = int(screen_height * 0.8)
    app.geometry(f"{window_width}x{window_height}+{int((screen_width - window_width) / 2)}+{int((screen_height - window_height) / 2)}")

    app_font = font.Font(size=14)

def init_logo_status():
    global signals_writing

    for key in signals_writing:
        write_memory(signals_writing[key], 0)

def read_memory(addr):
    return int(logo_client.read(addr))

def write_memory(addr, bit_value):
    logo_client.write(addr, int(bit_value))

def send_pulse(addr):
     async_pulse = threading.Thread(target=sync_send_pulse, args=[addr], daemon=True)
     async_pulse.start()

def sync_send_pulse(addr):
    write_memory(addr, 1)
    time.sleep(PULSE_WIDTH)
    write_memory(addr, 0)

def toggle_memory(addr):
    value = read_memory(addr)
    write_memory(addr, not value)

def read_status():
    global signals_reading, signals_writing

    status = {}
    for r in signals_reading:
        status[r] = read_memory(signals_reading[r])
    
    for w in signals_writing:
        status[w] = read_memory(signals_writing[w])
    
    return status
    
def create_app_label(frame, label_name, signal, row, column):
    global control_labels
    control_label = tk.Label(frame, text=label_name, fg='black', font=app_font)
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
        time.sleep(UI_DELAY)

def update_ui_from_queue():
    global control_labels, semaphore_ui
    global status_queue, rfid_A_queue, rfid_B_queue
    
    # Logo status queue
    try:
        status = status_queue.get_nowait()  # Get the latest status from the queue
        for key in control_labels.keys():
            text_color = get_status_color(status, key)
            control_labels[key].config(fg=text_color)

        for sem_group in semaphore_ui['semaphores']:
            update_semaphore_color(
                semaphore_ui['canvas']
                ,semaphore_ui['semaphores'][sem_group]['negated']
                ,'red' if not status[sem_group] else 'gray'
            )
            update_semaphore_color(
                semaphore_ui['canvas']
                ,semaphore_ui['semaphores'][sem_group]['normal']
                ,'green' if status[sem_group] else 'gray'
            )
    except queue.Empty:
        pass  # No new status updates

    # RFID reader A
    try:
        valid_card_reader_A = rfid_A_queue.get_nowait()  # Get card number from authorized access through reader A
        send_pulse(signals_writing['hab_entrar_A'])
    except queue.Empty:
        pass  # No valid card readings

    # RFID reader B
    try:
        valid_card_reader_B = rfid_B_queue.get_nowait()  # Get card number from authorized access through reader B
        send_pulse(signals_writing['hab_entrar_B'])
    except queue.Empty:
        pass  # No valid card readings

    # Schedule the next update
    app.after(500, update_ui_from_queue)

def on_weight_change(event):
    global weight_scale
    
    weight = int(weight_scale.get())
    if weight == 0:
        write_memory(signals_writing['camion_en_balanza'], 0)
        write_memory(signals_writing['balanza_en_cero'], 1)
    
    if weight > TRUCK_WEIGHT:
        write_memory(signals_writing['camion_en_balanza'], 1)
        write_memory(signals_writing['balanza_en_cero'], 0)

def create_semaphore(canvas, x, y, radius, color):
    return canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color)

def create_arrow(canvas, x1, y1, x2, y2):
    return canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST)

def setup_semaphore_ui(frame, row):
    global semaphore_ui

    sep = 500
    rad = 20
    pad = rad*2 + 10
    canvas = tk.Canvas(frame, width=sep+2*pad, height=300)
    canvas.grid(row=row, column=0, columnspan=2, padx=10, pady=10)
    semaphore_ui['canvas'] = canvas
    semaphores = {}

    # Semaphore A (Exit <--- Entry)
    y = 50
    semaphore_A_exit = {}
    semaphore_A_exit_red = create_semaphore(canvas, pad, y, rad, 'gray')
    semaphore_A_exit['negated'] = semaphore_A_exit_red
    semaphore_A_exit_green = create_semaphore(canvas, pad, y+pad, rad, 'gray')
    semaphore_A_exit['normal'] = semaphore_A_exit_green
    semaphores['Q2_semaforo_A2'] = semaphore_A_exit

    arrow_a = create_arrow(canvas, sep, y + int(pad/2), 2*pad, y + int(pad/2))
    
    semaphore_A_entry = {}
    semaphore_A_entry_red = create_semaphore(canvas, pad+sep, y, rad, 'gray')
    semaphore_A_entry['negated'] = semaphore_A_entry_red
    semaphore_A_entry_green = create_semaphore(canvas, pad+sep, y+pad, rad, 'gray')
    semaphore_A_entry['normal'] = semaphore_A_entry_green
    semaphores['Q1_semaforo_A1'] = semaphore_A_entry

    # Semaphore B (Entry ---> Exit)
    y += pad + rad
    y += pad
    semaphore_B_entry = {}
    semaphore_B_entry_red = create_semaphore(canvas, pad, y, rad, 'gray')
    semaphore_B_entry['negated'] = semaphore_B_entry_red
    semaphore_B_entry_green = create_semaphore(canvas, pad, y+pad, rad, 'gray')
    semaphore_B_entry['normal'] = semaphore_B_entry_green
    semaphores['Q3_semaforo_B1'] = semaphore_B_entry

    arrow_b = create_arrow(canvas, 2*pad, y + int(pad/2), sep, y + int(pad/2))
    
    semaphore_B_exit = {}
    semaphore_B_exit_red = create_semaphore(canvas, pad+sep, y, rad, 'gray')
    semaphore_B_exit['negated'] = semaphore_B_exit_red
    semaphore_B_exit_green = create_semaphore(canvas, pad+sep, y+pad, rad, 'gray')
    semaphore_B_exit['normal'] = semaphore_B_exit_green
    semaphores['Q4_semaforo_B2'] = semaphore_B_exit

    semaphore_ui['semaphores'] = semaphores

    return semaphore_ui

def update_semaphore_color(canvas, light_id, color):
    canvas.itemconfig(light_id, fill=color)

def create_scrollable_frame(app):
    # Create a canvas with a vertical scrollbar
    canvas = tk.Canvas(app)
    scrollbar = tk.Scrollbar(app, orient=tk.VERTICAL, command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    # Configure the canvas
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind(
        '<Configure>',
        lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
    )

    # Add the scrollable frame to the canvas
    canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')

    # Function to resize the frame width to match the canvas
    def resize_frame(event):
        canvas.itemconfig(canvas_frame, width=event.width)

    # Bind the canvas to resize the frame
    canvas.bind('<Configure>', resize_frame)

    # Pack the canvas and scrollbar
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Configure the scrollable frame to expand
    scrollable_frame.bind(
        '<Configure>',
        lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
    )

    return scrollable_frame

def main():
    global app
    global weight_scale
    global rfid_A_queue, rfid_B_queue

    init()
    
    init_logo_status()

    frame = create_scrollable_frame(app)

    # Centering widgets
    for c in range(2):
        frame.grid_columnconfigure(c, weight=1)

    # Create UI controls using grid
    row = 0
    create_app_label(frame, 'Habilitacion general', 'hab_general', row=row, column=0)
    create_app_label(frame, 'Fin pesada', 'fin_pesada', row=row, column=1)

    row+=1
    toggle_btn_hab_general = tk.Button(frame, text='Activar/Desactivar', relief=tk.SUNKEN, command=lambda: toggle_memory(signals_writing['hab_general']))
    toggle_btn_hab_general.grid(row=row, column=0, padx=10, pady=5, sticky="ew")

    toggle_btn_fin_pesada = tk.Button(frame, text='Activar/Desactivar', relief=tk.RAISED, command=lambda: send_pulse(signals_writing['fin_pesada']))
    toggle_btn_fin_pesada.grid(row=row, column=1, padx=10, pady=5, sticky="ew")

    row+=1
    create_app_label(frame, 'Balanza en cero', 'balanza_en_cero', row=row, column=0)
    create_app_label(frame, 'Camion en balanza', 'camion_en_balanza', row=row, column=1)
    
    row+=1
    weight_scale = tk.Scale(frame, from_=0, to=65000, orient=tk.HORIZONTAL)
    weight_scale.bind('<ButtonRelease-1>', on_weight_change)
    weight_scale.grid(row=row, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
    
    row+=1
    create_app_label(frame, 'RFID A', 'hab_entrar_A', row=row, column=0)
    create_app_label(frame, 'RFID B', 'hab_entrar_B', row=row, column=1)

    # Readings from LOGO
    row+=1
    create_app_label(frame, 'En servicio', 'en_servicio', row=row, column=0)
    create_app_label(frame, 'Listo', 'listo', row=row, column=1)
    
    row+=1
    create_app_label(frame, 'I1 barrera A', 'I1_barrera_A', row=row, column=0)
    create_app_label(frame, 'I2 barrera B', 'I2_barrera_B', row=row, column=1)

    row+=1
    create_app_label(frame, 'Ingreso por A', 'ingreso_A', row=row, column=0)
    create_app_label(frame, 'Ingreso por B', 'ingreso_B', row=row, column=1)

    row+=1
    create_app_label(frame, 'Listo pesar por A', 'salida_A', row=row, column=0)
    create_app_label(frame, 'Listo pesar por B', 'salida_B', row=row, column=1)
    

    '''
    row+=1
    create_app_label(frame, 'Semaforo entrada A', 'Q1_semaforo_A1', row=row, column=0)
    create_app_label(frame, 'Semaforo entrada B', 'Q3_semaforo_B1', row=row, column=1)
    
    row+=1
    create_app_label(frame, 'Semaforo salida A', 'Q2_semaforo_A2', row=row, column=0)
    create_app_label(frame, 'Semaforo salida B', 'Q4_semaforo_B2', row=row, column=1)
    '''

    row+=1
    setup_semaphore_ui(frame, row)

    # Start the thread for reading LOGO signals
    read_signals_thread = threading.Thread(target=read_logo_signals_status, daemon=True)
    read_signals_thread.start()
    
    # RFID threads
    rfid_reader_A_thread = threading.Thread(target=rfid.reading_loop, args=['reader_A', rfid_A_queue], daemon=True)
    rfid_reader_A_thread.start()
    rfid_reader_B_thread = threading.Thread(target=rfid.reading_loop, args=['reader_B', rfid_B_queue], daemon=True)
    rfid_reader_B_thread.start()

    # Start updating the UI from the queue
    app.after(200, update_ui_from_queue)

    # Start the Tkinter main loop
    app.mainloop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        if logo_client:
            logo_client.close()
        if app:
            app.quit()
