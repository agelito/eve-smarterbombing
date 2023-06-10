"""Site statistics aggregator"""
from datetime import datetime, timedelta
import pandas as pd

from smarterbombing.aggregrator.aggregator import Aggregator

_INPUT_COLUMNS = [
    'timestamp',
    'message_type',
    'damage',
    'direction',
    'subject',
    'what',
    'quality',
    'character',
    'friendly_fire',
]

def _safe_division(numerator, denominator):
    return numerator / denominator if denominator else 0.0

class SiteStatisticsAggregator(Aggregator):
    """
    SiteStatisticsAggregator: aggregates combat log events into statistics about sites

    """

    def __init__(self, minimum_gap_seconds: int):
        Aggregator.__init__(self)

        self.minimum_gap_seconds = minimum_gap_seconds

        self.previous_downtime = timedelta(0)

        # Sites done previously
        self.history = pd.DataFrame([])

        # Site in progress (according to minimum gap)
        self.current = pd.DataFrame([])

        # Combined site averages and totals
        self.compound = {
            'total_time': timedelta(0),
            'total_downtime': timedelta(0),
            'total_effective_time': timedelta(0),
            'sites_per_hour': 0,
            'average_downtime': timedelta(0),
            'average_time': timedelta(0),
            'average_effective_time': timedelta(0),
            'average_damage': 0.0,
            'total_damage': 0,
            'damage_per_second': 0.0,
            'time_efficiency': 0.0,
        }

    def _compound_site_statistics(self, data: pd.DataFrame):
        total_time = data.iloc[-1]['end_time'] - data.iloc[0]['start_time']

        total_seconds = total_time.total_seconds()
        total_hours = total_seconds / 3600

        total_downtime = data['downtime'].sum()

        average_downtime = data['downtime'].mean()
        average_site_time = data['duration'].mean()

        average_effective_time = data['effective_duration'].mean()
        effective_time = data['effective_duration'].sum()

        effective_seconds = effective_time.total_seconds()
        time_efficiency = _safe_division(effective_seconds, total_seconds)

        total_site_damage = data['damage'].sum()
        average_site_damage = data['damage'].mean()

        return {
            'total_time': total_time,
            'total_downtime': total_downtime,
            'total_effective_time': effective_time,
            'sites_per_hour': _safe_division(len(data.index),total_hours),
            'average_downtime': average_downtime,
            'average_time': average_site_time,
            'average_effective_time': average_effective_time,
            'average_damage': average_site_damage,
            'total_damage': total_site_damage,
            'damage_per_second': _safe_division(total_site_damage, effective_seconds),
            'time_efficiency': time_efficiency
        }

    def aggregate(self, end_at: datetime) -> pd.DataFrame:
        """
        Aggregate the data appended until now.

        :param prune_old_events: remove old events no longer needed for aggregation
        :param end_at: until what date and time data should be aggregated

        :returns: DataFrame with the site statistics data
        """

        end_at = end_at.replace(tzinfo=None)

        if len(self.events) == 0:
            return pd.concat([self.history, self.current])

        data = pd.DataFrame(self.events)
        data = data[data['direction'] == 'to']
        data = data[data['timestamp'] <= end_at]

        data = data.sort_values(by='timestamp')
        data = data.reset_index()

        # Calculate event deltas
        data['delta_time'] = data['timestamp'].diff()

        # Assign site index based on time
        data['new_site'] = data['delta_time'] > timedelta(seconds=self.minimum_gap_seconds)
        data['site_index'] = data['new_site'].cumsum()

        # Remove old events
        self.events = data[
            data['site_index'] == data['site_index'].max()
        ][_INPUT_COLUMNS].to_dict('records')

        data_no_friendly = data[~data['friendly_fire']]

        site_downtime = data[data['new_site']][['site_index', 'delta_time']]\
            .set_index('site_index')\
            .rename(columns={'delta_time': 'downtime'})

        if not site_downtime.empty:
            self.previous_downtime = site_downtime.iloc[-1]['downtime']

        if site_downtime.empty and not self.history.empty:
            site_downtime = pd.DataFrame([{
                'downtime': self.previous_downtime
            }])

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

        self.history = pd.concat([self.history, result.iloc[:-1]], ignore_index=True)
        self.current = result.iloc[-1:]

        if len(self.history.index) > 0:
            self.compound = self._compound_site_statistics(pd.concat([self.history, self.current]))

        return result
