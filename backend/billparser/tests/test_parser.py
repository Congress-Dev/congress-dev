from unittest import TestCase
from billparser.actions.parser import strike_emulation


class TestStrikeEmulation(TestCase):
    def test_119_hr_22(self):
        text = "Except as provided in subsection (b), notwithstanding any other Federal or State law, in addition to any other method of voter registration provided for under State law, each State shall establish procedures to register to vote in elections for Federal office-"
        result = strike_emulation("subsection (b)", "subsection (c)", text, False)
        self.assertEqual(
            result,
            "Except as provided in subsection (c), notwithstanding any other Federal or State law, in addition to any other method of voter registration provided for under State law, each State shall establish procedures to register to vote in elections for Federal office-",
        )
