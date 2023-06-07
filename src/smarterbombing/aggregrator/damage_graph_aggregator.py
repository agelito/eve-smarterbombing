"""Damage graph aggregator"""
from datetime import datetime, timedelta, timezone
import pandas as pd

# TODO(axel): Implement discarding of data which is too old to be used, or come up with a way
# preventing having to recalculate previous values every time. With huge amounts of data this
# function can take hundreds of milliseconds if this isn't implemented.

def _filter_by_datetime(data: pd.DataFrame, start_date: datetime, end_date: datetime):
    return data[(data['timestamp'] >= start_date) & (data['timestamp'] <= end_date)]

def _generate_1s_timeseries_dataframe(start_date: datetime, end_date: datetime) -> pd.DataFrame:
    start_date = start_date.replace(microsecond=0)
    end_date = end_date.replace(microsecond=0)

    timerange = pd.date_range(start_date, end_date, freq='S', unit='s')

    return timerange.to_frame(index=False, name='timestamp')

class DamageGraphAggregator:
    """
    DamageGraphAggregator - aggregates combat log events into average damage over time data
    """

    def __init__(self, graph_time_window: timedelta):
        self.events = []
        self.graph_time_window = graph_time_window

    def append_events(self, combat_log_events: list):
        """
        Append combat log events to aggregator.

        :param combat_log_events: list of combat log events

        """
        self.events.extend(combat_log_events)

    def aggregate(self,
                  average_over_seconds: int,
                  end_at: datetime = datetime.now(timezone.utc)
                  ) -> pd.DataFrame:
        """
        Aggregate the data appended until now.

        :param average_over_seconds: calculate average damage using a rolling window
        :param end_at: until what date and time data should be aggregated

        :returns: DataFrame with the damage per second graph data
        """

        end_at = end_at.replace(tzinfo=None)

        start_at = end_at - (self.graph_time_window + timedelta(seconds = average_over_seconds))
        graph_start_at = end_at - self.graph_time_window

        data = pd.DataFrame(self.events)
        data = data[['timestamp', 'character', 'damage']]
        data = _filter_by_datetime(data, start_at, end_at)

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

        if average_over_seconds > 0:
            data = data.rolling(timedelta(seconds=average_over_seconds)).mean()

        # NOTE(axel): Cut off at graph starting point after averaging, this prevents values
        # drifting as they get close to the start graph time window.
        data = data[data.index >= graph_start_at]

        return data
