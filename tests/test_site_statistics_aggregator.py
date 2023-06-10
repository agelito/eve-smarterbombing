from datetime import datetime, timezone, timedelta
import pandas as pd
from smarterbombing.aggregrator.site_statistics_aggregator import SiteStatisticsAggregator

def test_site_statistics_aggregator_empty_data():
    """test_site_statistics_aggregator_empty_data"""
    sut = SiteStatisticsAggregator(30)

    result = sut.aggregate(datetime.now(timezone.utc))

    assert result.empty

def test_site_statistics_two_sites():
    """test_site_statistics_two_sites"""
    sut = SiteStatisticsAggregator(30)

    events = [
        {
            'character': 'Character Name',
            'timestamp': datetime(2023, 6, 5, 13, 0, 0),
            'message_type': 'combat',
            'damage': 10,
            'direction': 'to',
            'subject': 'Somewhere',
            'what': 'Rocket',
            'quality': 'Hits',
            'friendly_fire': False,
        },
        {
            'character': 'Character Name',
            'timestamp': datetime(2023, 6, 5, 13, 0, 31),
            'message_type': 'combat',
            'damage': 10,
            'direction': 'to',
            'subject': 'Somewhere',
            'what': 'Rocket',
            'quality': 'Hits',
            'friendly_fire': False,
        }
    ]

    sut.append_events(events)
    result = sut.aggregate(datetime.now(timezone.utc))

    assert len(result.index) == 2
    assert len(sut.history.index) == 1

    assert sut.current.iloc[0]['effective_start_time'] == events[1]['timestamp']

def test_site_statistics_multiple_aggregate():
    """test_site_statistics_multiple_aggregate"""
    sut = SiteStatisticsAggregator(30)

    events = [
        {
            'character': 'Character Name',
            'timestamp': datetime(2023, 6, 5, 13, 0, 0),
            'message_type': 'combat',
            'damage': 10,
            'direction': 'to',
            'subject': 'Somewhere',
            'what': 'Rocket',
            'quality': 'Hits',
            'friendly_fire': False,
        },
        {
            'character': 'Character Name',
            'timestamp': datetime(2023, 6, 5, 13, 0, 31),
            'message_type': 'combat',
            'damage': 10,
            'direction': 'to',
            'subject': 'Somewhere',
            'what': 'Rocket',
            'quality': 'Hits',
            'friendly_fire': False,
        }
    ]

    sut.append_events(events)

    current_time = datetime.now(timezone.utc)
    sut.aggregate(current_time)
    sites1 = pd.concat([sut.history, sut.current])

    sut.aggregate(current_time)
    sites2 = pd.concat([sut.history, sut.current])

    assert len(sites1.index) == len(sites2.index)

def test_site_statistics_downtime_staggered_events():
    """test_site_statistics_downtime_staggered_events"""
    sut = SiteStatisticsAggregator(10)

    events = [
        {
            'character': 'Character Name',
            'timestamp': datetime(2023, 6, 5, 13, 0, 0),
            'message_type': 'combat',
            'damage': 10,
            'direction': 'to',
            'subject': 'Somewhere',
            'what': 'Rocket',
            'quality': 'Hits',
            'friendly_fire': False,
        },
        {
            'character': 'Character Name',
            'timestamp': datetime(2023, 6, 5, 13, 0, 3),
            'message_type': 'combat',
            'damage': 10,
            'direction': 'to',
            'subject': 'Somewhere',
            'what': 'Rocket',
            'quality': 'Hits',
            'friendly_fire': False,
        },
        {
            'character': 'Character Name',
            'timestamp': datetime(2023, 6, 5, 13, 0, 15),
            'message_type': 'combat',
            'damage': 10,
            'direction': 'to',
            'subject': 'Somewhere',
            'what': 'Rocket',
            'quality': 'Hits',
            'friendly_fire': False,
        },
        {
            'character': 'Character Name',
            'timestamp': datetime(2023, 6, 5, 13, 0, 16),
            'message_type': 'combat',
            'damage': 10,
            'direction': 'to',
            'subject': 'Somewhere',
            'what': 'Rocket',
            'quality': 'Hits',
            'friendly_fire': False,
        },
        {
            'character': 'Character Name',
            'timestamp': datetime(2023, 6, 5, 13, 0, 50),
            'message_type': 'combat',
            'damage': 10,
            'direction': 'to',
            'subject': 'Somewhere',
            'what': 'Rocket',
            'quality': 'Hits',
            'friendly_fire': False,
        },
        {
            'character': 'Character Name',
            'timestamp': datetime(2023, 6, 5, 13, 0, 55),
            'message_type': 'combat',
            'damage': 10,
            'direction': 'to',
            'subject': 'Somewhere',
            'what': 'Rocket',
            'quality': 'Hits',
            'friendly_fire': False,
        }
    ]

    sut.append_events(events[:2])
    sut.aggregate(datetime(2023, 6, 5, 13, 1, 0))
    sut.append_events(events[3:5])
    sut.aggregate(datetime(2023, 6, 5, 13, 1, 0))
    sut.aggregate(datetime(2023, 6, 5, 13, 1, 0))

    print(sut.history)
    print(sut.current)
    assert sut.compound['total_downtime'] == timedelta(seconds=47)
