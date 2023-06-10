"""Damage graph aggregator"""
from datetime import datetime, timedelta
import pandas as pd

from smarterbombing.aggregrator.aggregator import Aggregator

def _average_dps_per_character_melt(data: pd.DataFrame) -> pd.DataFrame:
    return data.reset_index().melt(id_vars='timestamp', value_name='damage')

def _filter_by_datetime(data: pd.DataFrame, start_date: datetime, end_date: datetime):
    return data[(data['timestamp'] >= start_date) & (data['timestamp'] <= end_date)]

def _generate_1s_timeseries_dataframe(start_date: datetime, end_date: datetime) -> pd.DataFrame:
    start_date = start_date.replace(microsecond=0)
    end_date = end_date.replace(microsecond=0)

    timerange = pd.date_range(start_date, end_date, freq='S', unit='s')

    return timerange.to_frame(index=False, name='timestamp')

class DamageGraphAggregator(Aggregator):
    """
    DamageGraphAggregator - aggregates combat log events into average damage over time data
    """

    def __init__(self,
                 graph_time_window: timedelta,
                 average_over_seconds: int,
                 only_incoming: bool = False,
                 only_outgoing: bool = False,
                 only_friendly: bool = False,
                 only_hostile: bool = False,
                ):
        Aggregator.__init__(self)

        self.graph_time_window = graph_time_window
        self.graph_data = pd.DataFrame(columns=['timestamp', 'character', 'damage'])

        self.average_over_seconds = average_over_seconds

        self.only_incoming = only_incoming
        self.only_outgoing = only_outgoing
        self.only_friendly = only_friendly
        self.only_hostile = only_hostile

    def aggregate(self, end_at: datetime) -> pd.DataFrame:
        """
        Aggregate the data appended until now.

        :param end_at: until what date and time data should be aggregated

        :returns: DataFrame with the damage per second graph data

        """

        end_at = end_at.replace(tzinfo=None)

        start_at = end_at - (
            self.graph_time_window + timedelta(seconds = self.average_over_seconds)
        )
        graph_start_at = end_at - self.graph_time_window

        if len(self.events) > 0:
            data = pd.DataFrame(self.events)
        else:
            data = pd.DataFrame(
                columns=['timestamp', 'character', 'friendly_fire', 'direction', 'damage']
            )

        data = _filter_by_datetime(data, start_at, end_at)

        if len(data.index) > 0:
            if self.only_incoming:
                data = data[data['direction'] == 'from']

            if self.only_outgoing:
                data = data[data['direction'] == 'to']

            if self.only_friendly:
                data = data[data['friendly_fire']]

            if self.only_hostile:
                data = data[~data['friendly_fire']]

        # Remove old events
        self.events = data.to_dict('records')

        data = data[['timestamp', 'character', 'damage']]

        characters = data['character'].unique()

        fixed_window = pd.concat([
            _generate_1s_timeseries_dataframe(start_at, end_at), pd.DataFrame(columns=characters),
        ]).fillna(0.0).set_index('timestamp').rename_axis('character', axis='columns')

        data = data.groupby(['timestamp', 'character']).sum().reset_index()
        data = data.pivot(
            index='timestamp',
            columns='character',
            values='damage'
        ).fillna(0.0)

        data = data.combine_first(fixed_window)
        data = data.assign(Total=data.sum(1))
        data = data.resample('1S').asfreq(fill_value=0.0)

        if self.average_over_seconds > 0:
            data = data.rolling(timedelta(seconds=self.average_over_seconds)).mean()

        # NOTE(axel): Cut off at graph starting point after averaging, this prevents values
        # drifting as they get close to the start graph time window.
        data = data[data.index >= graph_start_at]

        self.graph_data = _average_dps_per_character_melt(data)

        return data
