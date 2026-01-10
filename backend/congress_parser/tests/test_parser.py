from unittest import TestCase
from congress_parser.actions.utils import strike_emulation


class TestStrikeEmulation(TestCase):
    def test_119_hr_22(self):
        text = "Except as provided in subsection (b), notwithstanding any other Federal or State law, in addition to any other method of voter registration provided for under State law, each State shall establish procedures to register to vote in elections for Federal office-"
        result = strike_emulation("subsection (b)", "subsection (c)", text, False)
        self.assertEqual(
            result,
            "Except as provided in subsection (c), notwithstanding any other Federal or State law, in addition to any other method of voter registration provided for under State law, each State shall establish procedures to register to vote in elections for Federal office-",
        )

    def test_119_hr_22_2(self):
        text = "Each State motor vehicle driver's license application (including any renewal application) submitted to the appropriate State motor vehicle authority under State law shall serve as an application for voter registration with respect to elections for Federal office unless the applicant fails to sign the voter registration application."
        result = strike_emulation(
            "Each State motor vehicle driver's license application",
            "Subject to the requirements under section 8(j), each State motor vehicle driver's license application",
            text,
            False,
        )
        self.assertEqual(
            result,
            "Subject to the requirements under section 8(j), each State motor vehicle driver's license application (including any renewal application) submitted to the appropriate State motor vehicle authority under State law shall serve as an application for voter registration with respect to elections for Federal office unless the applicant fails to sign the voter registration application.",
        )

    def test_119_hr_22__parens(self):
        text = """states each eligibility requirement (including citizenship);"""
        result = strike_emulation(
            "(including citizenship)",
            ", including the requirement that the applicant provides documentary proof of United States citizenship",
            text,
            False,
        )
        self.assertEqual(
            result,
            "states each eligibility requirement, including the requirement that the applicant provides documentary proof of United States citizenship;",
        )