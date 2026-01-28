
"""
Main pyCES code
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
from pathlib import Path

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
    current_state = 1
    aux_file_name = ""
    while True:
        try:
            try:
                # Listen for a message from LV. If none, will jump to exception
                data, address = myserver.recvfrom(udp_params.buffer)
                message = data.decode('utf-8')
                commands = json.loads(message)
                # print(commands)
                for x, obj in commands.items():
                    print(x)
                    if x == 'SetGPIO' and enable_gpio:
                        for y, value in obj.items():
                            gpio.set_gpio_value(gpioID[y]["ID"], gpioID[y]["offset"], value)
                    if x == 'SetMFC' and enable_mfc:
                        for y, value in obj.items():
                            MFC.set_MFC(mfcID, mfc_params["unitAddr"][y]["unitID"], value)
                    if x == 'SetSave':
                        for y, value in obj.items():
                            if y == 'Save':
                                save = int(value)
                                if value == 1:
                                    new_file = 1
                    if x == 'SetTEC' and enable_tec:
                        for y, value in obj.items():
                            if y == "TargetT":
                                tecID.set_temp(float(value))
                            if y == "Enable":
                                if value == 1:
                                    tecID.enable()
                                if value == 0:
                                    tecID.disable()
                    if x == 'SetState':
                        for y, value in obj.items():
                            current_state = int(value)

            except TimeoutError:
                if enable_spec == 0:
                    time.sleep(1)
            
            current_time = datetime.datetime.now()
            status = str(current_time) + ";file:" + aux_file_name
            aux_string = [time.time() + 2082844800, current_state]
            # start_time = time.time()
            if enable_tec:
                tec_string = tecID.get_data()
                tec_aux_string = TEC.makeAuxFileString(tec_string)
                aux_string.extend(tec_aux_string)
                status += ';TEC:' + json.dumps(tec_string)
            else:
                status += ';TEC:' 
            # end_time = time.time()
            if enable_gpio:
                gpio_string = gpio.read_gpio_value_all(gpioID)
                gpio_aux_string = gpio.makeAuxFileString(gpio_string)
                aux_string.extend(gpio_aux_string)
                status += ';gpio:' + json.dumps(gpio_string)
            else:
                status += ";gpio:"
            
            if enable_analog:
                analog_string = analog.ReadAI(analog_params)
                analog_aux_string = analog.makeAuxFileString(analog_string)
                aux_string.extend(analog_aux_string)
                status += ';analog:' + json.dumps(analog_string)
            else:
                status += ";analog:"
            
            if enable_mfc:
                MFC_string = MFC.get_MFC_data(mfcID, mfc_params)
                MFC_aux_string = MFC.makeAuxFileString(MFC_string)
                aux_string.extend(MFC_aux_string)
                status += ";MFC:" + json.dumps(MFC_string)
            else:
                status += ";MFC:"
            
            if enable_spec:
                intensities = specID.intensities()
                spectra_string = ','.join(intensities.astype(str))
                status += ";spec:" + spectra_string
            else:  
                status += ";spec:"
            
            # print(aux_string)
            
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
                    # print(aux_file_name)
                    name_split = aux_file_name.split("-")
                    # print(name_split)
                    suffix = name_split[-2]
                    # print(suffix)
                    # suffix = file_full_name.split("-")
                    #aux_header = f"Timestamp{suffix}\tCurrent_state{suffix}\tT_C_LED{suffix}\tT_C_Heatsink{suffix}\tTEC_I{suffix}\tTEC_V{suffix}\tV_ZAHe{suffix}\tV_NO2addn{suffix}\tV_LED{suffix}\tCavity_T{suffix}\tBox_T{suffix}\tCavity_P{suffix}\tCavity_flow{suffix}\tCavity_flow_setpoint{suffix}\tCavity_MFC_pressure{suffix}\tCavity_MFC_temp{suffix}\tOverflow{suffix}\tOverflow_setpoint{suffix}\tOverflow_MFC_pressure{suffix}\tOverflow_MFC_temperature{suffix}\n"
                    aux_header = f"Timestamp{suffix}\tCurrent_state{suffix}\tT_C_LED{suffix}\tT_C_Heatsink{suffix}\tTEC_I{suffix}\tTEC_V{suffix}\tV_ZAHe{suffix}\tV_NO2addn{suffix}\tV_LED{suffix}\tCavity_T{suffix}\tBox_T{suffix}\tCavity_P{suffix}\tCavity_flow{suffix}\tCavity_flow_setpoint{suffix}\tCavity_MFC_temp{suffix}\tOverflow{suffix}\tOverflow_setpoint{suffix}\tOverflow_MFC_temperature{suffix}\n"

                    auxfile = open(Path(aux_file_name), "a")
                    auxfile.write(f"{aux_header}\n")
                    auxfile.close()

                auxfile = open(Path(aux_file_name), "a")
                aux_string_to_save = '\t'.join([str(s) for s in aux_string])
                auxfile.write(f"{aux_string_to_save}\n")
                auxfile.close()
                
                
                specfile = open(Path(spec_file_name), "a")
                spectra_string = '\t'.join(intensities.astype(str))
                specfile.write(f"{current_time}\t{spectra_string}\n")
                specfile.close()             
            
            # loop = end_time - start_time
            # print(f"Loop time: {loop} seconds")
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
