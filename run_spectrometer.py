"""
functions to run the Ocean Insight spectrometers
================================

Author: Carrie Womack
Last updated: Oct 15, 2025

"""

import seabreeze
seabreeze.use('pyseabreeze')
from seabreeze.spectrometers import list_devices, Spectrometer, SeaBreezeError

def scratch():
    specID = Spectrometer.from_first_available()
    close(specID)
    # devices = list_devices()
    # try:
    #     # raise SeaBreezeError
    #     # spec = Spectrometer.from_first_available()
    #     spec = list_devices()

    # except Exception as inst:
    #     print(type(inst))    # the exception type
    #     print(inst.args)     # arguments stored in .args
    #     print(inst)          # __str__ allows args to be printed directly,
    #                         # but may be overridden in exception subclasses
    #     # x, y = inst.args     # unpack args
    #     # print('x =', x)
    #     # print('y =', y)
    #     return inst.strerror

def check_for_spectrometers():
    """Check for available spectrometers. Hard exit if none"""

    # Check for available spectrometer. Return error string
    try:
        devices = list_devices()
        # print(devices)
        return ""

    except Exception as inst:
        return inst.strerror

def initialize_spectrometer():
    """If spectrometer available, initialize it with user-input parameters"""

    # Check for multiples, and warn the user.
    devices = list_devices()
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
    integ_time_us = 1000000
    min_integ_time, max_integ_time  = specID.integration_time_micros_limits
    if(integ_time_us > max_integ_time or integ_time_us < min_integ_time):
        print("Error! Specified integration time is outside the acceptable range")
        return 0
    specID.integration_time_micros(integ_time_us)

    spec_features = specID.features
    print(spec_features)
    return specID

def take_spectra(specID, num_spectra):
    """ Take a certain number of spectra, given by num_spectra"""

    wavelengths = specID.wavelengths()
    print(wavelengths)
    
    for i in range(0, num_spectra):
        intensities = specID.intensities()
        print(intensities)

def close_spectrometer(specID):
    specID.close()

def main():
    error = check_for_spectrometers()
    if(len(error) == 0):
        spec = initialize_spectrometer()
        if(spec != 0):
            take_spectra(spec, 5)

        close_spectrometer(spec)
    else:
        print(error)

if __name__ == '__main__':
    main()
    # scratch()

