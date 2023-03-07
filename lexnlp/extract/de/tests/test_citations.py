__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from lexnlp.extract.common.annotations.citation_annotation import CitationAnnotation
from lexnlp.extract.de.citations import get_citation_list, get_citation_annotations
from lexnlp.extract.de.tests.test_amounts import AssertionMixin
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester


def _sort(v):
    return sorted(v, key=lambda i: i['location_start'])


class CustomAssertionMixin(AssertionMixin):
    def assertSortedListEqual(self, list1, list2):
        self.assertListEqual(_sort(list1), _sort(list2))


class TestGetCitations(CustomAssertionMixin):
    def test_result(self):
        text = 'das Gesetz über die Beaufsichtigung der Versicherungsunternehmen (Versicherungsaufsichtsgesetz – VAG) vom 1. April 2015 (BGBl. I S. 434), das zuletzt durch Artikel 2 des Gesetzes vom 20. Juli 2017 (BGBl. I S. 2789) geändert worden ist, nach Maßgabe der §§ 61 ff. VAG - ,'
        res = get_citation_list(text)
        self.assertSortedListEqual(res, [{'location_start': 101,
                                          'location_end': 136,
                                          'text': ' vom 1. April 2015 (BGBl. I S. 434)',
                                          'article': '',
                                          'number': '',
                                          'paragraph': '',
                                          'subparagraph': '',
                                          'sentence': '',
                                          'letter': '',
                                          'date': '1. April 2015',
                                          'part': 'I',
                                          'page': '434',
                                          'year': ''},
                                         {'location_start': 156,
                                          'location_end': 214,
                                          'text': 'Artikel 2 des Gesetzes vom 20. Juli 2017 (BGBl. I S. 2789)',
                                          'article': '2',
                                          'number': '',
                                          'paragraph': '',
                                          'subparagraph': '',
                                          'sentence': '',
                                          'letter': '',
                                          'date': '20. Juli 2017',
                                          'part': 'I',
                                          'page': '2789',
                                          'year': ''}])

    def test_year(self):
        text = ' vom 15. Mai 2007 (BGBl. I S. 733 (1967)), die .'
        res = get_citation_list(text)
        self.assertEqual(res[0]['year'], '1967')

    def test_two_pages(self):
        text = ' vom 26. Juni 2001 (BGBl. I S. 1310, 1322), das '
        res = get_citation_list(text)
        self.assertEqual(res[0]['page'], '1310, 1322')

    def test_merged_citation(self):
        text = ' vom 2. Januar 2002 (BGBl. I S. 42, 2909; 2003 I S. 738), das '
        res = get_citation_list(text)
        self.assertEqual(len(res), 2)
        self.assertSortedListEqual(res, [{'location_start': 0,
                                          'location_end': 40,
                                          'text': ' vom 2. Januar 2002 (BGBl. I S. 42, 2909',
                                          'article': '',
                                          'number': '',
                                          'paragraph': '',
                                          'subparagraph': '',
                                          'sentence': '',
                                          'letter': '',
                                          'date': '2. Januar 2002',
                                          'part': 'I',
                                          'page': '42, 2909',
                                          'year': ''},
                                         {'location_start': 21,
                                          'location_end': 55,
                                          'text': 'BGBl. I S. 42, 2909; 2003 I S. 738',
                                          'article': '',
                                          'number': '',
                                          'paragraph': '',
                                          'subparagraph': '',
                                          'sentence': '',
                                          'letter': '',
                                          'date': '',
                                          'part': 'I',
                                          'page': '738',
                                          'year': '2003'}])

    def test_parts(self):
        text = 'Artikel 2 Absatz 1 Satz 1 Nr. 1 bis 3 Buchstabe b und c des Gesetzes v. 2. Januar 2002, BGBl. I S. 2477, das '
        res = get_citation_list(text)
        self.assertSortedListEqual(res, [{'location_start': 0,
                                          'location_end': 105,
                                          'text': 'Artikel 2 Absatz 1 Satz 1 Nr. 1 bis 3 Buchstabe b und c des Gesetzes v. 2. Januar 2002, BGBl. I S. 2477, ',
                                          'article': '2',
                                          'number': '1 bis 3',
                                          'paragraph': '1',
                                          'subparagraph': '',
                                          'sentence': '1',
                                          'letter': 'b und c',
                                          'date': '2. Januar 2002',
                                          'part': 'I',
                                          'page': '2477',
                                          'year': ''}])

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_citation_annotations,
            'lexnlp/typed_annotations/de/citation/citations.txt',
            CitationAnnotation)
