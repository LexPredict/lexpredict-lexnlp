import os
# pylint: disable=unused-import
from typing import List, Pattern, Generator
# pylint: enable=unused-import
import regex as re
import pandas as pd
from lexnlp.extract.common.annotations.regulation_annotation import RegulationAnnotation

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class RegulationsParser:
    """
    Parses Spanish regulations (acts, institutions and so on):
    - "la emisión de instrumentos inscritos en el Registro Nacional de Valores, colocados"
      boils down to 'Registro Nacional de Valores'

    - expects words like 'registro', 'comisión', 'comision', 'ley del'
      that open the following phrase
    """
    def __init__(self, regulations_dataframe: pd.DataFrame = None):
        """
        :param regulations_dataframe: a pandas dataframe with 2 columns: trigger: str, position: str
        """
        self.regulations_dataframe = regulations_dataframe
        self.start_triggers = []  # type: List[str]
        self.reg_start_triggers = []  # type: List[Pattern]
        self.load_trigger_words()
        self.setup_regexes()
        self.annotations = []  # type: List[RegulationAnnotation]
        self.locale = ''

    def setup_regexes(self) -> None:
        # read *.csv content and build regexes out of this data
        triggers_str = "|".join(self.start_triggers)
        reg = re.compile(r"(?:(?<=[\s\b])|(?<=^))(%s)[^,\b;\.\n]+" % triggers_str,
                   re.UNICODE | re.IGNORECASE)
        self.reg_start_triggers.append(reg)

    def load_trigger_words(self) -> None:
        # load records like ('ley del', 'start') - (trigger_word, position)
        dtypes = {'trigger': str,
                  'position': str}
        if not self.regulations_dataframe:
            path = os.path.join(os.path.dirname(__file__), "../../config/es/es_regulations.csv")
            self.regulations_dataframe = pd.read_csv(path,
                                                     encoding="utf-8",
                                                     error_bad_lines=False,
                                                     converters=dtypes)
        subset = self.regulations_dataframe[['trigger', 'position']]
        tuples = [tuple(x) for x in subset.values]
        self.start_triggers = [t[0] for t in tuples if t[1] == 'start']

    def parse(self, text: str, locale: str = None) -> List[RegulationAnnotation]:
        # find annotations in text passed and return them as a list of objects
        self.locale = locale
        self.annotations = []
        self.match_start_trigger(text)
        for ant in self.annotations:
            ant.country = 'Spain'
        return self.annotations

    def match_start_trigger(self, phrase: str) -> None:
        """
        :param phrase: mediante la emisión de instrumentos inscritos en el Registro Nacional de Valores, colocados
        :return: {name: 'Registro Nacional de Valores', probability: 100, ...}
        """
        for reg in self.reg_start_triggers:
            for match in reg.finditer(phrase):
                text = match.group()
                coords = (match.start(), match.end())
                ant = RegulationAnnotation(
                    name=text, coords=coords, text=text,
                    locale=self.locale)
                self.annotations.append(ant)

    def trim_annotations(self) -> None:
        # remove excess words from each definition
        pass

    def get_annotations_as_dictionaries(self) -> List:
        # make dictionaries like
        # { "attr": { "start": 100, "end": 162 }, "tags": {..} }
        # out of annotations
        return [a.to_dictionary() for a in self.annotations]


def make_de_regulations_parser():
    p = RegulationsParser()
    return p


parser = make_de_regulations_parser()


def get_regulations(text: str, language: str = None) -> Generator[dict, None, None]:
    regs = parser.parse(text, language if language else 'es')
    for reg in regs:
        yield reg.to_dictionary()


def get_regulation_list(text: str, language: str = None) -> List[RegulationAnnotation]:
    return parser.parse(text, language if language else 'es')
