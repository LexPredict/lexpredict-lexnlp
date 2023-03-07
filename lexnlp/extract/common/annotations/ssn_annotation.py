__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import Tuple, List
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation


class SsnAnnotation(TextAnnotation):
    """
    create an object of SsnAnnotation (Social Secutiry Number) like
    cp = SsnAnnotation(coords=(0, 100), value='1234 4321 1234')
    """
    record_type = 'ssn'

    def __init__(self,
                 coords: Tuple[int, int],
                 locale: str = 'en',
                 text: str = None,
                 number: str = None):
        super().__init__(
            name='',
            locale=locale,
            coords=coords,
            text=text)
        self.number = number

    def get_cite_value_parts(self) -> List[str]:
        return [self.number]

    def get_dictionary_values(self) -> dict:
        df = {
            'tags': {
                'Extracted Entity SSN': self.number or '',
                'Extracted Entity Text': self.text
            }
        }
        return df
