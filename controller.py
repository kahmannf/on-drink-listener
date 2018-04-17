from data import Data
from sys import argv
from threading import Thread
##import asyncio

##for testing purposes
from time import sleep 

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

def pour_task(controller, slotid, amount_ratio, server_config):
    
    amount = amount_ratio * server_config['glass_size']
    
    seconds = amount / ((80 / (60*60)) * 1000)
    
    print('Slot: %s, Amount: %s ml, %s sec' % (slotid, amount, seconds))

    ##pump ratio => 80 l/h
    ## => 80/60 l/min ~ 1,33 l/min
    ## => 80/ (60*60) l/s ~ 22,22 ml/s
    ## => 80 / (60 * 60) * 1000 ml/s
    ## => ml / (ml/s) = s


    if isMockController:
        print('Mock_controller: open %s for %s sec' % (slotid, seconds))
    else:
        open_port(slotid)
        sleep(seconds)
        close_port(slotid)

def mix_task(controller, recipe, server_config):
    data = Data(server_config)
    
    supply_tasks = {}
    
    for ingredient in recipe['ingredients']:
        supply_item = data.get_supply_item(ingredient['beverage'])
        if supply_item:
            if not supply_item['slot'] in supply_tasks.keys():
                supply_tasks[supply_item['slot']] = ingredient['amount']
            else:
                supply_tasks[supply_item['slot']] = supply_tasks[supply_item['slot']] + ingredient['amount']
    
    total_parts = float(sum(supply_tasks.values()))

    controller.remaining_operations = len(supply_tasks.keys())

    for slot, amount in supply_tasks.items():
        thread = Thread(target=pour_task, args=(controller, slot, float(amount) / total_parts, server_config), kwargs={})
        thread.start()

    controller.isAvailable = True
    
def ready_slot_task(controller, slotid):
    if isMockController:
        print('open and close slot %s (mock)' % slotid)
        return

    print('Open port %s' % slotid)
    open_port(slotid)
    
    sleep(1)

    print('Close port %s' % slotid)
    close_port(slotid)
    
    controller.isAvailable = True


class Controller:

    def __init__(self):
        self.isAvailable = True
        self.current_thread = None
        self.remaining_operations = 0

    def mix_cocktail(self, recipe, server_config):
        data = Data(server_config)
        
        if not self.isAvailable or not data.can_mix(recipe):
            return
        else:
            self.isAvailable = False
            self.current_thread = Thread(target=mix_task, args=(self, recipe, server_config), kwargs={})
            self.current_thread.start()

    def ready_slot(self, slotid:int, server_config):
        data = Data(server_config)
        
        if not self.isAvailable:
            return

        for slot in data.supply:
            if slot['slot'] == slotid:
                self.isAvailable = False
                self.current_thread = Thread(target=ready_slot_task, args=(self, slotid), kwargs={})
                self.current_thread.start()
                return
    
    def complete_pourtask(self):
        self.remaining_operations = self.remaining_operations - 1

        if self.remaining_operations == 0:
            self.isAvailable = True

        

    
        