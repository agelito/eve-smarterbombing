"""Configuration helpers"""
import json
from os.path import isfile
from smarterbombing.logs import default_log_directory

def load_configuration(configuration_path):
    """Load configuration"""

    if not isfile(configuration_path):
        configuration = {
            'log_directory': default_log_directory(),
            'characters': [],
            'dps_rolling_window_seconds': 10,
        }

        save_configuration(configuration, configuration_path)

        return configuration

    with open(configuration_path, 'rt', encoding='UTF8') as config_file:
        return json.load(config_file)
    
def save_configuration(configuration, configuration_path):
    """Save configuration"""
    with open(configuration_path, 'wt', encoding='UTF8') as config_file:
        json.dump(configuration, config_file)