"""
Main pyCES code
================================
*Still very much under development! Don't try to use it like this!*

"""
# Completed modules:
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
    MFC_params = MFC.configure_MFC() #read in MFC addresses

    #set initial mode to 0 (Idle mode), and status to an empty string...
    #...open up the UDP socket and start listening
    mode = 0
    status = f""
    print(f"UDP Server listening on {udp_params.IP}:{udp_params.port}")
    myserver = udp.open_UDP_server(udp_params)

    #main loop. Idle until an Activate message is received from LabView (LV)
    while True:
        try:
            try:
                # Listen for a message from LV. If none, will jump to exception
                data, address = myserver.recvfrom(udp_params.buffer)
                message = data.decode('utf-8')
                print(f"Received from {address}: {message}")

                # If an activate message is received for the first time (i.e. mode is 0)
                # then activate the different components of the CES instrument
                if ("Activate" in message) and mode == 0:
                    #create a spectrometer instance
                    # spec = ocean_spectrometer.initialize_spectrometer(spec_params)
                    # wavelengths = spec.wavelengths()

                    # file_path_name = save_params["location"]
                    # min_between_file_saves = save_params["minToSave"]
                    # sec_between_file_saves = int(min_between_file_saves * 60)

                    tec = TEC.MeerstetterTEC(port=tec_params["port"], channel=tec_params["channel"], baudrate=tec_params["baudrate"])
                    gpioID = gpio.initialize_gpio(gpio_params)
                    
                    #TO-DO
                    #activate MFCs
                    
                    # The spectrometer takes ~5 seconds to initialize, so
                    # after that, clear out the UDP buffer of messages received during that time.
                    udp.clear_buffer(myserver, udp_params)
                    status = f"Activation received"
                    mode = 1 #change active mode to 1

                # # Prepare and send a response
                # myserver.sendto(status.encode('utf-8'), address)
                # print(f"Sent response to {address}: '{status}'")

                if "Also, " in message:
                    print("\t\tGotcha boss, gonna do that right now")
            except TimeoutError:
                time.sleep(0.5)
                # pass
            if(mode == 1):
                current_time = datetime.datetime.now()
                status = str(current_time)
                # intensities = spec.intensities()
                tec_string = tec.get_data()
                status += ';TEC:' + json.dumps(tec_string)

                gpio_string = gpio.read_gpio_value_all(gpioID)
                status += ';gpio:' + json.dumps(gpio_string)

                analog_string = analog.ReadAI(analog_params)
                status += ';analog:' + json.dumps(analog_string)
                
                myserver.sendto(status.encode('utf-8'), address)
                print(f"Sent response to {address}: '{status}'")               
                # time_since_new_file = current_time - new_file_time
                # if(time_since_new_file.seconds > sec_between_file_saves):
                #     print("Time for a new file!")
                #     new_file_time = datetime.datetime.now()
                #     # aux_file_name = save_data.get_file_name(file_path_name, "aux")
                #     spec_file_name = save_data.get_file_name(file_path_name, "spec")

                # file = open(spec_file_name, "a")
                # timestamp = datetime.datetime.now()

                # spectra_string = '\t'.join(intensities.astype(str))
                # file.write(f"{timestamp}\t{spectra_string}\n")
                # file.close()

                # status = '\t'.join(intensities.astype(str))
                # print(intensities)              
                # Prepare and send a response

        except KeyboardInterrupt:
            print("\tClosing pyCES now")
            if(mode == 1):
                # ocean_spectrometer.close_spectrometer(spec)
                #Other shutdown procedures
                tec._tearDown()
            myserver.close()
            break

if __name__ == '__main__':
    main()
