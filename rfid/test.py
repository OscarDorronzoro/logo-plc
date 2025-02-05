readed1 = b'\xa6\x00\x0c\x01@\x01\x04\x00Fy4\x00\x00\xe5'
#         0x a6  00  0c  01 40 01 04  00 46 79 34 00 00 e5
readed2 = b'\xa6\x00\x0c\x01@\x01\x04\x00F\xb4>\x00\x00"'
#         0x a6  00  0c  01 40 01 04 00 46 b4 3e 00 00 22

readed3 = b'\xa6\x00\x0c\x01@\x01\x04\x00E\x86\xf1\x00\x00\xdc'
#         0x a6  00  0c  01 40 01 04  00 45 86  f1  00  00  dc

#   |---------fijo---------|tarjeta-|-------|
#   0  1  2  3  4  5  6  7  8  9  10 11 12 13
#   a6 00 0c 01 40 01 04 00 46 79 34 00 00 e5
#   a6 00 0c 01 40 01 04 00 46 b4 3e 00 00 22
#   a6 00 0c 01 40 01 04 00 45 86 f1 00 00 dc
#   a6 00 0c 01 40 01 04 00 46 24 9e 00 00 12
#   a6 00 0c 01 40 01 04 00 46 6c 63 00 00 a7
#   a6 00 0c 01 40 01 04 00 45 d1 3e 00 00 44
#   a6 00 0c 01 40 01 04 00 46 8e 95 00 00 b3
#   a6 00 0c 01 40 01 04 00 46 06 a8 00 00 06
#   a6 00 0c 01 40 01 04 00 46 5c 26 00 00 d2
#   a6 00 0c 01 40 01 04 00 45 91 85 00 00 bf

readed = readed1[0].to_bytes(length=1, byteorder='big') # header

readed = readed1[1:3] # 13 -> data length ???

readed = readed1[3:7] # 13 -> command ???

readed = readed1[7].to_bytes(length=1, byteorder='big') # null byte -> data separation?

readed = readed1[7:11] # 4618548 -> 0004618548 printed on card, concat bytes from 070,31028   (ff ff ff ff = 4 B -> 10 digits, as on card number)
readed = readed1[7:9] # 70 -> 070 printed on card
readed = readed1[9:11] # 31028 -> card number? printed on card

readed = readed1[11:13] # two null bytes -> end of reading? padding? reserved?

readed = readed1[13].to_bytes(length=1, byteorder='big') # checksum


readed = readed1[7:9]


print(readed)
z = int.from_bytes(readed, byteorder='big')
print(z)
print(bin(z))
print(hex(z))


# Convert from decimal (printed on card) to hex
print('-----------')

r2_first = int('0004633662') # Decimal value is the result of concat hex of "sec" and "rd", and convert to decimal
print(hex(r2_first))

r2_sec = int('070')
print(hex(r2_sec))

r2_rd = int('46142')
print(hex(r2_rd))


print('------------')



'''
# Access Granted
Received: a6 00 0c 01 40 01 04 00 46 b4 3e 00 00 22 # card
Received: a6 00 00 00 00 23 00 00 00 c8 00 00 00 4d  # response from controller

# Access Denied
Received: a6 00 0c 01 40 01 04 00 46 79 34 00 00 e5 # card
Received: a6 00 00 00 00 23 00 00 01 c8 00 00 00 4c # response from controller

# Unregistered card (same as access denied)
Received: a6 00 0c 01 40 01 04 00 45 86 f1 00 00 dc # card
Received: a6 00 00 00 00 23 00 00 01 c8 00 00 00 4c # response from controller


# One by one
Received: a6
Received: 00
Received: 0c
Received: 01
Received: 40
Received: 01
Received: 04
Received: 00
Received: 46
Received: b4
Received: 3e
Received: 00
Received: 00
Received: 22

Received: a6
Received: 00
Received: 00
Received: 00
Received: 00
Received: 23
Received: 00
Received: 00
Received: 00
Received: c8
Received: 00
Received: 00
Received: 00
Received: 4d

Received: a6
Received: 00
Received: 0c
Received: 01
Received: 40
Received: 01
Received: 04
Received: 00
Received: 46
Received: 79
Received: 34
Received: 00
Received: 00
Received: e5

Received: a6
Received: 00
Received: 00
Received: 00
Received: 00
Received: 23
Received: 00
Received: 00
Received: 01
Received: c8
Received: 00
Received: 00
Received: 00
Received: 4c
'''