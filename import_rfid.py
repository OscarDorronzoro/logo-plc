from rfid import read_serial_port as rsp
import threading

chksum = rsp.calculate_checksum(bytes.fromhex('a00b00'))
print(chksum)

rsp.init()
rsp.reading_loop('reader_A')

loop_reader_A = threading.Thread(target=rsp.reading_loop, args=('reader_A'), daemon=True)
#loop_reader_B = threading.Thread(rsp.reading_loop, args=('reader_B'), daemon=True)

#loop_reader_A.start()