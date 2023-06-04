"""Analyze logs offlinee"""
from datetime import timedelta
import pandas as pd
from gradio import Progress

from smarterbombing.logs import find_character_logs_at_date
from smarterbombing.log_reader import read_all_combat_log_entries, open_character_logs, log_entries_to_dataframe

def _filter_by_direction(events: pd.DataFrame, direction: str):
    filter_outgoing = events['direction'].isin([direction])
    return events[filter_outgoing]

def _filter_unfriendly_damage(events: pd.DataFrame, characters: list[str]):
    filter_friendly = events['subject'].isin(characters)
    return events[~filter_friendly]

def _filter_friendly_damage(events: pd.DataFrame, characters: list[str]):
    filter_friendly = events['subject'].isin(characters)
    return events[filter_friendly]

def _group_by_delta_time(events: pd.DataFrame, max_gap_seconds: float):
    events['delta'] = events['timestamp'].diff() > timedelta(seconds=max_gap_seconds)

    groups = []
    for _, group in events.groupby([events['delta'].cumsum()]):
        groups.append(group)

    return groups

def _total_mean_damage(events: pd.DataFrame, sample_seconds: int):
    damage = events[['timestamp', 'damage']]
    damage = damage.groupby('timestamp').sum()

    dps = damage.rolling(timedelta(seconds=sample_seconds)).mean().fillna(0.0)

    if len(dps.index) > 5000:
        dps = dps.resample('1T').fillna(0.0).mean()

    dps.reset_index(inplace=True)

    return dps

def parse_logs(configuration, date, progress=Progress()):
    """Parse logs collecting events and best effort split into sessions"""

    log_directory = configuration['log_directory']
    characters = configuration['characters']

    progress(0, desc='Locating log files')
    character_logs = find_character_logs_at_date(log_directory, date)

    progress(0.1, desc='Opening log files')
    character_files = open_character_logs(character_logs, characters)

    progress(0.2, desc='Parsing log messages')
    combat_log_entries = list(read_all_combat_log_entries(character_files))
    combat_log_entries = log_entries_to_dataframe(combat_log_entries)

    combat_log_entries.to_csv('out.csv')

    sessions = _group_by_delta_time(combat_log_entries, 350)

    info = []
    data = []

    for session in sessions:
        info.append({
            'Date': date,
            "Start": session.iloc[0]['timestamp'].strftime('%H:%M:%S'),
            "End": session.iloc[-1]['timestamp'].strftime('%H:%M:%S'),
            "Events": len(session.index),
        })

        outgoing_damage = _filter_by_direction(session, 'to')
        outgoing_damage_to_friendly = _filter_friendly_damage(outgoing_damage, characters)
        outgoing_damage_to_hostile = _filter_unfriendly_damage(outgoing_damage, characters)

        incoming_damage = _filter_by_direction(session, 'from')
        incoming_damage_from_friendly = _filter_friendly_damage(incoming_damage, characters)
        incoming_damage_from_hostile = _filter_unfriendly_damage(incoming_damage, characters)

        data.append({
            'all_combat_events': session,
            'outgoing_damage': outgoing_damage,
            'outgoing_hostile_damage': outgoing_damage_to_hostile,
            'outgoing_friendly_damage': outgoing_damage_to_friendly,
            'incoming_damage': incoming_damage,
            'incoming_hostile_damage': incoming_damage_from_hostile,
            'incoming_friendly_damage': incoming_damage_from_friendly,
        })

    progress(1.0, desc='Done')

    return (data, pd.DataFrame(info))

def average_dps(data, rolling_window=120) -> pd.DataFrame:
    """Calculate average dps"""
    return _total_mean_damage(data, rolling_window)
