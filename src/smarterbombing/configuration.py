"""Configuration helpers"""
import os
from os.path import isfile
from yaml import (
    load as ymload,
    dump as ymdump,
    Loader, Dumper)
from smarterbombing.logs.log_locator import default_log_directory

CONFIGURATION_FILE_NAME = 'smarterbombing.yaml'
CONFIGURATION_MAX_SQUADS = 10

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

    squads = []
    for i in range(CONFIGURATION_MAX_SQUADS):
        squads.append({ 'squad_name': f'Squad {i + 1}', 'characters': [] })

    configuration = {}
    configuration['log_directory'] = default_log_directory()
    configuration['squads'] = squads
    configuration['dps_average_seconds'] = 10
    configuration['live_graph_minutes'] = 5
    configuration['site_boundary_minimum_seconds'] = 20
    configuration['ignore_list'] = ['Heavy Missile', 'Light Missile']
    configuration['graph_width'] = 530

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
        save(configuration, name_prefix=name_prefix)

        return configuration

    with open(path, 'r', encoding='UTF8') as config_file:
        return ymload(config_file, Loader=Loader)

def delete(name_prefix=''):
    """
    Delete configuration file.

    :param name_prefix: append name or path in front of configuration file name

    """
    print(f'deleting: {name_prefix}{CONFIGURATION_FILE_NAME}')

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

def create_squad(configuration: dict, squad_name: str):
    """
    Create a new squad.

    :param configuration: configuration
    :param squad_name: the squad name

    """

    squad = {
        'squad_name': squad_name,
        'characters': []
    }

    squads = configuration.get('squads', [])
    squads.append(squad)

def get_graph_width(configuration: dict) -> int:
    """
    Get graph width option.

    :param configuration: configuration
    
    :returns: The configured graph width or None if not set

    """

    return configuration.get('wider_graphs', None)
