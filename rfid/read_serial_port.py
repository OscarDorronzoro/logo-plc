# Only for testing
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'testing'))

import serial
#from serial.tools import list_ports
import threading
import time

# pip install pyserial
RS_485_FRAME_LENGTH = 14
serial_readers = {}
f_cards = None
f_valid = None
cards = []
valid_UIDs = []

def init():
    global serial_readers
    global f_cards, f_valid
    global cards, valid_UIDs

    port_reader_A = 'COM3' # Default value
    port_reader_B = 'COM4' # Default value

    #ports = list_ports.comports()
    ports = [type('', (), {'name':'COM3', 'description': 'Port COM3', 'serial_number': 'A5069RR4'})(), type('', (), {'name':'COM4', 'description': 'Port COM4', 'serial_number': 'A5069RR5'})()]
    for p in ports:
        print(f'{p.name} - {p.description} -- {p.serial_number}')

        # Set port for reader A
        if p.serial_number and p.serial_number.__contains__('A5069RR4'):
            if p.name.__contains__('ttyUSB'):
                port_reader_A = f'/dev/{p.name}'
            else:
                port_reader_A = p.name

        # Set port for reader B
        if p.serial_number and p.serial_number.__contains__('A5069RR5'): # Change serial number
            if p.name.__contains__('ttyUSB'):
                port_reader_B = f'/dev/{p.name}'
            else:
                port_reader_B = p.name
    print()
    serial_readers['reader_A'] = serial.Serial(port=port_reader_A, baudrate=9600, bytesize=8, timeout=5, stopbits=serial.STOPBITS_ONE)
    serial_readers['reader_B'] = serial.Serial(port=port_reader_B, baudrate=9600, bytesize=8, timeout=5, stopbits=serial.STOPBITS_ONE)


    f_cards = open('rfid_cards_db.txt', 'r+')
    f_valid = open('valid_uid_db.txt', 'r')

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

def check_valid_UID(data):
    uid = int.from_bytes(data[7:11], byteorder='big')
    return valid_UIDs.__contains__(uid)

def make_response(reader, valid_card):
    if valid_card:
        response = 'a6 00 00 00 00 23 00 00 00 c8 00 00 00 4d'    
    else:
        response = 'a6 00 00 00 00 23 00 00 01 c8 00 00 00 4c'
    
    reader.write(bytes.fromhex(response))

def reading_loop(reader_name):
    if not serial_readers.keys().__contains__(reader_name):
        raise KeyError(f'reader key ("{reader_name}") doesn\'t exist')
    
    reader = serial_readers[reader_name]
    while True:
        res = reader.read(size=RS_485_FRAME_LENGTH)
        print(res.hex())
        if (
            res
            and len(res) == RS_485_FRAME_LENGTH
            and calculate_checksum(res) == res[13].to_bytes(length=1, byteorder='big')
        ):
            add_new_card(res)
            valid_card = check_valid_UID(res)

            print() 
            make_response(reader, valid_card)

def main():
    global serial_readers

    init()
    print('Waiting card...')
    reader_A_thread = threading.Thread(target=reading_loop, args=['reader_A'], daemon=True)
    reader_B_thread = threading.Thread(target=reading_loop, args=['reader_B'], daemon=True)
    
    reader_A_thread.start()
    reader_B_thread.start()
    
    # Main loop
    while True:
        time.sleep(3)

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

