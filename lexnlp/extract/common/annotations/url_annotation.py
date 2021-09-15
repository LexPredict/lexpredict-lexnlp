__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

from typing import Tuple, List
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation


class UrlAnnotation(TextAnnotation):
    record_type = 'url'
    """
    create an object of UrlAnnotation like
    cp = UrlAnnotation(name='name', coords=(0, 100), url='www.google.com')
    """
    def __init__(self,
                 coords: Tuple[int, int],
                 locale: str = 'en',
                 text: str = None,
                 url: str = None):
        super().__init__(
            name='',
            locale=locale,
            coords=coords,
            text=text)
        self.url = url

    def get_cite_value_parts(self) -> List[str]:
        return [self.url]

    def get_dictionary_values(self) -> dict:
        df = {
            'tags': {
                'Extracted Entity URL': self.url,
                'Extracted Entity Text': self.text
            }
        }
        return df
