"""Utility to help read lines from log files"""
import re
from datetime import datetime
from typing import IO
from parse import search
import pandas as pd

CLEAN_MARKUP_REGEX = re.compile('<.*?>')
CLEAN_TIME_AND_TYPE_REGEX = re.compile(r'^(\[\s.*\s\])[ ](\(combat\)[ ])')
CLEAN_CORP_AND_SHIP_REGEX = re.compile(r'\[.*')

class CharacterLogFile:
    """Class representing a character name and log file handle"""
    def __init__(self, filename: str, character: str, file: IO[any]):
        self.filename = filename
        self.character = character
        self.file = file

    def is_open(self) -> bool:
        """Return boolean indicating if file is open"""
        return not self.file.closed

    def close(self):
        """Close the file handle"""
        self.file.close()

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

def _read_and_parse_combat_log_lines(log: CharacterLogFile):
    file = log.file
    character = log.character

    parsed_lines = []

    for line in file.readlines():
        parsed = _parse_combat_log_line(line, character)

        if parsed is not None:
            parsed_lines.append(parsed)

    return parsed_lines

def _flatten(in_list):
    return [item for ll in in_list for item in ll]

def read_all_combat_log_entries(character_files):
    """Read all combat log entries from character log files"""
    if len(character_files) == 0:
        return []

    character_log_entries = map(_read_and_parse_combat_log_lines, character_files)

    return _flatten(character_log_entries)

def open_log_files(
        character_logs,
        filter_characters,
        seek_to_end: bool = False
    ):
    """Open character log files"""
    character_files = []
    for character_log in character_logs:
        name = character_log['character_name']
        path = character_log['path']

        if name not in filter_characters:
            continue

        print(f'open {name} log at {path}')
        file = open(path, 'r', encoding='UTF8')
        if seek_to_end:
            file.seek(0, 2)

        character_files.append(CharacterLogFile(path, name, file))
    return character_files

def log_entries_to_dataframe(log_entries) -> pd.DataFrame:
    """Create DataFrame from log entries"""
    columns = ['character','timestamp','type','damage','direction','subject','what']
    result = pd.DataFrame(log_entries, columns=columns)
    result.sort_values('timestamp', ascending=True)

    return result
