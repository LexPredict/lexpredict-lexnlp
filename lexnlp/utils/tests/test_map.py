from unittest import TestCase
from lexnlp.utils.map import Map

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestMap(TestCase):

    def test_map(self):
        m = Map({'name': 'Siemens', 'age': 108})
        self.assertEqual('Siemens', m['name'])
        self.assertEqual('Siemens', m.name)

        m = Map({'name': {'company': 'Siemens', 'trademark': '(c)Siemens'}})
        self.assertEqual('Siemens', m.name['company'])
        self.assertEqual('Siemens', m.name.company)
        m.name.specie = Map()
        m.name.specie.legal = 'xXx'
        self.assertEqual('xXx', m.name.specie.legal)
