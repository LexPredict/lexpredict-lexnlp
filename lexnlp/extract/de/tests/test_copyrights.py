from unittest import TestCase
from lexnlp.extract.de.copyrights import get_copyright_list, get_copyrights


class TestParseDeCourts(TestCase):
    """
    siemens.com globale Website © Siemens 1996 – 2019   Impressum   Datenschutz

    © 2019 urheberrecht.de | Alle Angaben ohne Gewähr

    Copyright © Mustervorlage und Vertrag kostenlos: Vorlagen für Beruf und Privat 2019.
    """
    def test_parse_empty_text(self):
        ret = get_copyright_list('')
        self.assertEqual(0, len(ret))
        ret = get_copyright_list("""

         """)
        self.assertEqual(0, len(ret))

    def test_parse_simply_phrase(self):
        text = "siemens.com globale Website Siemens © 1996 – 2019   "
        ret = get_copyright_list(text)
        self.assertEqual(1, len(ret), 'test_parse_simply_phrase failed')
        self.assertEqual(1996, ret[0].year_start)
        self.assertEqual(2019, ret[0].year_end)
        self.assertEqual("de", ret[0].locale)

    def test_parse_company_afterwards(self):
        text = "Copyright 2019, Siemens"
        ret = get_copyright_list(text, "XY")
        self.assertEqual(1, len(ret), 'test_parse_wo_company failed')
        self.assertEqual(2019, ret[0].year_end)
        self.assertEqual("XY", ret[0].locale)

        cps = list(get_copyrights(text))
        self.assertEqual(2019, cps[0]["tags"]["Extracted Entity End"])
