from html import escape
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation


class CourtCitationAnnotation(TextAnnotation):
    """
    create an object of CourtCitationAnnotation like
    cp = CourtCitationAnnotation(name='name', coords=(0, 100), text='text text')
    """
    def __init__(self, *args, **kwargs):
        super(CourtCitationAnnotation, self).__init__(record_type='court citation', *args, **kwargs)
        self.type = 'court citation'
        self.short_name = ''
        self.translated_name = ''

    def get_cite_value_encoded(self) -> str:
        parts = [escape(self.name),
                 escape(self.short_name),
                 escape(self.translated_name)]
        return "/".join([p for p in parts if p])

    def to_dictionary(self) -> dict:
        dc = {'attrs': {'start': self.coords[0], 'end': self.coords[1]},
              'tags': {
                  'Extracted Entity Type': 'court citation',
                  'Extracted Entity Text': self.text if self.text else self.name
              }}
        if self.name:
            dc["tags"]["Extracted Entity Name"] = self.name
        if self.short_name:
            dc["tags"]["Extracted Entity Short Name"] = self.short_name
        return dc
