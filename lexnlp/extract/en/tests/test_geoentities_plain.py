import os
from unittest import TestCase
from typing import List
from lexnlp.extract.common.annotations.geo_annotation import GeoAnnotation
from lexnlp.extract.en.geoentities import get_geoentities, load_entities_dict_by_path, get_geoentity_annotations
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def make_geoconfig():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    ge_path = dir_path + '/../../../../test_data/lexnlp/extract/en/tests/test_geoentities/'
    entities_fn = ge_path + 'geoentities.csv'
    aliases_fn = ge_path + 'geoaliases.csv'
    return list(load_entities_dict_by_path(entities_fn, aliases_fn))


GEO_CONFIG = make_geoconfig()


def parse_geo_annotations(text: str) -> List[GeoAnnotation]:
    ants = list(get_geoentity_annotations(text, GEO_CONFIG))
    return ants


class TestGeoentitiesPlain(TestCase):
    def test_multiline_address(self):
        text = """
        Sincerely,
        DUKE REALTY CORPORATION
        Ana M. Hernandez
        Property Administrator
        
        2400 North Commerce  Parkway
        Suite 405
        Weston, FL 33326
        Main: 954-453-5660
        P: 954-453-5265
        F: 954.453.5695 
        ana.hernandez@dukerealty.com 
        www.dukerealty.com
        
        
        Cc: File
        LEASE
        """

        ds = list(get_geoentities(text, GEO_CONFIG))
        self.assertEqual(1, len(ds)) # how come?

    def test_simple_address(self):
        text = 'In BE, we usually write: John Smith, 23 Acacia Avenue, Harrogate, Yorkshire, 170000.'
        ds = parse_geo_annotations(text)
        self.assertEqual(2, len(ds))

        # here we (surprisingly) expect BE (for Belgium)
        ant = parse_geo_annotations(text)[0]
        self.assertEqual((3, 6), ant.coords)
        cite = ant.get_cite()
        self.assertEqual('/en/geoentity/Belgium/1993', cite)

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            parse_geo_annotations,
            'lexnlp/typed_annotations/en/geoentity/geoentities.txt',
            GeoAnnotation)
