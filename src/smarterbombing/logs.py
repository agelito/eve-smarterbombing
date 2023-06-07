"""Functions for finding and filtering log files"""
from datetime import datetime
from os import listdir
from os.path import isfile, join
from pathlib import Path
import pandas as pd

def _map_log_file(filename: str):
    """Retrieve structured data about log file based on the file name"""
    [name, _] = filename.split('.')
    parts =  name.split('_', 3)

    if len(parts) == 3:
        (date, time, account) = parts
    elif len(parts) == 2:
        (date, time, account) = parts + [None]

    date_time = f'{date} {time}'
    created_at = datetime.strptime(date_time, '%Y%m%d %H%M%S')

    return {
        'filename': filename,
        'account': account,
        'created_at': created_at
    }

def _find_log_files(eve_logs_directory):
    """Find all log files in provided directory"""
    files = [f for f in listdir(eve_logs_directory) if isfile(join(eve_logs_directory, f))]
    files = list(map(_map_log_file, files))

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
        character_name = character_line[:9]

    return character_name

def _create_log_result(directory, log):
    log_path = join(directory, log['filename'])
    character_name = _read_log_character_name(log_path)

    return {
        'path': log_path,
        'character_id': log['account'],
        'character_name': character_name,
        'created_at': log['created_at'],
    }

def find_most_recent_character_logs(directory):
    """Find the most recent log file for each account"""
    log_files = _find_log_files(directory)

    log_files.dropna(inplace=True)
    log_files.sort_values(by='created_at', inplace=True, ascending=False)

    unique_accounts = log_files['account'].unique()

    result = []

    for account in unique_accounts:
        account_logs = log_files.loc[log_files['account'] == account]
        if account_logs.count == 0:
            continue

        first_log = account_logs.iloc[0]

        result.append(_create_log_result(directory, first_log))

    return result

def find_character_logs_at_date(directory, date):
    """Find all log files at date"""
    log_files = _find_log_files(directory)
    log_files.dropna(inplace=True)

    log_files['date'] = log_files['created_at'].apply(_date_string)

    logs_at_date = log_files['date'].isin([date])
    filtered_logs = log_files[logs_at_date]

    return list(
        filtered_logs.apply(lambda log: _create_log_result(directory, log), axis=1)
    )

def _date_string(date: datetime):
    return date.date().strftime('%Y-%m-%d')

def find_all_dates(directory):
    """Find all available log file dates"""
    log_files = _find_log_files(directory)
    log_files.dropna(inplace=True)

    return list(log_files['created_at'].apply(_date_string).unique())

def default_log_directory():
    """Retrieve the default Eve log directory"""
    user_directory = join(Path.home(), 'Documents\\EVE\\logs\\Gamelogs')

    return user_directory
