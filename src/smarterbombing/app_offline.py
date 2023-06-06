"""Offline application"""
import pandas as pd
from gradio import Progress
from smarterbombing.analysis import parse_logs, average_dps_per_character, resample_30s_mean

class AppOffline:
    """Class holding state for offline processing"""
    def __init__(self, configuration) -> None:
        self.configuration = configuration
        self.session_index = 0
        self.data = None
        self.info = None

    def load_at_date(self, date, progress=Progress()):
        """Load logs at date"""
        (data, info) = parse_logs(self.configuration, date, progress)

        self.info = info
        self.data = data

        return info

    def select_session(self, session_index):
        """Select session with index"""
        self.session_index = session_index

    def selected_session(self) -> str:
        """Returns a list of session choices"""
        if not self.loaded():
            return None
        return self.info['Start'].iloc[0]

    def damage_over_time_hostile(self) -> pd.DataFrame:
        """Returns a dataframe with DPS"""
        if not self.loaded():
            return pd.DataFrame([])

        session = self.data[self.session_index]
        data = session['outgoing_hostile_damage']

        if (data.empty):
            return pd.DataFrame([])

        average_dps = average_dps_per_character(data)
        average_dps = resample_30s_mean(average_dps)

        return average_dps

    def damage_over_time_friendly(self) -> pd.DataFrame:
        """Returns a dataframe with DPS"""
        if not self.loaded():
            return pd.DataFrame([])

        session = self.data[self.session_index]
        data = session['outgoing_friendly_damage']

        if (data.empty):
            return pd.DataFrame([])

        average_dps = average_dps_per_character(data)
        average_dps = resample_30s_mean(average_dps)

        return average_dps

    def damage_over_time_incoming_hostile(self) -> pd.DataFrame:
        """Returns a dataframe with DPS"""
        if not self.loaded():
            return pd.DataFrame([])

        session = self.data[self.session_index]
        data = session['incoming_hostile_damage']

        if (data.empty):
            return pd.DataFrame([])

        average_dps = average_dps_per_character(data)
        average_dps = resample_30s_mean(average_dps)

        return average_dps

    def damage_over_time_incoming_friendly(self) -> pd.DataFrame:
        """Returns a dataframe with DPS"""
        if not self.loaded():
            return pd.DataFrame([])

        session = self.data[self.session_index]
        data = session['incoming_friendly_damage']

        if (data.empty):
            return pd.DataFrame([])

        average_dps = average_dps_per_character(data)
        average_dps = resample_30s_mean(average_dps)

        return average_dps

    def loaded(self) -> bool:
        """Return boolean indicating if data is loaded"""
        return self.info is not None and self.data is not None
