__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import os
# pylint: disable=unused-import
from typing import List, Pattern, Generator
# pylint: enable=unused-import
import regex as re
from pandas import DataFrame, read_csv

from lexnlp.extract.common.base_path import lexnlp_base_path
from lexnlp.extract.common.annotations.regulation_annotation import RegulationAnnotation


class RegulationsParser:
    """
    Parses Spanish regulations (acts, institutions and so on):
    - "la emisión de instrumentos inscritos en el Registro Nacional de Valores, colocados"
      boils down to 'Registro Nacional de Valores'

    - expects words like 'registro', 'comisión', 'comision', 'ley del'
      that open the following phrase
    """
    def __init__(self, regulations_dataframe: DataFrame = None):
        """
        :param regulations_dataframe: a pandas dataframe with 2 columns: trigger: str, position: str
        """
        self.regulations_dataframe = regulations_dataframe
        self.start_triggers: List[str] = []
        self.reg_start_triggers: List[Pattern] = []
        self.load_trigger_words()
        self.setup_regexes()

    def setup_regexes(self) -> None:
        """
        Read *.csv content and build regexes out of this data
        """
        triggers_str = "|".join(self.start_triggers)
        reg = re.compile(r"(?:(?<=[\s\b])|(?<=^))(%s)[^,\b;\.\n]+" % triggers_str,
                   re.UNICODE | re.IGNORECASE)
        self.reg_start_triggers.append(reg)

    def load_trigger_words(self) -> None:
        """
        Load records like ('ley del', 'start') - (trigger_word, position)
        """
        dtypes = {'trigger': str, 'position': str}
        if not self.regulations_dataframe:
            path = os.path.join(lexnlp_base_path, 'lexnlp/config/es/es_regulations.csv')
            self.regulations_dataframe = read_csv(path, encoding='utf-8', error_bad_lines=False, converters=dtypes)
        subset = self.regulations_dataframe[['trigger', 'position']]
        tuples = [tuple(x) for x in subset.values]
        self.start_triggers = [t[0] for t in tuples if t[1] == 'start']

    def parse(self, text: str, locale: str = 'es') -> Generator[RegulationAnnotation, None, None]:
        """
        Find annotations in text passed and return them as a list of objects
        """
        for reg in self.reg_start_triggers:
            for match in reg.finditer(text):
                text = match.group()
                coords = (match.start(), match.end())
                annotation = RegulationAnnotation(
                    name=text,
                    coords=coords,
                    text=text,
                    locale=locale,
                    country='Spain',
                )
                yield annotation


parser = RegulationsParser()


def get_regulation_annotations(text: str, language: str = 'es') -> Generator[RegulationAnnotation, None, None]:
    yield from parser.parse(text, language)


def get_regulation_annotation_list(text: str, language: str = 'es') -> List[RegulationAnnotation]:
    return list(parser.parse(text, language))


def get_regulations(text: str, language: str = 'es') -> Generator[dict, None, None]:
    for reg in parser.parse(text, language):
        yield reg.to_dictionary()


def get_regulation_list(text: str, language: str = None) -> List[dict]:
    return list(get_regulations(text, language))
