from datetime import datetime
import pytest

from smarterbombing.parsing.combat_log_parser import parse_log_timestamp

@pytest.mark.parametrize(
        'log_date, date',
        [
            ('2023.08.15 15:00:32', datetime(2023, 8, 15, 15, 0, 32)),
            ('2023.01.02 03:00:55', datetime(2023, 1, 2, 3, 0, 55)),
            ('1995.12.10 12:55:00', datetime(1995, 12, 10, 12, 55, 0)),
            ('2024.02.19 00:01:02', datetime(2024, 2, 19, 0, 1, 2))
        ]
)

def test_parse_log_timestamp(log_date, date):
    assert parse_log_timestamp(log_date) == date

def test_parse_log_timestamp_raises_value_error():
    with pytest.raises(ValueError):
        parse_log_timestamp('22-01-15 15:10:25')
