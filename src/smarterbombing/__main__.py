from datetime import datetime, timedelta
import pandas as pd

from smarterbombing.analysis import average_dps_per_character_melt, fixed_window_average_dps_per_character

characters = ['Ageliten', 'Fresar Ronuken', 'Yeol Ramyun', 'Mr Vesuvio']
template = pd.DataFrame(columns=characters)

data = pd.DataFrame([
    {'timestamp': '2023-06-06 00:42:38', 'character': 'Ageliten', 'damage': 10 },
    { 'timestamp': '2023-06-06 00:47:31', 'character': 'Fresar Ronuken', 'damage': 5 },
    { 'timestamp': '2023-06-06 00:47:31', 'character': 'Ageliten', 'damage': 13 },
    { 'timestamp': '2023-06-06 00:42:43', 'character': 'Fresar Ronuken', 'damage': 2 },
    { 'timestamp': '2023-06-06 00:42:41', 'character': 'Yeol Ramyun', 'damage': 4 },
    { 'timestamp': '2023-06-06 00:47:32', 'character': 'Mr Vesuvio', 'damage': 1 },
    { 'timestamp': '2023-06-06 00:42:42', 'character': 'Ageliten', 'damage': 6 },
])
data['timestamp'] = pd.to_datetime(data['timestamp'])

empty_data = pd.DataFrame(columns=['timestamp', 'character', 'damage'])

start_at = datetime.strptime('2023-06-06 00:42:38', '%Y-%m-%d %H:%M:%S')
end_at = start_at + timedelta(minutes=5)

average_dps = fixed_window_average_dps_per_character(empty_data, template, start_at, end_at)
average_dps = average_dps_per_character_melt(average_dps)
average_dps.to_csv('combined.csv')

print(average_dps)
