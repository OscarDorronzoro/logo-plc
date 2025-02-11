import snap7

print('Starting snap7 server...')
#server = snap7.server.Server()
server_default = snap7.server.mainloop(tcpport=102, init_standard_values=True)

