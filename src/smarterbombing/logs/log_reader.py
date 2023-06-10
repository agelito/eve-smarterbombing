"""Utilities to help open and read log files"""

from smarterbombing.parsing.combat_log_parser import parse_combat_log_line

def _filter_subjects(event: dict, filter_subjects: list):
    return event['subject'] not in filter_subjects

def _filter_none(event: dict):
    return event is not None

def _apply_character_info(event: dict, character: str, friendly_characters: list):
    event['character'] = character
    event['friendly_fire'] = event['subject'] in friendly_characters
    return event

class LogReader:
    """
    LogReader

    """

    def __init__(self, log_file, friendly_characters: list, filter_subjects: list):
        self.log_file = log_file
        self.friendly_characters = friendly_characters
        self.filter_subjects = filter_subjects
        self.file = None

    def is_open(self):
        """
        Check if file is open

        :returns: True if file is open, otherwise False

        """

        return self.file is not None

    def open(self, seek_to_end: bool = False):
        """
        Open the file for reading

        :param seek_to_end: Seek to end of file after opening it

        """

        self.file = open(self.log_file['path'], 'r', encoding='UTF8')

        if seek_to_end:
            self.file.seek(0, 2)

    def close(self):
        """
        Close the file

        """

        self.file.close()
        self.file = None

    def read_log_events(self):
        """
        Read and parse all available lines from file

        :returns: list of parsed events

        """

        character = self.log_file['character']

        events = filter(_filter_none, map(parse_combat_log_line, self.file.readlines()))
        events = filter(
            lambda evt: _filter_subjects(evt, self.filter_subjects), events
        )
        events = map(
            lambda evt: _apply_character_info(evt, character, self.friendly_characters), events
        )

        return events
