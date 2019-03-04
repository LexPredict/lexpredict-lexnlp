from html import escape
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation


class CopyrightAnnotation(TextAnnotation):
    """
    create an object of CopyrightAnnotation like
    cp = CopyrightAnnotation(name='name', coords=(0, 100), text='text text')
    """
    def __init__(self, *args, **kwargs):
        super(CopyrightAnnotation, self).__init__(record_type='copyright', *args, **kwargs)
        self.company = ''
        self.year_start = 0
        self.year_end = 0

    def get_cite_value_encoded(self) -> str:
        parts = [escape(self.company),
                 '' if self.year_start == 0 else str(self.year_start),
                 '' if self.year_end == 0 else str(self.year_end)]
        return "/".join([p for p in parts if p])

    def to_dictionary(self) -> dict:
        df = {
            "attrs": {
                "start": self.coords[0],
                "end": self.coords[1]
            },
            "tags": {
                'Extracted Entity Type': 'copyright',
                'Extracted Entity Name': self.name,
                'Extracted Entity Text': self.text if self.text else self.name
            }
        }
        if self.company:
            df["tags"]["Extracted Entity Company"] = self.company
        if self.year_start > 0:
            df["tags"]["Extracted Entity Start"] = self.year_start
        if self.year_end > 0:
            df["tags"]["Extracted Entity End"] = self.year_end
        return df
