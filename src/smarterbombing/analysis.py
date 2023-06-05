"""Analyze logs offlinee"""
from datetime import datetime, timedelta
import pandas as pd
from gradio import Progress

from smarterbombing.logs import find_character_logs_at_date
from smarterbombing.log_reader import\
    read_all_combat_log_entries,\
    open_log_files,\
    log_entries_to_dataframe

EVENT_GROUP_ALL_DAMAGE='all_combat_events'
EVENT_GROUP_OUTGOING_DAMAGE='outgoing_damage'
EVENT_GROUP_OUTGOING_HOSTILE_DAMAGE='outgoing_hostile_damage'
EVENT_GROUP_OUTGOING_FRIENDLY_DAMAGE='outgoing_friendly_damage'
EVENT_GROUP_INCOMING_DAMAGE='incoming_damage'
EVENT_GROUP_INCOMING_HOSTILE_DAMAGE='incoming_hostile_damage'
EVENT_GROUP_INCOMING_FRIENDLY_DAMAGE='incoming_friendly_damage'

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

def group_damage_events(events: pd.DataFrame, characters: list[str]):
    """Sort combat events by type and direction"""
    outgoing_damage = _filter_by_direction(events, 'to')
    outgoing_damage_to_friendly = _filter_friendly_damage(outgoing_damage, characters)
    outgoing_damage_to_hostile = _filter_unfriendly_damage(outgoing_damage, characters)

    incoming_damage = _filter_by_direction(events, 'from')
    incoming_damage_from_friendly = _filter_friendly_damage(incoming_damage, characters)
    incoming_damage_from_hostile = _filter_unfriendly_damage(incoming_damage, characters)

    return {
        EVENT_GROUP_ALL_DAMAGE: events,
        EVENT_GROUP_OUTGOING_DAMAGE: outgoing_damage,
        EVENT_GROUP_OUTGOING_HOSTILE_DAMAGE: outgoing_damage_to_hostile,
        EVENT_GROUP_OUTGOING_FRIENDLY_DAMAGE: outgoing_damage_to_friendly,
        EVENT_GROUP_INCOMING_DAMAGE: incoming_damage,
        EVENT_GROUP_INCOMING_HOSTILE_DAMAGE: incoming_damage_from_hostile,
        EVENT_GROUP_INCOMING_FRIENDLY_DAMAGE: incoming_damage_from_friendly,
    }

def parse_logs(configuration, date, progress=Progress()):
    """Parse logs collecting events and best effort split into sessions"""

    log_directory = configuration['log_directory']
    characters = configuration['characters']

    progress(0, desc='Locating log files')
    character_logs = find_character_logs_at_date(log_directory, date)

    progress(0.1, desc='Opening log files')
    character_files = open_log_files(character_logs, characters)

    progress(0.2, desc='Parsing log messages')
    combat_log_entries = list(read_all_combat_log_entries(character_files))
    combat_log_entries = log_entries_to_dataframe(combat_log_entries)

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

        grouped_events = group_damage_events(session, characters)

        data.append(grouped_events)

    progress(1.0, desc='Done')

    return (data, pd.DataFrame(info))

def average_dps_per_character(data: pd.DataFrame, average_seconds: int = 10) -> pd.DataFrame:
    """Calculate average DPS per character"""

    if data.empty:
        return data

    data = data[['timestamp', 'character', 'damage']]
    data = data.groupby(['timestamp', 'character']).sum().reset_index()
    data = data.pivot(
        index='timestamp',
        columns='character',
        values='damage'
    ).fillna(0.0)

    data = data.assign(Total=data.sum(1))
    data = data.resample('1S').asfreq(fill_value=0.0)

    if average_seconds > 0:
        data = data.rolling(timedelta(seconds=average_seconds)).mean()

    return data

def average_dps_per_character_melt(data: pd.DataFrame) -> pd.DataFrame:
    """Reshape DataFrame to long format"""
    data = data.reset_index().melt(id_vars='timestamp', value_name='damage')

    return data

def resample_30s_mean(data: pd.DataFrame) -> pd.DataFrame:
    """Resample data to 30s average rows"""

    return data.resample('30S').mean()

def filter_by_datetime(data: pd.DataFrame, after: datetime, until: datetime):
    """Return rows which timestamp is within the provided datetimes"""
    return data[(data['timestamp'] > after) & (data['timestamp'] <= until)]
