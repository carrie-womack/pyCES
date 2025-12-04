"""
Runs the Meerstetter TEC-1092 module
*********
Under development. Don't use yet!
"""

import time

def configure_TEC():
    """Opens config file TEC parameters"""
    config_data = config.open_config()

    return config_data["TEC"]