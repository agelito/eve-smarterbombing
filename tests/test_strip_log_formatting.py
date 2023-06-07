import pytest

from smarterbombing.parsing.combat_log_parser import strip_log_formatting

@pytest.mark.parametrize(
        'log_line, clean_log_line',
        [
            ('[ 2023.06.03 05:36:39 ] (combat) <color=0xff00ffff><b>26</b> <color=0x77ffffff><font size=10>to</font> <b><color=0xffffffff>Fresar Ronuken[GUNS-](Machariel)</b><font size=10><color=0x77ffffff> - Imperial Navy Large EMP Smartbomb - Hits',
             '[ 2023.06.03 05:36:39 ] (combat) 26 to Fresar Ronuken[GUNS-](Machariel) - Imperial Navy Large EMP Smartbomb - Hits'),
            ('[ 2023.06.03 05:36:39 ] (combat) <color=0xff00ffff><b>375</b> <color=0x77ffffff><font size=10>to</font> <b><color=0xffffffff>Centus Dread Lord</b><font size=10><color=0x77ffffff> - Imperial Navy Large EMP Smartbomb - Hits',
             '[ 2023.06.03 05:36:39 ] (combat) 375 to Centus Dread Lord - Imperial Navy Large EMP Smartbomb - Hits'),
            ('[ 2023.06.03 05:36:38 ] (combat) <color=0xffcc0000><b>65</b> <color=0x77ffffff><font size=10>from</font> <b><color=0xffffffff>Centus Tyrant</b><font size=10><color=0x77ffffff> - Hits',
             '[ 2023.06.03 05:36:38 ] (combat) 65 from Centus Tyrant - Hits'),
        ]
)

def test_strip_log_formatting(log_line, clean_log_line):
    assert strip_log_formatting(log_line) == clean_log_line
