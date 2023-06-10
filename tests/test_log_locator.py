from datetime import datetime
from os import path
import tempfile
from smarterbombing.logs.log_locator import (
    default_log_directory, get_all_log_dates, get_latest_log_files
)

LOG_HEADER_TEMPLATE = """------------------------------------------------------------
  Gamelog
  Listener: |character|
  Session Started: |date|2021.02.25 07:23:40
------------------------------------------------------------
"""

SAMPLE_LOGS_SPEC = [
    { 'character_id': '12345', 'created_at': datetime(2020, 11, 1, 13, 0, 0),
     'character_name': 'John Travolta'},
    { 'character_id': '12345', 'created_at': datetime(2020, 11, 1, 21, 45, 0),
     'character_name': 'John Travolta'},
    { 'character_id': '44444', 'created_at': datetime(2022, 5, 12, 1, 22, 50),
     'character_name': 'Michael'},
    { 'character_id': '44444', 'created_at': datetime(2020, 2, 29, 2, 23, 20),
     'character_name': 'Michael'},
    { 'character_id': '99999', 'created_at': datetime(1995, 11, 1, 0, 0, 1),
     'character_name': 'Gill Bates'},
]

def _create_sample_logs(filespec: list, directory: str):
    for fs in filespec:
        file_name = f'{fs["created_at"].strftime("%Y%m%d_%H%M%S")}_{fs["character_id"]}.txt'

        header = LOG_HEADER_TEMPLATE.replace('|character|', fs['character_name'])
        header = header.replace('|date|', fs["created_at"].strftime('%Y.%m.%d %H:%M:%S'))

        with open(path.join(directory, file_name), 'w', encoding='UTF8') as f:
            f.write(header)

def test_default_log_directory_is_absolute():
    default_directory = default_log_directory()
    assert path.isabs(default_directory)

def test_get_latest_log_files():
    with tempfile.TemporaryDirectory() as tmp_dir:
        _create_sample_logs(SAMPLE_LOGS_SPEC, tmp_dir)

        log_files = get_latest_log_files(tmp_dir)

        character_names = list(map(lambda l: l['character'], log_files))
        created_at_dates = list(map(lambda l: l['created_at'], log_files))

        expected_characters = ['Michael', 'John Travolta', 'Gill Bates']

        for character in expected_characters:
            assert character in character_names

        expected_dates = [
            datetime(2020, 11, 1, 21, 45, 0),
            datetime(2022, 5, 12, 1, 22, 50),
            datetime(1995, 11, 1, 0, 0, 1),
        ]

        for date in expected_dates:
            assert date in created_at_dates

def test_get_all_log_dates():
    with tempfile.TemporaryDirectory() as tmp_dir:
        _create_sample_logs(SAMPLE_LOGS_SPEC, tmp_dir)
        log_dates = get_all_log_dates(tmp_dir)

        expected_dates = [
            '2022-05-12',
            '2020-11-01',
            '2020-02-29',
            '1995-11-01',
        ]

        assert log_dates == expected_dates
