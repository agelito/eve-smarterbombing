import pandas as pd

from smarterbombing.analysis import compound_site_statistics, parse_logs, site_statistics
from smarterbombing.configuration import load_configuration

characters = ['Ageliten', 'Fresar Ronuken', 'Yeol Ramyun', 'Mr Vesuvio']
template = pd.DataFrame(columns=characters)

CONFIGURATION_PATH = 'configuration.json'
DATE = '2023-05-30'

def _real_session_data():
    configuration = load_configuration(CONFIGURATION_PATH)

    (data, info) = parse_logs(configuration, DATE)

    return data[0]['outgoing_damage']

df = pd.DataFrame([
    { 'timestamp': '2023-06-06 00:42:38', 'direction': 'to', 'character': 'Ageliten', 'damage': 10, 'subject': 'Sansha Rat 1', 'what': 'Smartbomb'  },
    { 'timestamp': '2023-06-06 00:42:41', 'direction': 'to', 'character': 'Yeol Ramyun', 'damage': 4, 'subject': 'Ageliten', 'what': 'Smartbomb'  },
    { 'timestamp': '2023-06-06 00:42:42', 'direction': 'to', 'character': 'Ageliten', 'damage': 6, 'subject': 'Sansha Rat 1', 'what': 'Smartbomb'  },
    { 'timestamp': '2023-06-06 00:42:43', 'direction': 'to', 'character': 'Fresar Ronuken', 'damage': 2, 'subject': 'Sansha Rat 2', 'what': 'Smartbomb'  },
    { 'timestamp': '2023-06-06 00:47:31', 'direction': 'to', 'character': 'Ageliten', 'damage': 13, 'subject': 'Sansha Rat 2', 'what': 'Smartbomb'  },
    { 'timestamp': '2023-06-06 00:47:32', 'direction': 'to', 'character': 'Mr Vesuvio', 'damage': 1, 'subject': 'Sansha Rat 1', 'what': 'Smartbomb'  },
    { 'timestamp': '2023-06-06 00:49:15', 'direction': 'to', 'character': 'Yeol Ramyun', 'damage': 4, 'subject': 'Ageliten', 'what': 'Smartbomb' },
    { 'timestamp': '2023-06-06 00:47:31', 'direction': 'to', 'character': 'Fresar Ronuken', 'damage': 5, 'subject': 'Sansha Rat 1', 'what': 'Smartbomb'  },
    { 'timestamp': '2023-06-06 00:49:30', 'direction': 'to', 'character': 'Ageliten', 'damage': 6, 'subject': 'Sansha Rat 2', 'what': 'Smartbomb'  },
    { 'timestamp': '2023-06-06 00:50:01', 'direction': 'to', 'character': 'Fresar Ronuken', 'damage': 2, 'subject': 'Sansha Rat 2', 'what': 'Smartbomb'  },
    { 'timestamp': '2023-06-06 00:50:11', 'direction': 'to', 'character': 'Fresar Ronuken', 'damage': 12, 'subject': 'Sansha Rat 3', 'what': 'Smartbomb'  },
])
df['timestamp'] = pd.to_datetime(df['timestamp'])

df = _real_session_data()

stats = site_statistics(df, characters)
stats.to_markdown('stats.md')

compound_stats = compound_site_statistics(stats)
compound_stats.transpose().to_markdown('compound.md')

print(stats)
print(compound_stats)
