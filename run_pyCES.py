
"""
Main pyCES code
================================
*Still very much under development! Don't try to use it like this!*

"""
# pyCES modules:
import ocean_spectrometer
import save_data
import udp
import TEC
import analog
import gpio
import MFC

# Python built-ins
import time
import datetime
import json

def main():

    #read in parameters from the config file
    udp_params = udp.configure_UDP() #read in UDP IP address and port
    save_params = save_data.configure_save() #read in parameters for file saving (file location, minutes between new save, etc.)
    spec_params = ocean_spectrometer.configure_spectrometers() #read in parameters for spectrometer (integration time, etc)
    tec_params = TEC.configure_TEC() #read in TEC serial port
    analog_params = analog.configure_AI() #read in analog conversion factors
    gpio_params = gpio.configure_gpio() #read in the GPIO pin parameters
    mfc_params = MFC.configure_MFC() #read in MFC addresses

    enable_spec = spec_params["enable"]
    enable_tec = tec_params["enable"]
    enable_gpio = gpio_params["enable"]
    enable_mfc = mfc_params["enable"]
    enable_analog = analog_params["enable"]

    #initialize any components that have been enabled
    status = f""
    file_path_name = save_params["location"]
    min_between_file_saves = save_params["minToSave"]
    sec_between_file_saves = int(min_between_file_saves * 60)

    if enable_tec:
        tecID = TEC.MeerstetterTEC(port=tec_params["port"], channel=tec_params["channel"], baudrate=tec_params["baudrate"])
    if enable_gpio:
        gpioID = gpio.initialize_gpio(gpio_params)
    if enable_mfc:
        mfcID = MFC.initialize_MFC(mfc_params)
    if enable_spec:
        specID = ocean_spectrometer.initialize_spectrometer(spec_params)
        wavelengths = specID.wavelengths()

    print(f"UDP Server listening on {udp_params.server_IP}:{udp_params.server_port}")
    myserver = udp.open_UDP_server(udp_params)
    client_address = (udp_params.client_IP, udp_params.client_port) 
    
    #main loop. 
    save = 0
    new_file = 1
    new_file_time = datetime.datetime.now()
    while True:
        try:
            try:
                # Listen for a message from LV. If none, will jump to exception
                data, address = myserver.recvfrom(udp_params.buffer)
                message = data.decode('utf-8')
                # print(f"Received from {address}: {message}")
                commands = json.loads(message)
                print(commands)
                for x, obj in commands.items():
                    print(x)
                    if x == 'SetGPIO' and enable_gpio == 1:
                        for y, value in obj.items():
                            print(f"{y} = {value}")
                            gpio.set_gpio_value(gpioID[y]["ID"], gpioID[y]["offset"], value)
                    if x == 'SetMFC' and enable_mfc == 1:
                        for y, value in obj.items():
                            print(f"{y} = {value}")
                            MFC.set_MFC(mfcID, mfc_params["unitAddr"][y]["unitID"], value)
                    if x == 'SetSave':
                        for y, value in obj.items():
                            if y == 'Save':
                                save = int(value)
                                if value == 1:
                                    new_file = 1
                    if x == 'SetTEC':
                        for y, value in obj.items():
                            print(f"{y} = {value}")
                            if y == "TargetT":
                                tecID.set_temp(float(value))
                            if y == "Enable":
                                if value == 1:
                                    tecID.enable()
                                if value == 0:
                                    tecID.disable()
            except TimeoutError:
                # time.sleep(0.5)
                # print("I got nothing")
                if enable_spec == 0:
                    time.sleep(1)
                

            current_time = datetime.datetime.now()
            status = str(current_time)
            
            if enable_tec:
                tec_string = tecID.get_data()
                status += ';TEC:' + json.dumps(tec_string)
            else:
                status += ';TEC:' 

            if enable_gpio:
                gpio_string = gpio.read_gpio_value_all(gpioID)
                status += ';gpio:' + json.dumps(gpio_string)
            else:
                status += ";gpio:"

            if enable_analog:
                analog_string = analog.ReadAI(analog_params)
                status += ';analog:' + json.dumps(analog_string)
            else:
                status += ";analog:"

            if enable_mfc:
                MFC_string = MFC.get_MFC_data(mfcID, mfc_params)
                status += ";MFC:" + json.dumps(MFC_string)
            else:
                status += ";MFC:"

            if enable_spec:
                intensities = specID.intensities()
                spectra_string = ','.join(intensities.astype(str))
                status += ";spec:" + spectra_string
            else:  
                status += ";spec:"

            myserver.sendto(status.encode('utf-8'), client_address)
            # print(f"Sent response to {client_address}: '{status}'") 
            
            if save == 1:            
                time_since_new_file = current_time - new_file_time
                if time_since_new_file.seconds > sec_between_file_saves or new_file == 1:
                    print("Time for a new file!")
                    new_file_time = datetime.datetime.now()
                    aux_file_name = save_data.get_file_name(file_path_name, "aux")
                    spec_file_name = save_data.get_file_name(file_path_name, "spec")
                    new_file = 0

                auxfile = open(aux_file_name, "a")
                auxfile.write(f"{current_time}\t{tec_string}\n")
                auxfile.close()
                
                
                specfile = open(spec_file_name, "a")
                spectra_string = '\t'.join(intensities.astype(str))
                specfile.write(f"{current_time}\t{spectra_string}\n")
                specfile.close()             

        except KeyboardInterrupt:
            print("\tClosing pyCES now")
            if enable_spec:
                ocean_spectrometer.close_spectrometer(specID)
            if enable_tec:
                tecID._tearDown()
            if enable_gpio:
                gpio.release_gpio_pins(gpioID)
            if enable_mfc:
                MFC.close_MFC(mfcID)
            myserver.close()
            break

if __name__ == '__main__':
    main()
