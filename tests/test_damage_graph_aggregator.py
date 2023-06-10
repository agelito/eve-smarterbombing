from datetime import datetime, timedelta, timezone

from smarterbombing.aggregrator.damage_graph_aggregator import DamageGraphAggregator

def test_damage_graph_aggregator_empty_data():
    """test_damage_graph_aggregator_empty_data"""
    sut = DamageGraphAggregator(timedelta(minutes=5), 5, only_hostile=True, only_outgoing=True)

    result = sut.aggregate(datetime.now(timezone.utc))

    assert result.empty is False

def test_damage_graph_aggregator_one_event():
    """test_damage_graph_aggregator_one_event"""
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
        }
    ]
    sut = DamageGraphAggregator(timedelta(minutes=5), 5, only_hostile=True, only_outgoing=True)

    sut.append_events(events)

    result = sut.aggregate(datetime.now(timezone.utc))

    assert result.empty is False

def test_damage_graph_aggregator_one_filtered_event():
    """test_damage_graph_aggregator_one_filtered_event"""
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
        }
    ]
    sut = DamageGraphAggregator(timedelta(minutes=5), 5, only_incoming=True)

    sut.append_events(events)

    result = sut.aggregate(datetime.now(timezone.utc))

    assert result.empty is False

def test_damage_graph_aggregator_keep_recent_events():
    """test_damage_graph_aggregator_keep_recent_events"""
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
        }
    ]
    sut = DamageGraphAggregator(timedelta(minutes=5), 5, only_outgoing=True)

    sut.append_events(events)
    sut.aggregate(datetime(2023, 6, 5, 13, 2, 0))

    assert len(sut.events) == 1
