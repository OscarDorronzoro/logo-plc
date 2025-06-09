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
    'semaforo_A': 'V0.2',
    'semaforo_B': 'V0.3',
}

signals_reading = {
    # Read from Logo! to PC
    'I1_barrera_A': 'V0.0'
    ,'I2_barrera_B': 'V0.1'
}


TRUCK_WEIGHT = 4000 # Threshold to calculate if there is a truck on the scale
PULSE_WIDTH = 1 # Pulse duration in seconds
UI_DELAY = 0.5 # Seconds to wait for reading logo status
LOGO_CONN_TYPE = 'modbus'
RFID_READER_TYPE = 'tcp'

#OGO_MAC = '8C:F3:19:B5:40:16'
LOGO_IPs = [
    '192.168.0.5'
    ,'192.168.0.9'
    ,'127.0.0.1'
]

logo_clients = []

app = None
logo_control_labels = []
weight_scale = None
semaphore_ui_list = []
app_font = None
title_font = None

# Thread-safe queue for status updates
logo_status_queues = []

def init():
    global logo_clients
    global app, app_font, title_font
    global logo_status_queues
    global LOGO_CONN_TYPE

    # Connection with logo
    connection_ok = False
    for i in range(len(LOGO_IPs)):
        client = LogoFactory.get_logo_conn(LOGO_CONN_TYPE)

        try:
            client.connect(LOGO_IPs[i])
            logo_clients.append(client)
            connection_ok = True
            print(f'Successfully connected to LOGO! on IP: {LOGO_IPs[i]}')
        except Exception as e:
            print(f'Error connecting to LOGO! on IP: {LOGO_IPs[i]}')
    
    # If any LOGO is UP, continue otherwise quit program
    if not connection_ok:
        print('Quiting!')
        quit()

    # Threading
    for i in range(len(logo_clients)):
        logo_status_queues.append(queue.Queue())
    
    # Control labes for UI
    for i in range(len(logo_clients)):
        logo_control_labels.append({})

    # Initialize Tkinter UI
    app = tk.Tk()
    app.title('Control de Báscula')

    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()
    window_width = int(screen_width * 0.8)
    window_height = int(screen_height * 0.8)
    app.geometry(f"{window_width}x{window_height}+{int((screen_width - window_width) / 2)}+{int((screen_height - window_height) / 2)}")

    app_font = font.Font(size=14)
    title_font = font.Font(size=16)

def init_logo_status(client):
    global signals_writing

    for key in signals_writing:
        write_memory(client, signals_writing[key], 0)

def read_memory(client, addr):
    return int(client.read(addr))

def write_memory(client, addr, bit_value):
    client.write(addr, int(bit_value))

def send_pulse(client, addr):
     async_pulse = threading.Thread(target=sync_send_pulse, args=[client, addr], daemon=True)
     async_pulse.start()

def sync_send_pulse(client, addr):
    write_memory(client, addr, 1)
    time.sleep(PULSE_WIDTH)
    write_memory(client, addr, 0)

def toggle_memory(client, addr):
    value = read_memory(client, addr)
    write_memory(client, addr, not value)

def read_status(client):
    global signals_reading, signals_writing

    status = {}
    for r in signals_reading:
        status[r] = read_memory(client, signals_reading[r])
    
    for w in signals_writing:
        status[w] = read_memory(client, signals_writing[w])
    
    return status
    
def create_app_label(frame, control_labels, label_name, signal, row, column):
    label = tk.Label(frame, text=label_name, fg='black', font=app_font)
    label.grid(row=row, column=column, padx=10, pady=5, sticky="ew")
    control_labels[signal] = label

def get_status_color(status, key):
    return 'lime' if status[key] == 1 else 'red'

def read_logo_signals_status(client, status_queue):
    while True:
        status = read_status(client)
        status_queue.put(status)  # Send status to the main thread
        time.sleep(UI_DELAY)

def update_ui_from_queue():
    global semaphore_ui_list
    global logo_status_queues
    global logo_control_labels
    
    # Logo status queue
    for i in range(len(logo_status_queues)):
        status_queue = logo_status_queues[i]
        control_labels = logo_control_labels[i]
        semaphore_ui = semaphore_ui_list[i]
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
                    ,'lime' if status[sem_group] else 'gray'
                )
        except queue.Empty:
            pass  # No new status updates

    # Schedule the next update
    app.after(500, update_ui_from_queue)

def create_semaphore(canvas, x, y, radius, color):
    return canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color)

def create_arrow(canvas, x1, y1, x2, y2):
    return canvas.create_line(x1, y1, x2, y2, arrow=tk.BOTH)

