__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import os
from unittest import TestCase

from lexnlp.extract.en.dict_entities import DictionaryEntry
from lexnlp.extract.common.annotation_type import AnnotationType
from lexnlp.extract.common.fact_extracting import FactExtractor, ExtractorResultFormat


def make_geoconfig():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    ge_path = dir_path + '/../../../../test_data/lexnlp/extract/en/tests/test_geoentities/'
    entities_fn = ge_path + 'geoentities.csv'
    aliases_fn = ge_path + 'geoaliases.csv'
    return list(DictionaryEntry.load_entities_from_files(entities_fn, aliases_fn))


EN_GEO_CONFIG = make_geoconfig()


class TestFactExtractor(TestCase):

    def test_one_fact_en(self):
        text = """
        Three people check into a hotel room. 
        The manager says the bill is $30, so each guest pays $10. 
        Later the manager realizes the bill should only be $25. 
        To rectify this, he gives the bellhop $5 to return to the guests.
        """
        facts = FactExtractor.parse_text(text,
                                         FactExtractor.LANGUAGE_EN,
                                         ExtractorResultFormat.fmt_class,
                                         extract_all=False,
                                         include_types={AnnotationType.money})
        self.assertTrue(AnnotationType.money in facts)
        facts = facts[AnnotationType.money]
        self.assertGreater(len(facts), 2)

    def test_one_fact_dict_en(self):
        text = """
        Three people check into a hotel room. 
        The manager says the bill is $30, so each guest pays $10. 
        Later the manager realizes the bill should only be $25. 
        To rectify this, he gives the bellhop $5 to return to the guests.
        """
        facts = FactExtractor.parse_text(text,
                                         FactExtractor.LANGUAGE_EN,
                                         ExtractorResultFormat.fmt_dict,
                                         extract_all=False,
                                         include_types={AnnotationType.money})
        self.assertTrue(AnnotationType.money in facts)
        facts = facts[AnnotationType.money]
        facts.sort(key=lambda f: f['attrs']['start'])
        self.assertEqual(5.0, float(facts[-1]['tags']['Extracted Entity Value']))

    def test_one_fact_de(self):
        text = """
        Die neuesten Bevölkerungszahlen basieren auf Daten der Volkszählung von 2011 in Indien. 
        Während des Jahrzehnts 2001–2011 hat sich das jährliche Bevölkerungswachstum in Indien 
        von 2,15 % auf 1,76% verlangsamt. [6] Basierend auf Daten aus zehnjährigen Volkszählungen 
        weisen Dadra und Nagar Haveli die schnellste Wachstumsrate von 55,5 Prozent auf, gefolgt
        von Daman und Diu (53,5 Prozent), Meghalaya (27,8 Prozent) und Arunachal Pradesh (25,9 Prozent).
        Nagaland verzeichnete die niedrigste Wachstumsrate von -0,5 Prozent.
        """
        facts = FactExtractor.parse_text(text,
                                         FactExtractor.LANGUAGE_DE,
                                         ExtractorResultFormat.fmt_class,
                                         extract_all=False,
                                         include_types={AnnotationType.percent})
        self.assertTrue(AnnotationType.percent in facts)
        facts = facts[AnnotationType.percent]
        self.assertGreater(len(facts), 2)

    def test_all_facts_en(self):
        text = """
        Country code: BE. Three people check into a hotel room.
        The manager says the bill is $30, so each guest pays $10. 
        Later the manager realizes the bill should only be $25. 
        To rectify this, he gives the bellhop $5 to return to the guests.
        """
        FactExtractor.ensure_parser_arguments_en(geo_config=EN_GEO_CONFIG)
        facts = FactExtractor.parse_text(text,
                                         FactExtractor.LANGUAGE_EN,
                                         ExtractorResultFormat.fmt_class,
                                         extract_all=True)
        self.assertTrue(AnnotationType.money in facts)
