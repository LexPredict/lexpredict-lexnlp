__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import Tuple, Dict, Any, List
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation
from lexnlp.utils.map import Map


class CusipAnnotation(TextAnnotation):
    """
    create an object of CusipAnnotation like
    cp = CusipAnnotation(coords=(0, 100))
    """
    record_type = 'cusip'

    def __init__(self,
                 coords: Tuple[int, int],
                 locale: str = 'en',
                 name: str = '',
                 text: str = None,
                 code: str = None,
                 internal: bool = None,
                 ppn: str = None,
                 tba: dict = None,
                 checksum: str = None,
                 issue_id: str = None,
                 issuer_id: str = None):
        super().__init__(
            name=name,
            locale=locale,
            coords=coords,
            text=text)

        self.code = code
        self.internal = internal
        self.ppn = ppn
        self.tba = tba
        self.checksum = checksum
        self.issue_id = issue_id
        self.issuer_id = issuer_id

    def get_cite_value_parts(self) -> List[str]:
        parts = [self.code or '',
                 self.ppn or '',
                 # self.tba or '',
                 self.issue_id or '',
                 self.issuer_id or '']
        return parts

    def get_dictionary_values(self) -> dict:
        df = Map({
            'tags': {
                'Extracted Entity Code': self.code,
                'Extracted Entity Internal': self.internal
            }
        })
        if self.tba:
            df.tags['Extracted Entity TBA'] = self.tba
        if self.ppn:
            df.tags['Extracted Entity PPN'] = self.ppn
        if self.checksum:
            df.tags['Extracted Entity Checksum'] = self.ppn
        if self.issuer_id:
            df.tags['Extracted Entity Issuer ID'] = self.issuer_id
        if self.issue_id:
            df.tags['Extracted Entity Issue ID'] = self.issue_id

        return df

    def to_dictionary_legacy(self) -> Dict[str, Any]:
        return {'location_start': self.coords[0],
                'location_end': self.coords[1],
                'text': self.code,
                'issuer_id': self.issuer_id,
                'issue_id': self.issue_id,
                'checksum': self.checksum,
                'internal': self.internal,
                'tba': self.tba,
                'ppn': self.ppn}
