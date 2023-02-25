__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import Tuple, List
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation


class TrademarkAnnotation(TextAnnotation):
    """
    create an object of TrademarkAnnotation like
    cp = TrademarkAnnotation(name='name', coords=(0, 100), trademark='CZ')
    """
    record_type = 'trademark'

    def __init__(self,
                 coords: Tuple[int, int],
                 locale: str = 'en',
                 text: str = None,
                 trademark: str = ''):
        super().__init__(
            name='',
            locale=locale,
            coords=coords,
            text=text)
        self.trademark = trademark

    def get_cite_value_parts(self) -> List[str]:
        return [self.trademark]

    def get_dictionary_values(self) -> dict:
        df = {
            'tags': {
                'Extracted Entity Trademark': self.trademark,
                'Extracted Entity Text': self.text
            }
        }
        return df
