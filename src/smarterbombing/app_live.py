"""Live application"""
from datetime import timedelta, datetime, timezone
import pandas as pd
from smarterbombing.analysis import\
    EVENT_GROUP_INCOMING_FRIENDLY_DAMAGE,\
    EVENT_GROUP_INCOMING_HOSTILE_DAMAGE,\
    EVENT_GROUP_OUTGOING_FRIENDLY_DAMAGE,\
    EVENT_GROUP_OUTGOING_HOSTILE_DAMAGE,\
    create_empty_damage_dataframe,\
    filter_by_datetime,\
    fixed_window_average_dps_per_character,\
    group_damage_events

from smarterbombing.logs import find_most_recent_character_logs
from smarterbombing.log_reader import\
    CharacterLogFile,\
    log_entries_to_dataframe,\
    open_log_files,\
    read_all_combat_log_entries

class AppLive:
    """Live application"""
    def __init__(self, configuration):
        self.configuration = configuration
        self.current_time = datetime.now(timezone.utc)

        self.logs: list[CharacterLogFile] = []

        self.data = pd.DataFrame([])
        self.outgoing_hostile_damage = create_empty_damage_dataframe()
        self.outgoing_friendly_damage = create_empty_damage_dataframe()
        self.incoming_hostile_damage = create_empty_damage_dataframe()
        self.incoming_friendly_damage = create_empty_damage_dataframe()

        self.damage_data_template = pd.DataFrame(columns=configuration['characters'])\
            .rename_axis('character', axis='columns')

        self.data_rows = 0
        self.most_recent_timestamp = None
        self.damage_graph_time_window = timedelta(minutes=5)

    def open_logs(self):
        """Open log files"""
        most_recent_logs = find_most_recent_character_logs(self.configuration['log_directory'])

        for log in self.logs:
            log.close()

        self.logs = open_log_files(most_recent_logs, self.configuration['characters'], True)

    def close_logs(self):
        """Close all log files"""
        for log in self.logs:
            log.close()

        self.logs = []

    def clear_data(self):
        """Clear all data"""
        self.data = pd.DataFrame([])

        self.outgoing_hostile_damage = create_empty_damage_dataframe()
        self.outgoing_friendly_damage = create_empty_damage_dataframe()
        self.incoming_hostile_damage = create_empty_damage_dataframe()
        self.incoming_friendly_damage = create_empty_damage_dataframe()

    def is_logs_open(self) -> bool:
        """Return boolean indicating if any log files is open"""
        return any(map(lambda log: log.is_open(), self.logs))

    def parse_new_log_messages(self):
        """Parse all new log messages"""
        parsed_logs = read_all_combat_log_entries(self.logs)

        if len(parsed_logs) > 0:
            parsed_logs = log_entries_to_dataframe(parsed_logs)
            self.data = pd.concat([self.data, parsed_logs])

    def recalculate_damage_graphs(self, graph_from: datetime, graph_until: datetime):
        """Recalculate average dps data"""
        damage_graph_data = filter_by_datetime(self.data, graph_from, graph_until)
        grouped_events = group_damage_events(damage_graph_data, self.configuration['characters'])
        average_seconds = self.configuration['dps_rolling_window_seconds']

        self.outgoing_hostile_damage = fixed_window_average_dps_per_character(
            grouped_events[EVENT_GROUP_OUTGOING_HOSTILE_DAMAGE],
            self.damage_data_template, graph_from, graph_until, average_seconds)
        self.outgoing_friendly_damage = fixed_window_average_dps_per_character(
            grouped_events[EVENT_GROUP_OUTGOING_FRIENDLY_DAMAGE],
            self.damage_data_template, graph_from, graph_until, average_seconds)
        self.incoming_hostile_damage = fixed_window_average_dps_per_character(
            grouped_events[EVENT_GROUP_INCOMING_HOSTILE_DAMAGE],
            self.damage_data_template, graph_from, graph_until, average_seconds)
        self.incoming_friendly_damage = fixed_window_average_dps_per_character(
            grouped_events[EVENT_GROUP_INCOMING_FRIENDLY_DAMAGE],
            self.damage_data_template, graph_from, graph_until, average_seconds)

    def update(self):
        """Read logs and recalculate derived data"""
        self.current_time = datetime.now(timezone.utc).replace(tzinfo=None)

        self.parse_new_log_messages()

        self.data_rows = len(self.data.index)

        if self.data_rows > 0:
            self.most_recent_timestamp = self.data['timestamp'].max()

            damage_graph_from = self.current_time - self.damage_graph_time_window
            damage_graph_until = self.current_time
            self.recalculate_damage_graphs(damage_graph_from, damage_graph_until)
