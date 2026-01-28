import gpiod
import time
import config

from gpiod.line import Direction, Value

def configure_gpio():
    """Opens config file analog parameters"""
    config_params = config.open_config()
    return config_params["gpio"]

def initialize_gpio(config_params):
    """Establishes a line request for each valve,
        sets them to be output, and then drives them low"""
    gpioLocation = config_params["gpioLocation"]    #Read base location of GPIO
    lineParams = config_params["lineParams"]    #Read dictionary of other paramters
    
    #Cycle through each gpio pin from config file
    for x, obj in lineParams.items():

        #Get the board number and offset value for each
        board = gpioLocation + obj["board"]
        offset = obj["offset"]

        #Request a line for each, set it to OUTPUT and INACTIVE
        gpio_id = gpiod.request_lines(board, consumer="pyCES", config={
            offset: gpiod.LineSettings(
                direction=Direction.OUTPUT, output_value=Value.INACTIVE
            )})

        #Add the request object to the dictionary so it can be reference lated
        obj["ID"] = gpio_id
    
    return lineParams

def set_gpio_value(ID, offset, value):
    """Sets a line with ID and offset to a certain value (0 or 1)"""
    if(value == 1):
        ID.set_value(offset, Value.ACTIVE)
    else:
        ID.set_value(offset, Value.INACTIVE)

def read_gpio_value_all(lineParams):
    """Read current values and convert ACTIVE to 1 and INACTIVE to 0
    Return a dictionary of labels and values"""
    values = {}
    for x, obj in lineParams.items():
        offset = obj["offset"]
        ID = obj["ID"]
        status = ID.get_value(offset)
        if status == Value.INACTIVE:
            value = 0
        elif status == Value.ACTIVE:
            value = 1
        values.update({x:value})
    return values
          
def read_gpio_value_by_offset(ID, offset):
    
    return ID.get_value(offset)

def release_gpio_pins(lineParams):
    """Release the line when done. Not sure if necessary, but why not"""
    for x, obj in lineParams.items():
        ID = obj["ID"]   
        ID.release()

def demo_toggle_valve(lineParams):
    """Demo program that toggles all the pins every 
    2 seconds until the user interrupts"""
    value = 1
    while True:
        try:
            value ^= 1
            set_string = f"setting "
            for x, obj in lineParams.items():
                offset = obj["offset"]
                ID = obj["ID"]
                
                print(f"{x} to {value}, ",end="")
                set_gpio_value(ID, offset, value)
            
            read_values = read_gpio_value_all(lineParams)
            print(f"\nReading values: {read_values}")
            
            time.sleep(2)
        except KeyboardInterrupt:
            print("Exiting...")
            #for x, obj in lineParams.items():
                #ID = obj["ID"]
            release_gpio_pins(lineParams)
            break
            
def makeAuxFileString(gpio_string):
    aux_string = []
    aux_string.append(gpio_string["SSR0"])
    aux_string.append(gpio_string["SSR1"])
    aux_string.append(gpio_string["LED"])
    return aux_string

if __name__ == '__main__':
    config_params = configure_gpio()
    lineParams = initialize_gpio(config_params)
    demo_toggle_valve(lineParams)
