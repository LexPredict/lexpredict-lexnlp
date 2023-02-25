__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import os
from inspect import cleandoc
from unittest import TestCase

from lexnlp.extract.en.dict_entities import DictionaryEntry
from lexnlp.extract.common.annotations.geo_annotation import GeoAnnotation
from lexnlp.extract.en.geoentities import get_geoentities, get_geoentity_annotations
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester


def make_geoconfig():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    ge_path = dir_path + '/../../../../test_data/lexnlp/extract/en/tests/test_geoentities/'
    entities_fn = ge_path + 'geoentities.csv'
    aliases_fn = ge_path + 'geoaliases.csv'
    return list(DictionaryEntry.load_entities_from_files(entities_fn, aliases_fn))


GEO_CONFIG = make_geoconfig()


class TestGeoentitiesPlain(TestCase):
    def test_multiline_address(self):
        text = """
        Sincerely,
        DUCK REALTY CORPORATION
        Ono M. Hernandez
        Property Administrator
        
        2400 North Commerce  Forkway
        Suite 405
        Weston, FL 55582
        Main: 954-453-4091
        P: 954-453-4091
        F: 954.453.4092 
        ono.hernandez@dukerealty.com 
        www.duckrealty.com
        
        
        Cc: File
        LEASE
        """

        ds = list(get_geoentities(text, GEO_CONFIG))
        self.assertEqual(1, len(ds))    # how come?

    def test_simple_address(self):
        text = 'In BE, we usually write: John Smith, 23 Acacia Avenue, Harrogate, Yorkshire, 170000.'
        ants = list(get_geoentity_annotations(text, GEO_CONFIG))
        self.assertEqual(2, len(ants))

        # here we (surprisingly) expect BE (for Belgium)
        ant = ants[0]
        self.assertEqual((3, 5), ant.coords)
        cite = ant.get_cite()
        self.assertEqual('/en/geoentity/Belgium', cite)

    def test_alias_locale(self):
        text = 'One Island two.'
        ants = list(get_geoentity_annotations(text, GEO_CONFIG))
        self.assertEqual(1, len(ants))
        self.assertEqual('Iceland', ants[0].name)
        self.assertEqual('de', ants[0].locale)

    def test_locale_is_en(self):
        text = 'Hello!!!!Mississippi!!!(US)!!!'
        ants = list(get_geoentity_annotations(text, GEO_CONFIG))
        self.assertEqual(2, len(ants))
        self.assertEqual('en', ants[0].locale)

    def test_file_samples(self):
        def parse_geo_annotations(text):
            return list(get_geoentity_annotations(text, GEO_CONFIG))

        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            parse_geo_annotations,
            'lexnlp/typed_annotations/en/geoentity/geoentities.txt',
            GeoAnnotation)

    def test_several_entries(self):
        text = '''Abbreviation “MS” can mean either MMMontserrat or Misssssisssssippi. And different
non-letter symbols should be treated correctly (MS).'''
        ants = list(get_geoentity_annotations(text, GEO_CONFIG))
        self.assertEqual(4, len(ants))

        self.assertEqual((14, 16), ants[0].coords)
        self.assertEqual((131, 133), ants[2].coords)

    def test_michigan_coords(self):
        text = 'This Contract (“Contract”) is entered into by and between ' +\
               'the City of Detroit, a Michigan municipal corporation'
        ants = list(get_geoentity_annotations(text, GEO_CONFIG))
        self.assertEqual(1, len(ants))
        fragment = text[ants[0].coords[0]: ants[0].coords[1]]
        self.assertEqual('Michigan', fragment)

    def test_chinese_republics(self):
        text: str = cleandoc("""
            In accordance with the Law of the People's Republic of China on Joint
            Ventures Using Chinese and Foreign Investment (the ""Joint Venture Law"") and
            other relevant Chinese laws and regulations, ABC Group Limited Liability
            Company and XYZ Technology Inc., in accordance with the principle of
            equality and mutual benefit and through friendly consultations, agree to jointly
            invest to establish a joint venture enterprise in Baoding City, Hebei Province
            of the People's Republic of China.
        """)
        annotations = list(get_geoentity_annotations(text, GEO_CONFIG))
        self.assertEqual(3, len(annotations))
        self.assertEqual('China', annotations[0].name)
        self.assertEqual('China', annotations[2].name)

    def test_abbreviated_country_name(self):
        text: str = cleandoc("""
            ABC Inc. has been working with the PRC since 1986. In 2021, ABC approved
            the construction of a new factory in CHN with the overarching goal
            of increasing manufacturing capabilities by 2030.
        """)
        annotations = list(get_geoentity_annotations(text, GEO_CONFIG))
        self.assertEqual(2, len(annotations))
        self.assertEqual('China', annotations[0].name)
        self.assertEqual('China', annotations[1].name)