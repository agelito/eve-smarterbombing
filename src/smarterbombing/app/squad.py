"""Runtime information for a squad (group of characters)"""

from datetime import timedelta, datetime, timezone
import pandas as pd
from smarterbombing.aggregrator.damage_graph_aggregator import DamageGraphAggregator
from smarterbombing.aggregrator.site_statistics_aggregator import SiteStatisticsAggregator
from smarterbombing.configuration import get_log_directory
from smarterbombing.logs.log_locator import get_latest_log_files
from smarterbombing.logs.log_reader import LogReader

def _read_events(reader: LogReader):
    return reader.read_log_events()

def _flatten(in_list):
    return [item for ll in in_list for item in ll]

class Squad:
    """
    Squad - a group of characters

    """

    def __init__(self, name, characters, config):
        self.name = name
        self.characters = characters
        self.config = config

        self.readers = []
        self.aggregators = {}

        self.filter_subjects = config['ignore_list']

    def initialize_aggregators(self):
        """
        Initialize data aggregators for the squad

        """

        dps_average_seconds = self.config['dps_average_seconds']
        realtime_graph_minutes = self.config['live_graph_minutes']
        site_boundary_minimum_seconds = self.config['site_boundary_minimum_seconds']

        outgoing_hostile_damage = DamageGraphAggregator(
            timedelta(minutes=realtime_graph_minutes), dps_average_seconds,
            only_outgoing=True, only_hostile=True)

        outgoing_friendly_damage = DamageGraphAggregator(
            timedelta(minutes=realtime_graph_minutes), dps_average_seconds,
            only_outgoing=True, only_friendly=True)

        incoming_hostile_damage = DamageGraphAggregator(
            timedelta(minutes=realtime_graph_minutes), dps_average_seconds,
            only_incoming=True, only_hostile=True)

        site_statistics = SiteStatisticsAggregator(site_boundary_minimum_seconds)

        self.aggregators['outgoing_hostile_damage'] = outgoing_hostile_damage
        self.aggregators['outgoing_friendly_damage'] = outgoing_friendly_damage
        self.aggregators['incoming_hostile_damage'] = incoming_hostile_damage
        self.aggregators['site_statistics'] = site_statistics

    def initialize_readers(self, follow_logs: bool = True):
        """
        Find and open log files of characters in the squad

        :param follow_logs: should the open logs seek to end

        """

        for reader in self.readers:
            reader.close()
        self.readers = []

        log_directory = get_log_directory(self.config)
        recent_log_files = get_latest_log_files(log_directory)

        for log_file in recent_log_files:
            if log_file['character'] in self.characters:
                reader = LogReader(log_file, self.characters, self.filter_subjects)
                reader.open(follow_logs)

                self.readers.append(reader)

    def read_and_aggregate_data(self):
        """
        Read available data from open logs and aggregate the results

        """

        events = _flatten(map(_read_events, self.readers))

        for _, aggregator in self.aggregators.items():
            aggregator.append_events(events)

        current_time = datetime.now(timezone.utc)
        for _, aggregator in self.aggregators.items():
            aggregator.aggregate(current_time)

    def get_open_files(self):
        """
        Get open files

        :returns: dataframe of open file information

        """

        if len(self.readers) > 0:
            open_files = pd.DataFrame(map(lambda reader: reader.log_file, self.readers))
        else:
            open_files = pd.DataFrame(columns=['filename', 'created_at', 'path', 'character'])

        return open_files

    def get_outgoing_hostile_damage_graph(self):
        """
        Get outgoing hostile damage graph

        :returns: DataFrame of damage to hostiles

        """

        return self.aggregators['outgoing_hostile_damage'].graph_data

    def get_incoming_hostile_damage_graph(self):
        """
        Get incoming hostile damage graph

        :returns: DataFrame of damage from hostiles

        """

        return self.aggregators['incoming_hostile_damage'].graph_data

    def get_compound_site_statistics(self):
        """
        Get compound site statistics

        :returns: DataFrame of compound site statistics

        """

        return self.aggregators['site_statistics'].compound
