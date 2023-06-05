from datetime import timedelta
import matplotlib.pyplot as plt
import pandas as pd

from smarterbombing.analysis import parse_logs
from smarterbombing.configuration import load_configuration

CONFIGURATION_PATH = 'configuration.json'
DATE = '2023-05-30'

def _real_session_data():
    configuration = load_configuration(CONFIGURATION_PATH)

    (data, info) = parse_logs(configuration, DATE)

    return data[0]['outgoing_hostile_damage'][['timestamp', 'character', 'damage']]


def _avg_dps_per_character(data: pd.DataFrame, average_seconds: int = 10) -> pd.DataFrame:
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

def _forged_session_data():
    data = [
        { 'timestamp': '2023-06-06 10:00:00', 'character': 'Ageliten', 'damage': 5 },
        { 'timestamp': '2023-06-06 10:00:00', 'character': 'Ageliten', 'damage': 8 },
        { 'timestamp': '2023-06-06 10:00:00', 'character': 'Yeol Ramyun', 'damage': 2 },
        { 'timestamp': '2023-06-06 10:00:01', 'character': 'Yeol Ramyun', 'damage': 4 },
        { 'timestamp': '2023-06-06 10:00:01', 'character': 'Fresar Ronuken', 'damage': 1 },
        { 'timestamp': '2023-06-06 10:00:03', 'character': 'Mr Vesuvio', 'damage': 5 },
        { 'timestamp': '2023-06-06 10:00:03', 'character': 'Ageliten', 'damage': 8 },
        { 'timestamp': '2023-06-06 10:00:04', 'character': 'Yeol Ramyun', 'damage': 13 },
        { 'timestamp': '2023-06-06 10:00:09', 'character': 'Ageliten', 'damage': 10 },
        { 'timestamp': '2023-06-06 10:00:11', 'character': 'Yeol Ramyun', 'damage': 12 },
        { 'timestamp': '2023-06-06 10:00:11', 'character': 'Mr Vesuvio', 'damage': 15 },
    ]

    return pd.DataFrame(data)

hostile_damage = _real_session_data()
hostile_damage['timestamp'] = pd.to_datetime(hostile_damage['timestamp'])

average_dps = _avg_dps_per_character(hostile_damage, 16)

average_dps.plot(ylabel='Damage', xlabel='Time')
plt.legend(average_dps.columns)

plt.show()
