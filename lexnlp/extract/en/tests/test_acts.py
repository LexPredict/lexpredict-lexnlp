__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from lexnlp.extract.common.annotations.act_annotation import ActAnnotation
from lexnlp.extract.en.acts import get_act_list, get_acts_annotations
from lexnlp.extract.de.tests.test_amounts import AssertionMixin
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester


class TestGetActs(AssertionMixin):
    def test_correct_cases(self):
        text = "This is awesome but VERY Important Act in the sentence"
        res = get_act_list(text)
        self.assertEqual([{'location_start': 20,
                           'location_end': 39,
                           'section': '',
                           'year': '',
                           'ambiguous': False,
                           'act_name': 'VERY Important Act',
                           'value': 'VERY Important Act '}], res)

        text = "This sentence which ends with VERY Important Act"
        res = get_act_list(text)
        self.assertEqual(res, [{'location_start': 30,
                                'location_end': 48,
                                'section': '',
                                'year': '',
                                'ambiguous': False,
                                'act_name': 'VERY Important Act',
                                'value': 'VERY Important Act'}])
        text = "This sentence which ends with point after VERY Important Act."
        res = get_act_list(text)
        self.assertEqual(res, [{'location_start': 42,
                                'location_end': 61,
                                'section': '',
                                'year': '',
                                'ambiguous': False,
                                'act_name': 'VERY Important Act',
                                'value': 'VERY Important Act.'}])
        text = "test verb in phrase Frozen VERY Important Act."
        res = get_act_list(text)
        self.assertEqual(res, [{'location_start': 20,
                                'location_end': 46,
                                'section': '',
                                'year': '',
                                'ambiguous': False,
                                'act_name': 'Frozen VERY Important Act',
                                'value': 'Frozen VERY Important Act.'}])
        text = "test year in VERY Important Act of 1954."
        res = get_act_list(text)
        self.assertEqual(res, [{'location_start': 13,
                                'location_end': 39,
                                'section': '',
                                'year': '1954',
                                'ambiguous': False,
                                'act_name': 'VERY Important Act',
                                'value': 'VERY Important Act of 1954'}])
        text = "test section 12 of the VERY Important Act of 1954."
        res = get_act_list(text)
        self.assertEqual(res, [{'location_start': 5,
                                'location_end': 49,
                                'section': '12',
                                'year': '1954',
                                'ambiguous': False,
                                'act_name': 'VERY Important Act',
                                'value': 'section 12 of the VERY Important Act of 1954'}])
        text = "test that part 12 of the VERY Important Act of 1954."
        res = get_act_list(text)
        self.assertEqual(res, [{'location_start': 25,
                                'location_end': 51,
                                'section': '',
                                'year': '1954',
                                'ambiguous': False,
                                'act_name': 'VERY Important Act',
                                'value': 'VERY Important Act of 1954'}])

    def test_ambiguous_cases(self):
        text = 'accordance with sections 751(a)(1) and 777(i)(1) of the Act, and 19 CFR 351'
        res = get_act_list(text)
        self.assertEqual(res, [{'location_start': 16,
                                'location_end': 61,
                                'act_name': 'Act',
                                'section': '751(a)(1) and 777(i)(1)',
                                'year': '',
                                'ambiguous': True,
                                'value': 'sections 751(a)(1) and 777(i)(1) of the Act, '}])

    def test_wrong_cases(self):
        text = "This is awesome but incorrect Important Activity in the sentence"
        res = get_act_list(text)
        self.assertEqual(res, [])

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_acts_annotations,
            'lexnlp/typed_annotations/en/act/acts.txt',
            ActAnnotation)
