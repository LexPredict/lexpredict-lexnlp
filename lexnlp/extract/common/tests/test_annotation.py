from unittest import TestCase
from lexnlp.extract.common.annotations.court_annotation import CourtAnnotation
from lexnlp.extract.common.annotations.copyright_annotation import CopyrightAnnotation

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.6"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestAnnotation(TestCase):
    def test_format_copyright_annotation(self):
        cp = CopyrightAnnotation(name='Siemens',
                                 coords=(0, 100),
                                 text='text text',
                                 locale='locale')
        cp.company = 'Siemens'
        cp.year_start = 1996
        s = cp.get_cite()  # '/copyright/Siemens/1996'
        self.assertGreater(s.find('copyright'), -1)
        self.assertGreater(s.find('Siemens'), -1)
        self.assertGreater(s.find('1996'), -1)

        cp.year_end = 2019
        cp.locale = 'en'
        s = cp.get_cite()  # '/en/copyright/Siemens/1996/2019'
        self.assertGreater(s.find('copyright'), -1)
        self.assertGreater(s.find('Siemens'), -1)
        self.assertGreater(s.find('1996'), -1)
        self.assertGreater(s.find('2019'), -1)

    def test_repr(self):
        ant = CourtAnnotation(name='GrossCourt',
                              coords=(1, 10), text='Court Gross',
                              locale='EN')
        s = ant.__repr__()
        self.assertGreater(len(s), 0)
