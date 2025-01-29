import tkinter as tk
import threading
import time

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


# Definicion de UI
app = tk.Tk()
app.title('Control de Bascula')

control_labels = []

def write_memory(mi,b):
    print("write_memory...", mi, b)

def create_app_control(label_name, mem_index):
    control_label = tk.Label(app, text=label_name, fg='black')
    control_label.pack()
    control_labels.append(control_label)

    on_button = tk.Button(app, text=f"Activar {label_name}", command=lambda: write_memory(mem_index, True), bg='lime')
    on_button.pack()

    off_button = tk.Button(app, text=f"Desactivar {label_name}", command=lambda: write_memory(mem_index, False), bg='red')
    off_button.pack()


create_app_control('Hab. entrar A', signals_mem['hab_entrar_A'])
create_app_control('Hab. entrar B', signals_mem['hab_entrar_B'])
create_app_control('Lista pesada', signals_mem['lista_pesada'])
create_app_control('Camion a balanza', signals_mem['camion_a_balanza'])
create_app_control('Balanza en cero', signals_mem['balanza_en_cero'])
create_app_control('Listo', signals_mem['listo'])
create_app_control('Listo pesar', signals_mem['listo_pesar'])

app.mainloop()
