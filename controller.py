from data import Data
from sys import argv

isMockController = True


if not len(argv) > 1 or not argv[1] == 'no_controller':
    import smbus2
    import time
    
    # for RPI version 1, use "bus = smbus.SMBus(0)"
    bus = smbus2.SMBus(1)

    # This is the address we setup in the Arduino Program
    address = 0x04

    isMockController = False

    def writeNumber(value):
        bus.write_byte(address, value)
        
        return -1

    def open_port(port):
        writeNumber(port + 2)
        writeNumber(1)

    def close_port(port):
        writeNumber(port + 2)
        writeNumber(0)


class Controller:

    def __init__(self):
        self.isAvailable = True

    def mix_cocktail(self, recipe):
        if not self.isAvailable:
            return
        pass

    
        