__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DefinitionMatch:
    """
    used inside EsDefinitionsParser and SpanishParsingMethods
    to store intermediate parsing results
    """
    def __init__(self):
        self.name = None # type: str
        self.start = 0
        self.end = 0
        self.probability = 0
