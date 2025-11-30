from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
import threading

def run_simulated_server(port):
    # Define the data blocks for the server
    coils = ModbusSequentialDataBlock(0x00, [False] * 100)
    discrete_inputs = ModbusSequentialDataBlock(0x00, [False] * 100)
    holding_registers = ModbusSequentialDataBlock(0x00, [0] * 100)
    input_registers = ModbusSequentialDataBlock(0x00, [0] * 100)

    # Create a Modbus slave context
    slave_context = ModbusSlaveContext(
        di=discrete_inputs,
        co=coils,
        hr=holding_registers,
        ir=input_registers,
    )

    # Create a Modbus server context
    server_context = ModbusServerContext(slaves=slave_context, single=True)

    print(f"Starting Modbus TCP server on localhost:{port}")
    StartTcpServer(context=server_context, address=('localhost', port))

if __name__ == "__main__":
    ports = [510, 10510, 11510, 12510]
    threads = []

    for p in ports:
        t = threading.Thread(target=run_simulated_server, args=(p,), daemon=True)
        threads.append(t)
        t.start()

    print("All Modbus servers started.")
    try:
        while True:
            pass  # Mantener el script vivo
    except KeyboardInterrupt:
        print("Stopping servers...")
