import serial
from serial.tools import list_ports

# pip install pyserial
# dhi-asr2200a-d

def make_response(valid_card):
    if valid_card:
        response = 'a6 00 00 00 00 23 00 00 00 c8 00 00 00 4d'    
    else:
        response = 'a6 00 00 00 00 23 00 00 01 c8 00 00 00 4c'
    
    serial_reader_A.write(bytes.fromhex(response))

def calculate_checksum(data):
    checksum = 0
    for byte in data:
        checksum ^= byte
    return checksum.to_bytes(length=1, byteorder='big')

def add_new_card(data: bytes):
    if len(data) == 14:
        card_number = int.from_bytes(data[9:11], byteorder='big')
        print(card_number)

        if not cards.__contains__(card_number):
            f.write(f'{card_number};{data.hex()}\n')
        else:
            print('Card repeated! ------')

def check_valid_UID(data):
    uid = int.from_bytes(data[7:11], byteorder='big')
    if valid_UIDs.__contains__(uid):
        return True
    else:
        return False


port_reader_A = 'COM3' # Default value
port_reader_B = 'COM4' # Default value

ports = list_ports.comports()
for p in ports:
    print(f'{p.name} - {p.description} -- {p.serial_number}')

    # Set port for reader A
    if p.serial_number and p.serial_number.__contains__('A5069RR4'):
        if p.name.__contains__('ttyUSB'):
            port_reader_A = f'/dev/{p.name}'
        else:
            port_reader_A = p.name

    # Set port for reader B
    if p.serial_number and p.serial_number.__contains__('A5069RR4'): # Change serial number
        if p.name.__contains__('ttyUSB'):
            port_reader_A = f'/dev/{p.name}'
        else:
            port_reader_A = p.name

print()


serial_reader_A = serial.Serial(port=port_reader_A, baudrate=9600, bytesize=8, timeout=5, stopbits=serial.STOPBITS_ONE)

f = open('rfid_cards_db.txt', 'r+')
f_valid = open('valid_uid_db.txt', 'r')

cards = []
for c in f.readlines():
    cards.append(int(c.split(';')[0]))

valid_UIDs = []
for v in f_valid.readlines():
    valid_UIDs.append(int(v.replace('\n', '')))

def main():
    print('Esperando tarjeta...')
    while True:
        res = serial_reader_A.read(size=14)

        if res != b'':
            print('Card:', res.hex())

            add_new_card(res)
            valid_card = check_valid_UID(res)

            print()
            make_response(valid_card=valid_card)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        f.close()
        f_valid.close()
        serial_reader_A.close()

# Get-PSReadlineKeyHandler
# Set-PSReadlineKeyHandler -Key ctrl+c -Function ViExit
# Set-PSReadlineKeyHandler -Key Ctrl+c -Function DeleteCharOrExit

# Manual
# https://www.dahuasecurity.com/asset/upload/uploads/soft/20210326/DHI-ASR2200A-D_datasheet_20201209.pdf

# Wiring
# https://www.manualslib.com/manual/3498322/Dahua-Asr2200a-D.html?page=9#manual

# https://github.com/mitchjacksontech/TagReader/blob/master/TagReader.py
# https://github.com/playfultechnology/arduino-rfid-RDM6300/blob/master/arduino-rfid-RDM6300.ino

# https://docs.rs-online.com/b9cc/A700000007623676.pdf

# Firmware Dahua
    # https://www.dahuasecurity.com/products/All-Products/Access-Control--Time-Attendance/Access-Control/Readers/ASR2200A (downloaded)
    # https://www.dahuasecurity.com/es/products/All-Products/Access-Control/Access-Control/Readers/ASR2200A-B

# https://www.mgco.jp/mssenglish/PDF/EM/service/emmodbus.pdf

# http://www.stronglink-rfid.com/download/SL031-User-Manual.pdf
    
