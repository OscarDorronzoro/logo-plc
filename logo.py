import tkinter as tk
import snap7
from snap7.util import *
from snap7.type import *
import threading
import time

client = snap7.client.Client()
LOGO_MAC = '' # Buscar IP via ARP 
LOGO_IP = '192.168.0.4'
RACK = 0
SLOT = 1
PORT = 102

client.connect(LOGO_IP, RACK, SLOT)

def write_memory(marker, state):
  memory = client.read_area(Areas.MK, 0, 0, 1)
  memory = set_bool(memory, 0, marker, state)
  client.write_area(Areas.MK, 0, 0, memory)
