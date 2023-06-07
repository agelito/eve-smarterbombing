from datetime import datetime
import pytest

from smarterbombing.parsing.combat_log_parser import parse_combat_log_line

@pytest.mark.parametrize(
        'log_line, combat_log_data',
        [
            ('[ 2023.06.03 05:36:39 ] (combat) <color=0xff00ffff><b>26</b> <color=0x77ffffff><font size=10>to</font> <b><color=0xffffffff>Fresar Ronuken[GUNS-](Machariel)</b><font size=10><color=0x77ffffff> - Imperial Navy Large EMP Smartbomb - Hits',
             { 'timestamp': datetime(2023, 6, 3, 5, 36, 39), 'message_type': 'combat', 'damage': 26, 'direction': 'to', 'subject': 'Fresar Ronuken[GUNS-](Machariel)', 'what': 'Imperial Navy Large EMP Smartbomb', 'quality': 'Hits'}),
            ('[ 2023.06.03 05:36:39 ] (combat) <color=0xff00ffff><b>375</b> <color=0x77ffffff><font size=10>to</font> <b><color=0xffffffff>Centus Dread Lord</b><font size=10><color=0x77ffffff> - Imperial Navy Large EMP Smartbomb - Hits',
             { 'timestamp': datetime(2023, 6, 3, 5, 36, 39), 'message_type': 'combat', 'damage': 375, 'direction': 'to', 'subject': 'Centus Dread Lord', 'what': 'Imperial Navy Large EMP Smartbomb', 'quality': 'Hits'}),
            ('[ 2023.06.03 05:36:38 ] (combat) <color=0xffcc0000><b>65</b> <color=0x77ffffff><font size=10>from</font> <b><color=0xffffffff>Centus Tyrant</b><font size=10><color=0x77ffffff> - Hits',
             { 'timestamp': datetime(2023, 6, 3, 5, 36, 38), 'message_type': 'combat', 'damage': 65, 'direction': 'from', 'subject': 'Centus Tyrant', 'what': '', 'quality': 'Hits'}),
            ('[ 2023.06.03 05:36:26 ] (bounty) <font size=12><b><color=0xff00aa00>5 343 ISK</b><color=0x77ffffff> added to next bounty payout (payment adjusted)', None),
            ('NOTE: Attacking members of your fleet is not a CONCORD sanctioned activity and may result in security status loss and police response.', None),
            ('[ 2023.04.10 11:11:51 ] (combat) <color=0xffffffff><b>Warp scramble attempt</b> <color=0x77ffffff><font size=10>from</font> <color=0xffffffff><b><font size=12><color=0xFFFFB900> <u><b>Hecate</b></u></color></font><font size=12><color=0xFFFEFF6F> [<b>CONDI</b>]</color></font> [<b>PVEV3</b>]  [Mr Ranger]<color=0xFFFFFFFF><b> -</b> <color=0x77ffffff><font size=10>to <b><color=0xffffffff></font><font size=12><color=0xFFFFB900> <u><b>Damnation</b></u></color></font><font size=12><color=0xFFFEFF6F> [<b>2GTHR</b>]</color></font> [<b>BLUEP</b>]  [Corpranis]<color=0xFFFFFFFF><b> -', None),
            ('[ 2023.04.01 11:46:39 ] (combat) <color=0xffccff66><b>487</b><color=0x77ffffff><font size=10> remote shield boosted by </font><b><color=0xffffffff><font size=12><color=0xFFFFB900> <u><b>Osprey</b></u></color></font><font size=12><color=0xFFFEFF6F> [<b>CONDI</b>]</color></font> [<b>BALA</b>]  [Logarm]<color=0xFFFFFFFF><b> -</b><color=0x77ffffff><font size=10> - Medium Murky Compact Remote Shield Booster</font>', None),
        ]
)

def test_parse_combat_log_line(log_line, combat_log_data):
    assert parse_combat_log_line(log_line) == combat_log_data
