"""
save data files from CES instrument
=======================

"""

from pathlib import Path
import datetime
import time
import random
import numpy
import config

def configure_save():
    """
    read in the save parameters from the config file and return them
    """
    config_data = config.open_config()

    return config_data["save"]

def get_file_name(path_name, file_descriptor):
    """
    get the file name (in format YYYY-MM-DD-XXX-descriptor.txt), 
    where XXX is an incrementing suffix, starting with 001.
    Find the highest existing file for today's date, then add one 
    to the suffix and return the name
    """

    #Get today's date
    current_datetime = datetime.datetime.now()
    # current_year = str(current_datetime.year)
    # current_month = str(current_datetime.month)
    current_date = str(current_datetime.year).zfill(4) + "-" + str(current_datetime.month).zfill(2) + "-" + str(current_datetime.day).zfill(2)

    #Look in the data file for all files that have today's date
    data_path = Path(path_name)
    all_files = list(data_path.glob(current_date + "*" + file_descriptor + "*"))
    
    #If there are none, then we can start with file -001. If there are existing files, sort the list and find the highest suffix
    #Add one to the suffix, and that's the name of the file
    if(len(all_files) == 0):
        current_file = path_name + "/" + current_date + "-001-" + file_descriptor + ".txt"
    else:
        all_files.sort()   
        last_file_full = all_files[-1]  #Grab the last one
        last_file_name = last_file_full.stem    #Get just the name without the path or file extension
        last_file_parts = last_file_name.split("-") #Split file name apart by the "-" separator
        last_file_suffix = last_file_parts[3]   #Grab the suffix, which is the 4th term after year, month, and day
        next_file_suffix = str(int(last_file_suffix) + 1)   #Increment it by 1
        next_file_suffix = next_file_suffix.zfill(3)    #Pad with zeros
        current_file = path_name + "/" + current_date + "-" + next_file_suffix + "-" + file_descriptor + ".txt" #This is the new file name

    print(f"Filename: {current_file}")

    #Convert the file name to a path and return it
    return Path(current_file)

def save_sample_aux_data_to_file(file_name):

    """
    make some fake CES aux data to test file saving
    just save the timestamp and a random number
    """

    file = open(file_name, "a")
    timestamp = datetime.datetime.now()
    value = random.random()
    file.write(f"{timestamp}\t{value:.2f}\n")
    file.close()

def save_sample_spec_data_to_file(file_name):

    """
    make some fake CES spectral data to test file saving
    save the timestamp, plus a random "spectrum" of length 10
    """
    file = open(file_name, "a")
    timestamp = datetime.datetime.now()
    spectra = numpy.random.random(10)
    spectra_string = '\t'.join(spectra.astype(str))
    file.write(f"{timestamp}\t{spectra_string}\n")
    file.close()
    
def main():

    save_params = configure_save()
    file_path_name = save_params["location"]
    min_between_file_saves = save_params["minToSave"]
    print(f"Saving data to: {file_path_name}")

    sec_between_file_saves = int(min_between_file_saves * 60)

    new_file_time = datetime.datetime.now()
    aux_file_name = get_file_name(file_path_name, "aux")
    spec_file_name = get_file_name(file_path_name, "spec")

    while(True):
        try:
            current_time = datetime.datetime.now()
            time_since_new_file = current_time - new_file_time
            print(f"Last new file was {time_since_new_file.seconds:.2f} seconds ago")
            if(time_since_new_file.seconds > sec_between_file_saves):
                print("Time for a new file!")
                new_file_time = datetime.datetime.now()
                aux_file_name = get_file_name(file_path_name, "aux")
                spec_file_name = get_file_name(file_path_name, "spec")
            save_sample_aux_data_to_file(aux_file_name)
            save_sample_spec_data_to_file(spec_file_name)
            time.sleep(1)
        except KeyboardInterrupt:
            print("exiting")
            break

if __name__ == '__main__':
    main()
