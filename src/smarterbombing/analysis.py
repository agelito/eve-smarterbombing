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

def _filter_unfriendly_damage(events: pd.DataFrame, characters):
    filter_friendly = events['subject'].isin(characters)
    return events[~filter_friendly]

def _filter_friendly_damage(events: pd.DataFrame, characters):
    filter_friendly = events['subject'].isin(characters)
    return events[filter_friendly]

def _group_by_delta_time(events: pd.DataFrame, max_gap_seconds: float):
    events['delta'] = events['timestamp'].diff() > timedelta(seconds=max_gap_seconds)

    groups = []
    for _, group in events.groupby([events['delta'].cumsum()]):
        groups.append(group)

    return groups

def group_damage_events(events: pd.DataFrame, characters):
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

def reshape_for_per_character_dps(data: pd.DataFrame) -> pd.DataFrame:
    """Reshape dataframe to represent damage per character"""
    data = data[['timestamp', 'character', 'damage']]
    data = data.groupby(['timestamp', 'character']).sum().reset_index()
    data = data.pivot(
        index='timestamp',
        columns='character',
        values='damage'
    ).fillna(0.0)

    return data

def fixed_window_average_dps_per_character(
        data: pd.DataFrame,
        template: pd.DataFrame,
        start_at: datetime,
        end_at: datetime,
        average_seconds: int = 10) -> pd.DataFrame:
    """Create a fixed time window and populate with average DPS"""

    fixed_window = pd.concat([
        generate_1s_dataframe(start_at, end_at),
        template,
    ]).fillna(0.0)\
        .set_index('timestamp')\
        .rename_axis('character', axis='columns')

    data = reshape_for_per_character_dps(data)
    data = data.combine_first(fixed_window)

    data = data.assign(Total=data.sum(1))
    data = data.resample('1S').asfreq(fill_value=0.0)

    if average_seconds > 0:
        data = data.rolling(timedelta(seconds=average_seconds)).mean()

    return data

def site_statistics(data: pd.DataFrame, characters, minimum_gap_seconds: int = 30) -> pd.DataFrame:
    """Calculate site based time statistics"""
    data = _filter_by_direction(data, 'to')
    data = data.sort_values(by='timestamp')
    data = data.reset_index()

    # Calculate event deltas
    data['delta_time'] = data['timestamp'].diff()

    # Assign site index based on time
    data['new_site'] = data['delta_time'] > timedelta(seconds=minimum_gap_seconds)
    data['site_index'] = data['new_site'].cumsum()

    if not data['new_site'].any():
        return create_empty_site_statistics_dataframe()

    mask_friendly = data['subject'].apply(lambda c: c in characters)
    data['hit_friendly'] = mask_friendly

    data_no_friendly = data[~data['hit_friendly']]

    filter_new_sites = data['new_site']
    site_downtime = data[filter_new_sites][['site_index', 'delta_time']]\
        .set_index('site_index')\
        .rename(columns={'delta_time': 'downtime'})

    site_groups = data.groupby('site_index')
    start_times = site_groups['timestamp'].first()
    end_times = site_groups['timestamp'].last()

    site_groups = data_no_friendly.groupby('site_index')
    effective_start_times = site_groups['timestamp'].first()
    effective_end_times = site_groups['timestamp'].last()

    site_damage = data_no_friendly.pivot(columns='site_index', values='damage').sum()
    site_hits = data_no_friendly.pivot(columns='site_index', values='subject').count()

    durations = end_times - start_times
    effective_durations = effective_end_times - effective_start_times

    result = pd.DataFrame({
        'effective_start_time': effective_start_times,
        'effective_end_time': effective_end_times,
        'start_time': start_times,
        'end_time': end_times,
        'duration': durations,
        'effective_duration': effective_durations,
        'damage': site_damage,
        'hits': site_hits,
    })

    result = result.combine_first(site_downtime).fillna(timedelta(0))

    return result

def compound_site_statistics(data: pd.DataFrame):
    """Calculate compound site statistics"""
    total_time = data.iloc[-1]['end_time'] - data.iloc[0]['start_time']

    total_seconds = total_time.total_seconds()
    total_hours = total_seconds / 3600

    total_downtime = data['downtime'].sum()

    average_downtime = data['downtime'].mean()
    average_site_time = data['duration'].mean()

    average_effective_time = data['effective_duration'].mean()
    effective_time = data['effective_duration'].sum()

    effective_seconds = effective_time.total_seconds()
    time_efficiency = effective_seconds / total_seconds

    sites_per_hour = len(data.index) / total_hours

    total_site_damage = data['damage'].sum()
    average_site_damage = data['damage'].mean()

    average_damage_per_second = total_site_damage / effective_seconds

    return pd.DataFrame([{
        'total_time': total_time,
        'total_downtime': total_downtime,
        'total_effective_time': effective_time,
        'sites_per_hour': sites_per_hour,
        'average_downtime': average_downtime,
        'average_time': average_site_time,
        'average_effective_time': average_effective_time,
        'average_damage': average_site_damage,
        'total_damage': total_site_damage,
        'damage_per_second': average_damage_per_second,
        'time_efficiency': time_efficiency
    }])

def average_dps_per_character(data: pd.DataFrame, average_seconds: int = 10) -> pd.DataFrame:
    """Calculate average DPS per character"""

    if data.empty:
        return data

    data = reshape_for_per_character_dps(data)

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

def generate_1s_dataframe(start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """Generate index of datetime range with 1 second frequency"""
    start_date = start_date.replace(microsecond=0)
    end_date = end_date.replace(microsecond=0)

    timerange = pd.date_range(start_date, end_date, freq='S', unit='s')

    return timerange.to_frame(index=False, name='timestamp')

def filter_by_datetime(data: pd.DataFrame, start_date: datetime, end_date: datetime):
    """Return rows which timestamp is within the provided datetimes"""
    return data[(data['timestamp'] >= start_date) & (data['timestamp'] <= end_date)]

def create_empty_damage_dataframe():
    """Create an empty damage DataFrame"""
    return pd.DataFrame(columns=['timestamp', 'character', 'damage'])

def create_empty_site_statistics_dataframe():
    """Create an empty site statistics DataFrame"""
    return pd.DataFrame(columns=[
        'effective_start_time',
        'effective_end_time',
        'start_time',
        'end_time',
        'duration',
        'effective_duration',
        'damage',
        'hits',
    ])

def create_empty_compound_site_statistics_dataframe():
    """Create an empty compound site statistics DataFrame"""
    return pd.DataFrame(columns=[
        'total_time',
        'total_downtime',
        'total_effective_time',
        'sites_per_hour',
        'average_downtime',
        'average_time',
        'average_effective_time',
        'average_damage',
        'total_damage',
        'damage_per_second',
        'time_efficiency',
    ])
