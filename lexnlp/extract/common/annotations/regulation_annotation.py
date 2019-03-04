from html import escape
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation


class RegulationAnnotation(TextAnnotation):
    """
    create an object of RegulationAnnotation like
    cp = RegulationAnnotation(name='name', coords=(0, 100), text='text text')
    """
    def __init__(self, *args, **kwargs):
        super(RegulationAnnotation, self).__init__(record_type='regulation', *args, **kwargs)
        self.country = ''
        self.source = 0

    def get_cite_value_encoded(self) -> str:
        parts = [escape(self.country),
                 escape(self.source)]
        return "/".join([p for p in parts if p])

    def to_dictionary(self) -> dict:
        dic = {
            "attrs": {
                "start": self.coords[0],
                "end": self.coords[1]
            },
            "tags": {
                "External Reference Issuing Country": self.country,
                "External Reference Text": self.name,
                "Extracted Entity Text": self.text if self.text else self.name
            }
        }
        if self.source:
            dic["tags"]["External Reference Source"] = self.source
        return dic
