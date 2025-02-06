def Serial(port='COM3', baudrate=9600, bytesize=8, timeout=5, stopbits=1):
    obj = type('', (), {})
    obj.read = lambda size : bytes.fromhex('a6 00 0c 01 40 01 04 00 46 79 34 00 00 e5')
    obj.write = lambda : 0
    return obj