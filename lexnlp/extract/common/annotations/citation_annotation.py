__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import Tuple, List, Dict, Any
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation
from lexnlp.utils.map import Map


class CitationAnnotation(TextAnnotation):
    """
    create an object of CitationAnnotation like
    cp = CitationAnnotation(name='name', coords=(0, 100), text='text text')
    """
    record_type = 'citation'

    def __init__(self,
                 coords: Tuple[int, int],
                 locale: str = 'en',
                 text: str = '',
                 volume: int = None,
                 volume_str: str = None,
                 year: int = None,
                 reporter: str = None,
                 reporter_full_name: str = None,
                 page: int = None,
                 page_range: str = None,
                 court: str = None,
                 source: str = None,
                 article: int = None,
                 paragraph: str = None,
                 subparagraph: str = None,
                 letter: str = None,
                 sentence: int = None,
                 date: str = None,
                 part: str = None,
                 year_str: str = None):
        super().__init__(
            name='',
            locale=locale,
            coords=coords,
            text=text)

        self.volume = volume
        self.volume_str = volume_str
        self.year = year
        self.reporter = reporter
        self.reporter_full_name = reporter_full_name
        self.page = page
        self.page_range = page_range
        self.court = court
        self.source = source
        self.article = article
        self.paragraph = paragraph
        self.subparagraph = subparagraph
        self.letter = letter
        self.sentence = sentence
        self.date = date
        self.part = part
        self.year_str = year_str

    def get_cite_value_parts(self) -> List[str]:
        pages = str(self.page_range or self.page or '')
        parts = [self.source or '',
                 str(self.volume or ''),
                 str(self.year or ''),
                 pages,
                 self.court,
                 self.reporter or self.reporter_full_name]
        return parts

    def get_dictionary_values(self) -> dict:
        df = Map({
            "tags": {
                'Extracted Entity Text': self.text
            }
        })
        if self.volume:
            df.tags["Extracted Entity Volume"] = self.volume
        if self.year:
            df.tags["Extracted Entity Year"] = str(self.year)
        if self.page:
            df.tags["Extracted Entity Page"] = str(self.page)
        if self.page_range:
            df.tags["Extracted Entity Page Range"] = str(self.page_range)
        if self.reporter:
            df.tags["Extracted Entity Reporter"] = str(self.reporter)
        if self.reporter_full_name:
            df.tags["Extracted Entity Reporter Full Name"] = str(self.reporter_full_name)
        if self.reporter:
            df.tags["Extracted Entity Court"] = str(self.court)
        if self.reporter:
            df.tags["Extracted Entity Source"] = str(self.source)

        return df

    def to_dictionary_legacy(self) -> Dict[str, Any]:
        return {
            'citation_str': str(self.source),
            'court': self.court,
            'page': self.page,
            'page2': self.page_range,
            'reporter': self.reporter,
            'reporter_full_name': self.reporter_full_name,
            'volume': self.volume,
            'year': self.year
        }
