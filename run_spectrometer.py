"""
functions to run the Ocean Insight spectrometers
================================

"""

import seabreeze
seabreeze.use('pyseabreeze')
from seabreeze.spectrometers import list_devices, Spectrometer, SeaBreezeError
import run_config

def check_for_spectrometers():
    """Check for available spectrometers. Returns list of devices, or returns None if none"""

    # Check for available spectrometers.
    try:
        return list_devices()
    except Exception:
        return None

def initialize_spectrometer():
    """If spectrometer available, initialize it with user-input parameters"""

    # Check for spectrometers. If exception, exit
    try:
        devices = list_devices()
    except Exception:
        return None
    
    # Check for number of spectrometers available. If 0, return "No spectrometers available"
    # If more than 1 device, warn user, but use the first one
    if(len(devices) > 0):
        if(len(devices) > 1):
            print("Caution! Multiple spectrometers detected. Only first will be used")

        # Open first available spectrometer
        specID = Spectrometer.from_first_available()
        
        # Print info about chosen spectrometer
        print('Spectrometer opened:\n++++++++++++++++++++++++')
        spec_name = devices[0]
        spec_serial_number = specID.serial_number
        spec_model = specID.model
        spec_num_pix = specID.pixels
        print(spec_name, '\nSerial number: ', spec_serial_number, '\nModel: ', spec_model, '\nPixels: ', spec_num_pix)

        # Set integration time (in microseconds) and check it's a valid number
        config_data = run_config.open_config()
        integ_time_us = config_data["spectrometer"]["integration_time"]
        print(f"Setting integration time to {integ_time_us} microseconds")
        min_integ_time, max_integ_time  = specID.integration_time_micros_limits
        if(integ_time_us > max_integ_time or integ_time_us < min_integ_time):
            print("Error! Specified integration time is outside the acceptable range")
            return None
        specID.integration_time_micros(integ_time_us)

        # spec_features = specID.features
        # print(spec_features)
        return specID
    else:
        print("No spectrometers found!")
        return None

def take_spectra(specID, num_spectra):
    """ Take a certain number of spectra, given by num_spectra"""

    wavelengths = specID.wavelengths()
    print(wavelengths)
    
    for i in range(0, num_spectra):
        intensities = specID.intensities()
        print(intensities)

def close_spectrometer(specID):
    specID.close()

def main(num_spectra):
    spec = initialize_spectrometer()
    if(spec):
        take_spectra(spec, num_spectra)
        close_spectrometer(spec)

if __name__ == '__main__':
    main(5)

