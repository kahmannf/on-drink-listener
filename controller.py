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

def pour_task(controller, slotid, amount_ml, server_config):
    
    data = Data(server_config)

    seconds = amount_ml / ((80 / (60*60)) * 1000)

    print('Slot: %s, Amount: %s ml, %s sec' % (slotid, amount_ml, seconds))

    ##pump ratio => 80 l/h
    ## => 80/60 l/min ~ 1,33 l/min
    ## => 80/ (60*60) l/s ~ 22,22 ml/s
    ## => 80 / (60 * 60) * 1000 ml/s
    ## => ml / (ml/s) = s


    if isMockController:
        print('Mock_controller: open %s for %s sec' % (slotid, seconds))
    else:
        data.remove_amount_by_slot(slotid, amount_ml)
        open_port(slotid)
        sleep(seconds)
        close_port(slotid)


    controller.complete_pourtask()

def mix_task(controller, recipe, server_config):
    
    supply_tasks = {}
    
    total_parts = sum(ingredient['amount'] for ingredient in recipe['ingredients'])


    for ingredient in recipe['ingredients']:    
        if not ingredient['beverage'] in supply_tasks.keys():
            supply_tasks[ingredient['beverage']] = ingredient['amount']
        else:
            supply_tasks[ingredient['beverage']] = supply_tasks[ingredient['beverage']] + ingredient['amount']
    
    pour_tasks = {}

    data = Data(server_config)

    for beverage, amount in supply_tasks.items(): 
        supply_items = sorted(data.get_supply_items(beverage), key= lambda d:d['amount'])

        amount = (amount / total_parts) * server_config['glass_size']

        for supply_item in supply_items:
            if amount > 0:
                if supply_item['amount'] >= amount:
                    pour_tasks[supply_item['slot']] = amount
                    amount -= amount
                else:
                    pour_tasks[supply_item['slot']] = supply_item['amount']
                    amount -= supply_item['amount']

    controller.remaining_operations = len(pour_tasks.keys())

    for slot, amount in pour_tasks.items():
        thread = Thread(target=pour_task, args=(controller, slot, amount, server_config), kwargs={})
        thread.start()


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

        print('Completed pour_task. Remaining: %s' % self.remaining_operations)

        if self.remaining_operations == 0:
            self.isAvailable = True

        

    
        