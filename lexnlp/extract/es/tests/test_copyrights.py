from unittest import TestCase
from lexnlp.extract.es.copyrights import get_copyright_list, get_copyrights


class TestParseDeCourts(TestCase):
    def test_parse_empty_text(self):
        ret = get_copyright_list('')
        self.assertEqual(0, len(ret))
        ret = get_copyright_list("""

         """)
        self.assertEqual(0, len(ret))

    def test_parse_simply_phrase(self):
        text = "Website BBC Mundo © 1996 – 2019   "
        ret = get_copyright_list(text)
        self.assertEqual(1, len(ret), 'test_parse_simply_phrase failed')
        self.assertEqual(1996, ret[0].year_start)
        self.assertEqual(2019, ret[0].year_end)

    def test_two_symbols(self):
        text = "Copyright © 2019 BBC"
        ret = get_copyright_list(text)
        self.assertEqual(1, len(ret), 'test_two_symbols failed')
        self.assertEqual(2019, ret[0].year_end)
        self.assertEqual('es', ret[0].locale)

        ret = list(get_copyrights(text))
        self.assertEqual(1, len(ret), 'test_two_symbols failed')
        self.assertEqual(2019, ret[0]["tags"]["Extracted Entity End"])
