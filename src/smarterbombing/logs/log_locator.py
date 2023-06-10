"""Functions to help locate Eve Online log files"""
from datetime import datetime
from os import listdir
from os.path import isfile, join
from pathlib import Path
import pandas as pd

def _join_paths(filename: str, directory: str):
    return join(directory, filename)

def _date_string(date: datetime):
    return date.date().strftime('%Y-%m-%d')

def _map_log_file(filename: str):
    [name, _] = filename.split('.')
    parts =  name.split('_', 3)

    if len(parts) == 3:
        (date, time, character_id) = parts
    elif len(parts) == 2:
        (date, time, character_id) = parts + [None]

    date_time = f'{date} {time}'
    created_at = datetime.strptime(date_time, '%Y%m%d %H%M%S')

    return {
        'filename': filename,
        'character_id': character_id,
        'created_at': created_at
    }

def _log_files(directory: str):
    files = [f for f in listdir(directory) if isfile(join(directory, f))]
    files = map(_map_log_file, files)

    return pd.DataFrame(files)

LOG_HEADER_SIG = '------------------------------------------------------------'
LOG_HEADER_TITLE = 'Gamelog'

def _read_log_character_name(log_file_path):
    """Read the character name from log header"""
    with open(log_file_path, 'r', encoding='UTF8') as log_file:
        sig = log_file.readline().strip()
        if LOG_HEADER_SIG not in sig:
            return None

        title = log_file.readline().strip()
        if LOG_HEADER_TITLE not in title:
            return None

        character_line = log_file.readline().strip()
        character_name = character_line[10:]

    return character_name

def get_all_log_dates(directory: str) -> list:
    """
    Get a list of all log dates.

    :param directory: which directory to search for log files

    :returns: list of unique log file dates

    """

    result = _log_files(directory)

    dates = result['created_at'].apply(_date_string)
    dates = sorted(dates.unique(), reverse=True)

    return dates

def get_latest_log_files(directory: str) -> list:
    """
    Get all latest log files.

    :param directory: which directory to search for log files

    :returns: list of log files dict[path, filename, character_id, character, created_at]

    """
    result = _log_files(directory)

    result['path'] = result['filename'].apply(_join_paths, args=(directory, ))

    result = result.sort_values(by='created_at', ascending=False)
    result = result.groupby('character_id', dropna=True).first()
    result['character'] = result['path'].apply(_read_log_character_name)

    return result.to_dict('records')

def default_log_directory():
    """
    Get the default Eve Online logs directory.

    :returns: absolute path to logs directory

    """
    user_directory = join(Path.home(), 'Documents\\EVE\\logs\\Gamelogs')

    return user_directory
