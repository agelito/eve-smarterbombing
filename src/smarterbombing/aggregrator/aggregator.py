"""Interface for collecting and aggregating data"""
from datetime import datetime
import pandas as pd

class Aggregator(object):
    """
    Aggregator: interface for collecting and aggregating data

    """

    def __init__(self):
        self.events = []

    def append_events(self, events: list):
        """
        Append events to aggregator.

        :param events: list of events

        """
        self.events.extend(events)

    def aggregate(self, end_at: datetime) -> pd.DataFrame:
        """
        Aggregate the data appended until now.

        :param end_at: until what date and time data should be aggregated

        :returns: DataFrame with the damage per second graph data

        """
