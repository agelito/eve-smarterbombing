"""Utility to help read lines from log files"""
import time
import re
from datetime import datetime
from parse import search
import pandas as pd

CLEAN_MARKUP_REGEX = re.compile('<.*?>')
CLEAN_TIME_AND_TYPE_REGEX = re.compile(r'^(\[\s.*\s\])[ ](\(combat\)[ ])')
CLEAN_CORP_AND_SHIP_REGEX = re.compile(r'\[.*')

def _parse_combat_log_line(line, character):
    parsed_line = search('[ {} ] ({})', line)
    if parsed_line is None:
        return None

    timestamp = datetime.strptime(parsed_line[0], '%Y.%m.%d %H:%M:%S')
    message_type = parsed_line[1]

    if message_type != 'combat':
        return None

    clean_line = re.sub(CLEAN_MARKUP_REGEX, '', line)
    clean_line = re.sub(CLEAN_TIME_AND_TYPE_REGEX, '', clean_line)

    parsed_damge_direction = search('{:d} {:l}', clean_line)

    if parsed_damge_direction is None:
        return None

    if parsed_damge_direction[1] not in ('to', 'from'):
        return None

    damage = parsed_damge_direction[0]
    direction = parsed_damge_direction[1]

    if direction == 'to':
        clip_index = clean_line.find('to') + 3
    elif direction == 'from':
        clip_index = clean_line.find('from') + 5

    subject_what_quality = clean_line[clip_index:].split(' - ')
    if len(subject_what_quality) < 2:
        return None

    subject = subject_what_quality[0]
    subject = re.sub(CLEAN_CORP_AND_SHIP_REGEX, '', subject)
    what = subject_what_quality[1]

    return [
        character,
        timestamp,
        message_type,
        damage,
        direction,
        subject,
        what ]

def _read_combat_log_with_character(character_file):
    (character, file) = character_file

    return _parse_combat_log_line(file.readline(), character)

def _read_all_combat_log_entries(character_file):
    (character, file) = character_file

    for line in file.readlines():
        parsed = _parse_combat_log_line(line, character)

        if parsed is None:
            continue

        yield parsed

def open_character_logs(character_logs, filter_characters):
    """Open character log files"""
    character_files = []
    for character_log in character_logs:
        name = character_log['character_name']
        path = character_log['path']

        if name not in filter_characters:
            continue

        print(f'open {name} log at {path}')
        character_files.append((
            name, open(path, 'r', encoding='UTF8')
        ))
    return character_files

def read_all_combat_log_entries(character_files):
    """Read all combat log entries from character log files"""
    character_log_entries = map(_read_all_combat_log_entries, character_files)

    for character_entries in character_log_entries:
        for entry in character_entries:
            yield entry

def follow_files(character_files):
    """Continually read (character, line) pairs from files"""

    # Seek to end of files
    for character_file_pair in character_files:
        (_, file) = character_file_pair
        file.seek(0, 2)

    while True:
        all_lines = map(_read_combat_log_with_character, character_files)
        all_lines = list(filter(lambda l: l is not None, all_lines))

        if len(all_lines) == 0:
            time.sleep(0.01)
            continue

        for line in all_lines:
            yield line

def log_entries_to_dataframe(log_entries) -> pd.DataFrame:
    """Create DataFrame from log entries"""
    columns = ['character','timestamp','type','damage','direction','subject','what']
    result = pd.DataFrame(log_entries, columns=columns)
    result.sort_values('timestamp', ascending=True)

    return result
