"""Functions for parsing Eve Online combat log messages"""
import re
from datetime import datetime

REGEX_REMOVE_LOG_FORMATTING = re.compile('<.*?>')

REGEX_MATCH_COMBAT_LOG = re.compile(
    r'^\[\ (.*?)\ \]\ \((combat)\) (\d*?) (to|from) (.*?)(?!\[.*?\]\(.*?\)) - ')

REGEX_REMOVE_SHIP_TYPE = re.compile(
    r'\[.*?\]\(.*?\)'
)

def strip_log_formatting(log_message: str) -> str:
    """
    Remove any formatting tags from log message.

    :param log_message: a log message
    :returns: the same log message without any formatting tags

    """

    return re.sub(REGEX_REMOVE_LOG_FORMATTING, '', log_message)

def parse_log_timestamp(log_datetime: str) -> datetime:
    """
    Parse log date/time representation to datetime object.

    :param log_datetime: a datetime string, ex. 2023.10.05 15:30:00
    :returns: a datetime object
    :raises ValueError: log_datetime doesn't match expected format

    """

    try:
        return datetime(int(log_datetime[:4]), int(log_datetime[5:7]), int(log_datetime[8:10]),
             int(log_datetime[11:13]), int(log_datetime[14:16]), int(log_datetime[17:]))
    except ValueError as inner:
        raise ValueError(f'Invalid date string: {log_datetime}') from inner

def parse_combat_log_line(log_line):
    """
    Parse one Eve Online combat log line.

    The result will contain the following keys:
    - timestamp (datetime)
    - message_type (str)    -- combat
    - damage (int)          -- eg. 345
    - direction (str)       -- to, from
    - subject (str)         -- eg. Centus Tyrant
    - what (str)            -- eg. Large EMP Smartbomb II
    - quality (str)         -- eg. Hits

    :param log_line: the raw log line
    :returns: a dict containing the parsed log or None if parsing failed

    """

    log_line = re.sub(REGEX_REMOVE_LOG_FORMATTING, '', log_line)

    match = re.match(REGEX_MATCH_COMBAT_LOG, log_line)
    if match is None:
        return None

    (
        timestamp,
        message_type,
        damage,
        direction,
        subject,
    ) = match.groups()

    subject = re.sub(REGEX_REMOVE_SHIP_TYPE, '', subject)

    timestamp = parse_log_timestamp(timestamp)

    log_line = log_line[match.end():]

    parts = log_line.split('-')

    if len(parts) > 1:
        [what, quality] = parts
    else:
        [what, quality] = ['', parts[0]]

    return {
        'timestamp': timestamp,
        'message_type': message_type,
        'damage': int(damage),
        'direction': direction,
        'subject': subject,
        'what': what.strip(),
        'quality': quality.strip(),
    }
