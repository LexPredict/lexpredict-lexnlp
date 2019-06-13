from lexnlp.extract.de.geoentities import get_geoentity_list
from lexnlp.extract.de.tests.test_amounts import AssertionMixin
import pandas as pd
import io


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.6"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


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
    def test_extract_geo(self):
        text = """some odd text and Georgien mentioned inside it"""
        result_columns = ["Entity ID", "Entity Category", "Entity Name", "Entity Priority", "German Name", "ISO-3166-2", "ISO-3166-3", "Alias"]
        res = get_geoentity_list(text, entity_df,
                                 parse_columns=["German Name", "ISO-3166-2", "ISO-3166-3", "Alias"],
                                 result_columns={i: i for i in result_columns},
                                 preformed_entity={'Entity Type': 'geo entity'},
                                 priority_sort_column="Entity Priority")
        self.assertEqual(res, [{'location_start': 17,
                                'location_end': 27,
                                'source': 'Georgien',
                                'Entity ID': 999,
                                'Entity Category': 'Dummy',
                                'Entity Name': 'Georgia',
                                'Entity Priority': 700,
                                'German Name': 'Georgien',
                                'ISO-3166-2': 'GE',
                                'ISO-3166-3': 'GEO',
                                'Alias': '',
                                'Entity Type': 'geo entity'}])
        res = get_geoentity_list(text, entity_df,
                                 parse_columns=["German Name", "ISO-3166-2", "ISO-3166-3", "Alias"],
                                 result_columns={i: i for i in result_columns[:-1]},
                                 preformed_entity={'Entity Type': 'SOME TAG'},
                                 priority_sort_column="Entity Priority",
                                 priority_sort_ascending=False)
        self.assertEqual(res, [{'location_start': 17,
                                'location_end': 27,
                                'source': 'Georgien',
                                'Entity ID': 83,
                                'Entity Category': 'Countries',
                                'Entity Name': 'Georgia',
                                'Entity Priority': 800,
                                'German Name': 'Georgien',
                                'ISO-3166-2': 'GE',
                                'ISO-3166-3': 'GEO',
                                'Entity Type': 'SOME TAG'}])
