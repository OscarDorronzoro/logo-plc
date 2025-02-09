# Only for testing
'''
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'testing'))
'''

from ReaderFactory import Reader, ReaderFactory
import serial
from serial.tools import list_ports
import threading
import time
import queue

# pip install pyserial

RS_485_FRAME_LENGTH = 14

serial_readers = {}
rfid_readers = {}

f_cards = None
f_valid = None
cards = []
valid_UIDs = []

def init(options):
    global serial_readers, rfid_readers
    global f_cards, f_valid
    global cards, valid_UIDs

    rfid_readers['reader_A'] = ReaderFactory(options['reader_type']) # 'serial' / 'tcp'
    rfid_readers['reader_B'] = ReaderFactory(options['reader_type']) # 'serial' / 'tcp'

    port_readers = []

    #ports = [type('', (), {'name':'COM3', 'description': 'Port COM3', 'serial_number': 'A5069RR4'})(), type('', (), {'name':'COM4', 'description': 'Port COM4', 'serial_number': 'A5069RR5'})()]
    ports = list_ports.comports()

    for p in ports:
        print(f'{p.name} - {p.description} -- {p.serial_number}')

        # Set port for reader A
        if p.serial_number and p.serial_number.__contains__('A5069RR4'):
            if p.name.__contains__('ttyUSB'):
                port_readers.append(f'/dev/{p.name}')
            else:
                port_readers.append(p.name)

    print()
    if len(port_readers) == 0:
        raise Exception('No readers connected')
    serial_readers['reader_A'] = serial.Serial(port=port_readers[0], baudrate=9600, bytesize=8, timeout=5, stopbits=serial.STOPBITS_ONE)
    if len(port_readers) >= 2:
        serial_readers['reader_B'] = serial.Serial(port=port_readers[1], baudrate=9600, bytesize=8, timeout=5, stopbits=serial.STOPBITS_ONE)


    f_cards = open(f'{options[db_root_folder]}rfid_cards_db.txt', 'r+')
    f_valid = open(f'{options[db_root_folder]}valid_uid_db.txt', 'r')

    cards = []
    for c in f_cards.readlines():
        cards.append(c.split(';')[0])

    valid_UIDs = []
    for v in f_valid.readlines():
        valid_UIDs.append(int(v.replace('\n', '')))
    
def calculate_checksum(data):
    checksum = 0
    for byte in data[:-1]:
        checksum ^= byte
    return checksum.to_bytes(length=1, byteorder='big')

def add_new_card(data: bytes):
    uid = int.from_bytes(data[7:11], byteorder='big')
    facility_code = int.from_bytes(data[7:9], byteorder='big')
    card_code = int.from_bytes(data[9:11], byteorder='big')
    hex_uid = data[7:11].hex()

    print(f'{uid} {facility_code},{card_code} -- {hex_uid}')

    if not cards.__contains__(str(uid)):
        f_cards.write(f'{uid};{data.hex()}\n')

def get_card_UID(data):
     return int.from_bytes(data[7:11], byteorder='big')

def check_valid_UID(data):
    uid = get_card_UID(data)
    return valid_UIDs.__contains__(uid)

def make_response(reader, valid_card):
    if valid_card:
        response = 'a6 00 00 00 00 23 00 00 00 c8 00 00 00 4d'    
    else:
        response = 'a6 00 00 00 00 23 00 00 01 c8 00 00 00 4c'
    
    reader.write(bytes.fromhex(response))

def reading_loop(reader_name, queue):
    global serial_readers
    
    if not serial_readers.keys().__contains__(reader_name):
        raise KeyError(f'reader key ("{reader_name}") doesn\'t exist')
    
    reader = serial_readers[reader_name]
    while True:
        res = reader.read(size=RS_485_FRAME_LENGTH)
        #print(res.hex())
        if (
            res
            and len(res) == RS_485_FRAME_LENGTH
            and calculate_checksum(res) == res[13].to_bytes(length=1, byteorder='big')
        ):
            add_new_card(res)
            valid_card = check_valid_UID(res)

            print() 
            make_response(reader, valid_card)

            if valid_card:
                queue.put(get_card_UID(res))

def main():
    options = {
        'db_root_folder': '../db/'
        ,'reader_type': 'serial'
    }
    init(options)

    rfid_A_queue = queue.Queue()
    rfid_B_queue = queue.Queue()

    print('Waiting card...')
    reader_A_thread = threading.Thread(target=reading_loop, args=['reader_A', rfid_A_queue], daemon=True)
    reader_B_thread = threading.Thread(target=reading_loop, args=['reader_B', rfid_B_queue], daemon=True)
    
    reader_A_thread.start()
    reader_B_thread.start()
    
    # Main loop
    while True:
         # RFID reader A
        try:
            valid_card_reader_A = rfid_A_queue.get_nowait()  # Get card number from authorized access through reader A
            print(valid_card_reader_A)
        except queue.Empty:
            pass  # No valid card readings

        # RFID reader B
        try:
            valid_card_reader_B = rfid_B_queue.get_nowait()  # Get card number from authorized access through reader B
            print(valid_card_reader_B)
        except queue.Empty:
            pass  # No valid card readings

        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        if f_cards:
            f_cards.close()
        if f_valid:
            f_valid.close()
        if serial_readers and serial_readers.keys().__contains__('reader_A') and serial_readers['reader_A']:
            serial_readers['reader_A'].close()
        if serial_readers and serial_readers.keys().__contains__('reader_B') and serial_readers['reader_B']:
            serial_readers['reader_B'].close()



# dhi-asr2200a-d

# Manual
# https://www.dahuasecurity.com/asset/upload/uploads/soft/20210326/DHI-ASR2200A-D_datasheet_20201209.pdf

# Wiring
# https://www.manualslib.com/manual/3498322/Dahua-Asr2200a-D.html?page=9#manual

