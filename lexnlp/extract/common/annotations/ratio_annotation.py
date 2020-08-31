from typing import Tuple, List
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation
from lexnlp.utils.map import Map

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class RatioAnnotation(TextAnnotation):
    record_type = 'ratio'
    """
    create an object of RatioAnnotation like
    cp = RatioAnnotation(name='name', coords=(0, 100), text='text text')
    """
    def __init__(self,
                 coords: Tuple[int, int],
                 locale: str = 'en',
                 text: str = None,
                 left: float = None,
                 right: float = None,
                 ratio: float = None):
        super().__init__(
            name='',
            locale=locale,
            coords=coords,
            text=text)
        self.left = left
        self.right = right
        self.ratio = ratio

    def get_cite_value_parts(self) -> List[str]:
        parts = [str(self.left or ''),
                 str(self.right or '')]
        return parts

    def get_dictionary_values(self) -> dict:
        df = Map({
            'tags': {
                'Extracted Entity Ratio': str(self.ratio or ''),
                'Extracted Entity Text': self.text
            }
        })
        if self.left:
            df.tags['left'] = str(self.left)
        if self.right:
            df.tags['right'] = str(self.right)
        return df
