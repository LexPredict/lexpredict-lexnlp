import os

from lexnlp.extract.common.language_dictionary_reader import LanguageDictionaryReader

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DeLanguageTokens:
    abbreviations = {'nr.', 'abs.', 'no.', 'act.', 'inc.', 'p.', 'Inc.'}
    articles = ['der', 'die', 'das', 'des', 'dem', 'den',
                'ein', 'eine', 'eines', 'einer', 'einem', 'einen']
    conjunctions = ['und', 'oder']

    @staticmethod
    def init():
        abr_file_path = os.path.join(os.path.dirname(__file__),
                                     'data/abbreviations.txt')
        if os.path.isfile(abr_file_path):
            file_set = LanguageDictionaryReader.read_str_set(abr_file_path)
            DeLanguageTokens.abbreviations = \
                DeLanguageTokens.abbreviations.union(file_set)


DeLanguageTokens.init()
