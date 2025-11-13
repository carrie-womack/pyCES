"""
Main pyCES code
================================
*Still very much under development! Don't try to use it like this!*

"""
# Completed modules:
import ocean_spectrometer
import save_data
import udp

## Modules to add later:
# import analog
# import MFCs
# import TEC
# import valves

# Python built-ins
import time
import datetime

def main():

    #read in parameters from the config file
    udp_params = udp.configure_UDP() #read in UDP IP address and port
    save_params = save_data.configure_save() #read in parameters for file saving (file location, minutes between new save, etc.)
    spec_params = ocean_spectrometer.configure_spectrometers() #read in parameters for spectrometer (integration time, etc)
    #TO-DO
    #TEC_params = ??
    #MFC_params = ??
    #analog_params = ??
    #valve_params = ??

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
                    spec = ocean_spectrometer.initialize_spectrometer(spec_params)
                    wavelengths = spec.wavelengths()

                    file_path_name = save_params["location"]
                    min_between_file_saves = save_params["minToSave"]
                    sec_between_file_saves = int(min_between_file_saves * 60)
                    #TO-DO
                    #activate MFCs
                    #activate valves
                    #activate TEC
                    #activate analog
                    
                    # The spectrometer takes ~5 seconds to initialize, so
                    # after that, clear out the UDP buffer of messages received during that time.
                    udp.clear_buffer(myserver, udp_params)

                    mode = 1 #change active mode to 1

                # Prepare and send a response
                myserver.sendto(status.encode('utf-8'), address)
                print(f"Sent response to {address}: '{status}'")

                if "Also, " in message:
                    print("\t\tGotcha boss, gonna do that right now")
            except TimeoutError:
                pass
            if(mode == 1):
                current_time = datetime.datetime.now()

                intensities = spec.intensities()
                status = str(intensities[0])
                
                time_since_new_file = current_time - new_file_time
                if(time_since_new_file.seconds > sec_between_file_saves):
                    print("Time for a new file!")
                    new_file_time = datetime.datetime.now()
                    # aux_file_name = save_data.get_file_name(file_path_name, "aux")
                    spec_file_name = save_data.get_file_name(file_path_name, "spec")

                file = open(spec_file_name, "a")
                timestamp = datetime.datetime.now()

                spectra_string = '\t'.join(intensities.astype(str))
                file.write(f"{timestamp}\t{spectra_string}\n")
                file.close()

                # status = '\t'.join(intensities.astype(str))
                # print(intensities)              

        except KeyboardInterrupt:
            print("\tClosing pyCES now")
            ocean_spectrometer.close_spectrometer(spec)
            #Other shutdown procedures
            myserver.close()
            break

if __name__ == '__main__':
    main()