def setup_semaphore_ui(frame, row):
    semaphore_ui = {}

    sep = 500
    rad = 30
    pad = rad*2 + 10
    canvas = tk.Canvas(frame, width=sep+2*pad, height=180)
    canvas.grid(row=row, column=0, columnspan=2, padx=10, pady=10)
    semaphore_ui['canvas'] = canvas
    semaphores = {}

    # Semaphore A (left)
    y = 50
    semaphore_A = {}
    semaphore_A_red = create_semaphore(canvas, pad, y, rad, 'gray')
    semaphore_A['negated'] = semaphore_A_red
    semaphore_A_green = create_semaphore(canvas, pad, y+pad, rad, 'gray')
    semaphore_A['normal'] = semaphore_A_green
    semaphores['semaforo_A'] = semaphore_A

    arrow_a = create_arrow(canvas, sep, y + int(pad/2), 2*pad, y + int(pad/2))
    
    # Semaphore B (right)
    semaphore_B = {}
    semaphore_B_red = create_semaphore(canvas, pad+sep, y, rad, 'gray')
    semaphore_B['negated'] = semaphore_B_red
    semaphore_B_green = create_semaphore(canvas, pad+sep, y+pad, rad, 'gray')
    semaphore_B['normal'] = semaphore_B_green
    semaphores['semaforo_B'] = semaphore_B


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
    global logo_clients
    global logo_control_labels, logo_status_queues, semaphore_ui_list

    init()
    
    for i in range(len(logo_clients)):
        init_logo_status(logo_clients[i])

    frame = create_scrollable_frame(app)

    # Centering widgets
    for c in range(2):
        frame.grid_columnconfigure(c, weight=1)


    # Create UI controls using grid
    row = 0

    # LOGO 1
    # Logo number label
    labelLogo1 = tk.Label(frame, text='Logo 1', fg='black', font=title_font)
    labelLogo1.grid(row=row, column=0, padx=10, pady=5, sticky="ew")

    # Readings from LOGO
    row += 1
    create_app_label(frame, logo_control_labels[0], 'Barrera A', 'I1_barrera_A', row=row, column=0)
    create_app_label(frame, logo_control_labels[0], 'Barrera B', 'I2_barrera_B', row=row, column=1)

    # Write to LOGO
    #row += 1
    #create_app_label(frame, 'Semaforo A', 'semaforo_A', row=row, column=0)
    #create_app_label(frame, 'Semaforo B', 'semaforo_B', row=row, column=1)

    # Semaphore Scale 1
    row += 1
    toggle_btn_semaphore_1A = tk.Button(frame, text='Prender / Apagar', font=app_font, relief=tk.RAISED, command=lambda: toggle_memory(logo_clients[0], signals_writing['semaforo_A']))
    toggle_btn_semaphore_1A.grid(row=row, column=0, padx=10, pady=5, sticky="ew")

    toggle_btn_semaphore_1B = tk.Button(frame, text='Prender / Apagar', font=app_font, relief=tk.RAISED, command=lambda: toggle_memory(logo_clients[0], signals_writing['semaforo_B']))
    toggle_btn_semaphore_1B.grid(row=row, column=1, padx=10, pady=5, sticky="ew")

    row += 1
    semaphore_ui_list.append(setup_semaphore_ui(frame, row))

    # Start the thread for reading LOGO signals
    read_signals_thread = threading.Thread(target=read_logo_signals_status, args=[logo_clients[0], logo_status_queues[0]], daemon=True)
    read_signals_thread.start()

    # LOGO 2
    # Logo number label
    row += 1
    labelLogo2 = tk.Label(frame, text='Logo 2', fg='black', font=title_font)
    labelLogo2.grid(row=row, column=0, padx=10, pady=5, sticky="ew")

    # Readings from LOGO
    row += 1
    create_app_label(frame, logo_control_labels[1], 'Barrera A', 'I1_barrera_A', row=row, column=0)
    create_app_label(frame, logo_control_labels[1], 'Barrera B', 'I2_barrera_B', row=row, column=1)

    # Write to LOGO
    # Semaphore Scale 1
    row += 1
    toggle_btn_semaphore_1A = tk.Button(frame, text='Prender / Apagar', font=app_font, relief=tk.RAISED, command=lambda: toggle_memory(logo_clients[1], signals_writing['semaforo_A']))
    toggle_btn_semaphore_1A.grid(row=row, column=0, padx=10, pady=5, sticky="ew")

    toggle_btn_semaphore_1B = tk.Button(frame, text='Prender / Apagar', font=app_font, relief=tk.RAISED, command=lambda: toggle_memory(logo_clients[1], signals_writing['semaforo_B']))
    toggle_btn_semaphore_1B.grid(row=row, column=1, padx=10, pady=5, sticky="ew")

    row += 1
    semaphore_ui_list.append(setup_semaphore_ui(frame, row))
    
    # Start the thread for reading LOGO signals
    read_signals2_thread = threading.Thread(target=read_logo_signals_status, args=[logo_clients[1], logo_status_queues[1]], daemon=True)
    read_signals2_thread.start()

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
        for client in logo_clients:
            if client:
                client.close()
        if app:
            app.quit()
