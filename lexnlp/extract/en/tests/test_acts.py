from lexnlp.extract.en.acts import get_act_list
from lexnlp.extract.de.tests.test_amounts import AssertionMixin


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.4"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestGetActs(AssertionMixin):
    def test_correct_cases(self):
        text = "This is awesome but VERY Important Act in the sentence"
        res = get_act_list(text)
        self.assertEqual(res, [{'location_start': 20,
                                'location_end': 38,
                                'value': 'VERY Important Act'}])
        text = "This sentence which ends with VERY Important Act"
        res = get_act_list(text)
        self.assertEqual(res, [{'location_start': 30,
                                'location_end': 48,
                                'value': 'VERY Important Act'}])
        text = "This sentence which ends with point after VERY Important Act."
        res = get_act_list(text)
        self.assertEqual(res, [{'location_start': 42,
                                'location_end': 60,
                                'value': 'VERY Important Act'}])
        text = "test verb in phrase Updated VERY Important Act."
        res = get_act_list(text)
        self.assertEqual(res, [{'location_start': 28,
                                'location_end': 46,
                                'value': 'VERY Important Act'}])
        text = "test year in VERY Important Act of 1954."
        res = get_act_list(text)
        self.assertEqual(res, [{'location_start': 13,
                                'location_end': 39,
                                'value': 'VERY Important Act of 1954'}])


    def test_wrong_cases(self):
        text = "This is awesome but incorrect Important Activity in the sentence"
        res = get_act_list(text)
        self.assertEqual(res, [])
