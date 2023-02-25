__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from decimal import Decimal
from typing import Tuple, List
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation
from lexnlp.utils.map import Map


class RatioAnnotation(TextAnnotation):
    """
    create an object of RatioAnnotation like
    cp = RatioAnnotation(name='name', coords=(0, 100), text='text text')
    """
    record_type = 'ratio'

    def __init__(
        self,
        coords: Tuple[int, int],
        locale: str = 'en',
        text: str = None,
        left: Decimal = None,
        right: Decimal = None,
        ratio: Decimal = None
    ) -> None:
        super().__init__(
            name='',
            locale=locale,
            coords=coords,
            text=text
        )
        self.left: Decimal = left
        self.right: Decimal = right
        self.ratio: Decimal = ratio

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
