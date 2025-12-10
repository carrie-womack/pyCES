import asyncio
from alicat import basis
import time
import config
import sys

def configure_MFC():
    """Opens config file MFC parameters"""
    config_data = config.open_config()

    return config_data["MFC"]

async def get(address, unit):
    """Sends the MFC the unit (i.e."A") and receives the response, converting it into a dictionary"""
    async with basis.FlowController(address, unit) as flow_controller:
        print(await flow_controller.get())

async def set_flow(flow, address, unit):
    async with basis.FlowController(address, unit) as flow_controller:
        await flow_controller.set_setpoint(flow)

async def set_air(air, address, unit):
    async with basis.FlowController(address, unit) as flow_controller:
        await flow_controller.set_gas('N2')

def main():

    config_params = configure_MFC()
    address = config_params["port"]
    unit = config_params["unit"]
    
    #checks if you have given a command and runs that
    if(len(sys.argv) > 1):
        if(sys.argv[1] == 'setFlow'):
            asyncio.run(set_flow(float(sys.argv[2]), address, unit))
        elif(sys.argv[1] == 'gas'):
            asyncio.run(set_air(str(sys.argv[2]), address, unit))
        else:
            print("Command not recognized!")

    #Prints the dictionary from the MFC once per second until interrupted
    while True:
        try: 
            asyncio.run(get(address, unit))
            time.sleep(1)
        except KeyboardInterrupt:
            print("\tClosing pyCES now")
            break


if __name__ == '__main__':
    main()
