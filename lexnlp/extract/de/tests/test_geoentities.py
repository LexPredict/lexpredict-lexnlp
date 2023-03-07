__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import List
import pandas as pd
import io

from lexnlp.extract.common.annotations.geo_annotation import GeoAnnotation
from lexnlp.extract.de.geoentities import get_geoentities_custom_settings, \
    get_geoentity_annotations_custom_settings
from lexnlp.extract.de.tests.test_amounts import AssertionMixin
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester


sample_csv = '''
"Entity ID","Entity Category","Entity Name","Entity Priority","German Name","Spanish Name","French Name","ISO-3166-2","ISO-3166-3","Alias","Latitude","Longitude"
1,"Countries","Afghanistan",800,"Afghanistan","Afganistán;República Islámica de Afganistán","l'Afghanistan","AF","AFG","","33","66"
2,"Countries","Albania",800,"Albanien","República de Albania;Albania","l'Albanie;la République d'Albanie","AL","ALB","","41","20"
3,"Countries","Algeria",800,"Algerien","República Argelina Democrática y Popular;Argelia","Algérie","DZ","DZA","","28","3"
83,"Countries","Georgia",800,"Georgien","República de Georgia;Georgia","la Géorgie","GE","GEO","","41.99998","43.4999"
999,"Dummy","Georgia",700,"Georgien","República de Georgia;Georgia","la Géorgie","GE","GEO","","41.99998","43.4999"
'''
file_like = io.StringIO(sample_csv)
entity_df = pd.read_csv(file_like)


class TestGetGeoEntities(AssertionMixin):
    def test_diff_sort_priority(self):
        text = """some odd text and Georgien mentioned inside it"""
        res = list(get_geoentities_custom_settings(
            text,
            entity_df,
            conflict_resolving_field='id',
            priority_direction='desc',
            local_name_column='German Name'))
        self.assertEqual(res, [{'location_start': 18,
                                'location_end': 26,
                                'source': None,  # 'Georgien',
                                'Entity ID': 999,
                                'Entity Category': 'Dummy',
                                'Entity Name': 'Georgia',
                                'Entity Priority': 700,
                                'German Name': 'Georgien',
                                'ISO-3166-2': 'GE',
                                'ISO-3166-3': 'GEO',
                                'Alias': 'Georgien',
                                'Entity Type': 'geo entity'}])

        res = list(get_geoentities_custom_settings(
            text,
            entity_df,
            conflict_resolving_field='priority',
            priority_direction='asc',
            local_name_column='German Name'))
        self.assertEqual(83, res[0]['Entity ID'])

        res = list(get_geoentities_custom_settings(
            text,
            entity_df,
            conflict_resolving_field='priority',
            priority_direction='desc',
            local_name_column='German Name',
            extra_columns={'ISO-3166-2': 'iso_3166_2',
                           'ISO-3166-3': 'iso_3166_3'}))
        self.assertEqual(999, res[0]['Entity ID'])

    def test_de_annotations(self):
        text = "some odd text and Georgien mentioned inside it"
        ants = list(get_geoentity_annotations_custom_settings(
            text,
            entity_df,
            conflict_resolving_field='priority',
            priority_direction='desc',
            local_name_column='German Name'))
        self.assertEqual(1, len(ants))
        self.assertEqual((18, 26), ants[0].coords)

        self.assertEqual(999, ants[0].entity_id)
        self.assertEqual('Dummy', ants[0].entity_category)
        # self.assertEqual('', ants[0].source)
        self.assertEqual('Georgien', ants[0].name)
        self.assertEqual('Georgia', ants[0].name_en)
        self.assertEqual(700, ants[0].entity_priority)
        self.assertEqual('GE', ants[0].iso_3166_2)
        self.assertEqual('GEO', ants[0].iso_3166_3)
        self.assertEqual('Georgien', ants[0].alias)

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_ordered_geo_annotations,
            'lexnlp/typed_annotations/de/geoentity/geoentities.txt',
            GeoAnnotation)


def get_ordered_geo_annotations(text: str) -> List[GeoAnnotation]:
    ants = list(get_geoentity_annotations_custom_settings(
        text,
        entity_df,
        conflict_resolving_field='priority',
        priority_direction='asc',
        local_name_column='German Name'))
    ants.sort(key=lambda a: a.coords[0])
    return ants
