__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import Tuple, List

from lexnlp.extract.common.annotations.text_annotation import TextAnnotation


class LawAnnotation(TextAnnotation):
    """
    create an object of LawAnnotation like
    cp = LawAnnotation(name='name', coords=(0, 100), text='text text')
    """
    record_type = 'law'

    def __init__(self,
                 coords: Tuple[int, int],
                 locale: str = '',
                 name: str = '',
                 text: str = ''):
        super().__init__(
            coords=coords,
            locale=locale,
            name=name,
            text=text)

    def get_cite_value_parts(self) -> List[str]:
        return [self.name]

    def get_dictionary_values(self) -> dict:
        ant = {
                'tags': {
                    'Extracted Entity Name': self.name,
                    'Extracted Entity Text': self.text or self.name
                }
            }
        return ant
