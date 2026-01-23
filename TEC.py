"""
Runs the Meerstetter TEC-1092 module
"""
import sys
sys.path.append('/home/debian/pyMeCom')
import time
import config
from mecom import MeComSerial, ResponseException, WrongChecksum

# default queries from command table below
DEFAULT_QUERIES = [
    "device status",
    "loop status",
    "object temperature",
    "sink temperature",
    "target object temperature",
    "output current",
    "output voltage"
    # "device temperature"
]
# SET_OPTIONS = {
#     "reset": []
#     "setT"
#     "enable"
#     "disable"
# }
# syntax
# { display_name: [parameter_id, unit, abbrv], }
COMMAND_TABLE = {
    "device status": [104, "", "stat"],
    "loop status": [1200, "", "Tstb"],
    "object temperature": [1000, "degC", "objT"],
    "target object temperature": [3000, "degC", "tarT"],
    "output current": [1020, "A", "tecI"],
    "output voltage": [1021, "V", "tecV"],
    "sink temperature": [1001, "degC", "snkT"],
    "ramp temperature": [1011, "degC", "rmpT"],
    # "device temperature": [1063, "degC", "devT"]
}

def configure_TEC():
    """
    read in the TEC parameters from the config file and return them
    """
    config_data = config.open_config()

    return config_data["TEC"]    

class MeerstetterTEC(object):
    """
    Controlling TEC devices via serial.
    ****
    Written by Meerstetter, lightly adapted here
    """

    def _tearDown(self):
        self.session().stop()

    def __init__(self, port=None, channel=1, baudrate=57600,queries=DEFAULT_QUERIES, *args, **kwars):
        self.channel = channel
        self.port = port
        self.baudrate = baudrate
        self.queries = queries
        self.timeout = 0.05
        self._session = None
        self._connect()

    def _connect(self):
        # open session
        self._session = MeComSerial(serialport=self.port, baudrate=self.baudrate, timeout=self.timeout)
        # get device address
        self.address = self._session.identify()

    def session(self):
        if self._session is None:
            self._connect()
        return self._session

    def get_data(self):
        data = {}
        for description in self.queries:
            id, unit, abbrv = COMMAND_TABLE[description]
            try:
                value = self.session().get_parameter(parameter_id=id, address=self.address, parameter_instance=self.channel)
                # data.update({description: (value, unit)})
                if(isinstance(value, float)):
                    new_value = int(value * 1000) / 1000
                    value = new_value
                data.update({abbrv: value})
            except (ResponseException, WrongChecksum) as ex:
                self.session().stop()
                self._session = None
        return data

    def set_temp(self, value):
        """
        Set object temperature of channel to desired value.
        :param value: float
        :param channel: int
        :return:
        """
        # assertion to explicitly enter floats
        assert type(value) is float
        return self.session().set_parameter(parameter_id=3000, value=value, address=self.address, parameter_instance=self.channel)

    def _set_enable(self, enable=True):
        """
        Enable or disable control loop
        :param enable: bool
        :param channel: int
        :return:
        """
        value, description = (1, "on") if enable else (0, "off")
        return self.session().set_parameter(value=value, parameter_name="Output Enable Status", address=self.address, parameter_instance=self.channel)

    def enable(self):
        return self._set_enable(True)

    def disable(self):
        return self._set_enable(False)

def makeAuxFileString(tec_string):
    aux_string = []
    aux_string.append(tec_string["objT"])
    aux_string.append(tec_string["snkT"])
    aux_string.append(tec_string["tecI"])
    aux_string.append(tec_string["tecV"])
    return aux_string

if __name__ == '__main__':
    # initialize controller
    tec_params = configure_TEC()
    mc = MeerstetterTEC(port=tec_params["port"], channel=tec_params["channel"], baudrate=tec_params["baudrate"])
    
    if(len(sys.argv) > 1):
        if(sys.argv[1] == 'enable'):
            mc.enable()
        elif(sys.argv[1] == 'disable'):
            mc.disable()
        elif(sys.argv[1] == 'setT'):
            mc.set_temp(float(sys.argv[2]))
        else:
            print("Command not recognized!")

    while True:
        try:
            results = mc.get_data()
            print(results)
            auxfile_string = makeAuxFileString(results)
            print(auxfile_string)
            time.sleep(1)
        except KeyboardInterrupt:
            print("exiting")
            mc._tearDown()
            break