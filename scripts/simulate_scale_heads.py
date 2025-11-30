#!/usr/bin/env python3
import serial
import threading
import time
import random
import signal
import sys

# Parámetros por defecto
PORTS = ["COM10", "COM11", "COM12", "COM13"]
BAUDRATE = 9600
INTERVAL_SEC = 5.0
RANDOMNESS = 300
BASE_WEIGHTS = [4000.0, 3800.0, 4100.0, 5000.0]  # peso base para cada cabezal

_stop_event = threading.Event()

def simulate_head(port_name: str, base_weight: float):
    try:
        with serial.Serial(port_name, baudrate=BAUDRATE, timeout=1, write_timeout=1) as ser:
            print(f"[{port_name}] Abierto, simulando cabezal con base {base_weight:.2f}")
            while not _stop_event.is_set():
                variation = random.uniform(-RANDOMNESS, RANDOMNESS)
                weight = base_weight + variation
                formatted = f"{weight:8.2f}\r\n"  # similar a muchos cabezales
                try:
                    ser.write(formatted.encode("ascii"))
                    ser.flush()
                    print(f"[{port_name}] enviado: '{formatted.strip()}'")
                except Exception as e:
                    print(f"[{port_name}] error escribiendo: {e}")
                time.sleep(INTERVAL_SEC)
    except Exception as e:
        print(f"[{port_name}] no se pudo abrir el puerto: {e}")

def shutdown_handler(signum, frame):
    print("\nRecibido Ctrl+C, cerrando simuladores...")
    _stop_event.set()

def main():
    # Permitir override desde línea de comando: python script.py COM10 COM11
    ports = PORTS
    if len(sys.argv) >= 2:
        ports = sys.argv[1:]
    if len(ports) != len(BASE_WEIGHTS):
        print("Cantidad de puertos debe coincidir con cantidad de pesos base configurados.")
        print(f"Uso esperado: {sys.argv[0]} COM10 COM11")
        sys.exit(1)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    threads = []
    for port, base in zip(ports, BASE_WEIGHTS):
        t = threading.Thread(target=simulate_head, args=(port, base), daemon=True)
        t.start()
        threads.append(t)

    # Esperar hasta que se pida terminar
    try:
        while not _stop_event.is_set():
            time.sleep(0.2)
    except KeyboardInterrupt:
        _stop_event.set()

    # Dar tiempo a que los hilos terminen
    for t in threads:
        t.join(timeout=1.0)
    print("Simuladores finalizados.")

if __name__ == "__main__":
    main()
