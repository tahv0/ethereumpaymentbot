#!/usr/bin/env python
import os
from configparser import ConfigParser
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONF_DIR = os.path.join(BASE_DIR, 'conf')

CONFIG_FILES = [
    #os.path.join(os.sep, 'usr', 'local', 'etherpaymentbot', 'etherpaymentbot.conf'),  # production
    os.path.join(CONF_DIR, 'settings.ini'),                                           # development
]

config = ConfigParser()


def get_config_value(section, key):
    retval = None
    try:
        config.read(CONFIG_FILES)
        section = config[section]
        # fallback value None
        retval = section.get(key, None)
    except Exception as e:
        print(str(e))
    return retval
