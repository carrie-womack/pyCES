import serial
import time
import config

def configure_MFC():
    """Opens config file MFC parameters"""
    config_data = config.open_config()

    return config_data["MFC"]

def initialize_MFC(config_data):

    ser = serial.Serial(
        port = config_data["port"],
        baudrate = config_data["baudrate"],
        timeout = 0.1
    )

    try:
        if ser.isOpen():
            print(f"Serial port {ser.name} opened successfully")
    except serial.SerialException as e:
        print(f"Serial port error: {e}")

    return ser

def get_MFC_data(ser, config_data):

    mfc_data = {}
    for x, obj in config_data["unitAddr"].items():
        # print(obj["unitID"])
        unit = obj["unitID"]
        name = obj["name"]
        # unit = config_data["unit"]
        # #sending data to MFC
        command = f"{unit}\r"
        ser.write(command.encode())
        # print(f"sent: {command.strip()}")

        # # time.sleep(0.05)

        # #reading data from MFC
        received_data = ser.readline()
        # header = "Unit, temperature, flow, totalizer, setpoint, valve drive, gas"
        header = "Unit, pressure, temperature, volflow, massflow, setpoint, , , , , gas"
        data_name = header.split(", ")
        # print(len(data_name))
        # print(received_data)
        if received_data:
            data = received_data.decode()
            # print(data)
            data = data.strip()
            # print(data)
            data = data.split(" ")
            # print(data)
            mfc_single = {}
            for x in range(len(data_name)):
                current_data = data[x]
                if len(data_name[x]) > 0:
                    if x > 0 and x < len(data_name) - 1:
                        current_data = float(current_data)
                    mfc_single.update({data_name[x]: current_data})
                
            # print(mfc_data)
        else:
            print("No data received within timeout period")
        mfc_data.update({name:mfc_single})
    return mfc_data
        # return 0

def set_MFC(ser, unit, value):
    command = f"{unit}S{value}\r"
    # print(command)
    ser.write(command.encode())
    received_data = ser.readline()
    # print(received_data)

def close_MFC(ser):
    ser.close()

if __name__ == '__main__':
    config_data = configure_MFC()
    mfcID = initialize_MFC(config_data)
    set_MFC(mfcID, "A", "0")
    # while True:
    # try:
    MFC_string = get_MFC_data(mfcID, config_data)
    print(MFC_string)
    time.sleep(1)
    # except KeyboardInterrupt:
    close_MFC(mfcID)
        # break



