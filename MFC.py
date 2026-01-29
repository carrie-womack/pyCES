import serial
import time
import config
import sys

def configure_MFC():
    """Opens config file MFC parameters"""
    config_data = config.open_config()

    return config_data["MFC"]

def initialize_MFC(config_data):

    ser = serial.Serial(
        port = config_data["port"],
        baudrate = config_data["baudrate"],
        timeout = 0.05
    )

    try:
        if ser.isOpen():
            print(f"Serial port {ser.name} opened successfully")
    except serial.SerialException as e:
        print(f"Serial port error: {e}")

    return ser

def makeAuxFileString(mfc_string, model):
    aux_string = []
    if model == "MC":
        aux_string.append(mfc_string["cavityFlow"]["flow"])
        aux_string.append(mfc_string["cavityFlow"]["setpoint"])
        # aux_string.append(mfc_string["cavityFlow"]["pressure"])
        aux_string.append(mfc_string["cavityFlow"]["temperature"])

        aux_string.append(mfc_string["overflow"]["flow"])
        aux_string.append(mfc_string["overflow"]["setpoint"])
        # aux_string.append(mfc_string["overflow"]["pressure"])
        aux_string.append(mfc_string["overflow"]["temperature"])
    if model == "BASIS":
        aux_string.append(mfc_string["cavityFlow"]["flow"])
        aux_string.append(mfc_string["cavityFlow"]["setpoint"])
        # aux_string.append(mfc_string["cavityFlow"]["pressure"])
        aux_string.append(mfc_string["cavityFlow"]["temperature"])

        aux_string.append(mfc_string["overflow"]["flow"])
        aux_string.append(mfc_string["overflow"]["setpoint"])
        # aux_string.append(mfc_string["overflow"]["pressure"])
        aux_string.append(mfc_string["overflow"]["temperature"])
    return aux_string

def get_MFC_data(ser, config_data):

    header = config_data["header"]
    data_name = header.split(", ")
    mfc_data = {}
    for x, obj in config_data["unitAddr"].items():
        unit = obj["unitID"]
        name = obj["name"]
        command = f"{unit}\r"
        ser.write(command.encode())

        # #reading data from MFC
        received_data = ser.readline()
        data = received_data.decode()
        if data:
            data = data.strip()
            data = data.split(" ")
            mfc_single = {}
            for x in range(len(data_name)):
                current_data = data[x]
                if len(data_name[x]) > 0:
                    if x > 0 and x < len(data_name) - 1:
                        current_data = float(current_data)
                    if data_name[x] == "Unit" or data_name[x] == "temperature" or data_name[x] == "flow" or data_name[x] == "setpoint" or data_name[x] == "gas":
                        mfc_single.update({data_name[x]: current_data})
            mfc_data.update({name:mfc_single})
        else:
            print("No data received within timeout period")
        
    return mfc_data

def set_MFC(ser, unit, value):
    command = f"{unit}S{value}\r"
    ser.write(command.encode())
    received_data = ser.readline()

def change_MFC_address(ser, unit, newunit):
    command = f"{unit}@={newunit}"
    ser.write(command.encode())
    received_data = ser.readline()

def close_MFC(ser):
    ser.close()

if __name__ == '__main__':
    config_data = configure_MFC()
    mfcID = initialize_MFC(config_data)
 
    if(len(sys.argv) > 1):
        if(sys.argv[1] == 'setflow'):
            unit = sys.argv[2]
            value = sys.argv[3]
            set_MFC(mfcID, unit, value)

        elif(sys.argv[1] == 'setAddress'):
            unit = sys.argv[2]
            newunit = sys.argv[3]
            change_MFC_address(mfcID, unit, newunit)
        else:
            print("Command not recognized!")
    while True:
        try:
            MFC_string = get_MFC_data(mfcID, config_data)
            print(MFC_string)
            # auxfile_string = makeAuxFileString(MFC_string, config_data["model"])
            # print(auxfile_string)
            time.sleep(1)
        except KeyboardInterrupt:
            close_MFC(mfcID)
            break



