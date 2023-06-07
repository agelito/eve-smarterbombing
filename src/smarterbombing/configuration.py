"""Configuration helpers"""
import os
from os.path import isfile
from yaml import (
    load as ymload,
    dump as ymdump,
    Loader, Dumper)
from smarterbombing.logs import default_log_directory

CONFIGURATION_FILE_NAME = 'smarterbombing.yml'

def exists(name_prefix='') -> bool:
    """
    Check if configuration file exists.

    :returns: True if configuration exists otherwise False.

    """
    return isfile(f'{name_prefix}{CONFIGURATION_FILE_NAME}')

def create_default() -> dict:
    """
    Create configuration file with default options.

    :returns: dict with the created configuration.
    
    """

    configuration = {}
    configuration['log_directory'] = default_log_directory()
    configuration['squads'] = []
    configuration['dps_rolling_window_seconds'] = 10

    return configuration


def save(configuration: dict, name_prefix=''):
    """
    Save configuration to configuration file.

    :param configuration: dict with configuration options

    """

    with open(f'{name_prefix}{CONFIGURATION_FILE_NAME}', 'w', encoding='UTF8') as config_file:
        ymdump(configuration, config_file, Dumper=Dumper)

def load(create_if_missing=False, name_prefix='') -> dict:
    """
    Load configuration from configuration file.

    :param create_if_missing: create default configuration if there is no configuration file.

    :returns: dict with configuration options or None if file doesn't exist
    
    """
    path = f'{name_prefix}{CONFIGURATION_FILE_NAME}'

    if not isfile(path):
        if not create_if_missing:
            return None

        configuration = create_default()
        save(configuration)

        return configuration

    with open(path, 'r', encoding='UTF8') as config_file:
        return ymload(config_file, Loader=Loader)

def delete(name_prefix=''):
    """
    Delete configuration file.

    :param name_prefix: append name or path in front of configuration file name

    """

    if exists(name_prefix=name_prefix):
        os.unlink(f'{name_prefix}{CONFIGURATION_FILE_NAME}')

def get_squads(configuration: dict) -> list:
    """
    Get list of squads from configuration.

    :param configuration: configuration

    :returns: list[dict] squads

    """

    return configuration.get('squads', {})

def get_log_directory(configuration: dict) -> str:
    """
    Get log directory from configuration.

    :param configuration: configuration

    :returns: str log directory
    """

    return configuration.get('log_directory', {})

def get_dps_average_seconds(configuration: dict) -> int:
    """
    Get DPS average seconds from configuration.

    :param configuration: configuration

    :returns: int dps average rolling window in seconds

    """

    return configuration.get('dps_average_seconds', 10)
