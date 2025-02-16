from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext

def run_simulated_server():
    # Define the data blocks for the server
    # Coils (read/write, 1 bit)
    coils = ModbusSequentialDataBlock(0x00, [False] * 100)  # 100 coils starting at address 0
    # Discrete Inputs (read-only, 1 bit)
    discrete_inputs = ModbusSequentialDataBlock(0x00, [False] * 100)  # 100 discrete inputs starting at address 0
    # Holding Registers (read/write, 16 bits)
    holding_registers = ModbusSequentialDataBlock(0x00, [0] * 100)  # 100 holding registers starting at address 0
    # Input Registers (read-only, 16 bits)
    input_registers = ModbusSequentialDataBlock(0x00, [0] * 100)  # 100 input registers starting at address 0

    # Create a Modbus slave context (represents a single device)
    slave_context = ModbusSlaveContext(
        di=discrete_inputs,  # Discrete Inputs
        co=coils,           # Coils
        hr=holding_registers,  # Holding Registers
        ir=input_registers,  # Input Registers
    )

    # Create a Modbus server context (can contain multiple slaves)
    server_context = ModbusServerContext(slaves=slave_context, single=True)

    # Start the Modbus TCP server
    port = 510
    print(f'Starting Modbus TCP server on localhost:{port}')
    StartTcpServer(context=server_context, address=('localhost', port))

if __name__ == "__main__":
    run_simulated_server()
