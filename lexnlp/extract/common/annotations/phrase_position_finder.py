import regex as re
from typing import List, Tuple

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.7"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class PhrasePositionFinder:
    reg_space = re.compile(r'\s+')
    space_symbols = {' ', '\t'}

    @staticmethod
    def find_phrase_int_source_text(text: str,
                                    phrases: List[str]) -> List[Tuple[str, int]]:
        """
        Though phrase is taken from text, it could be changed - e.g.,
        extra or removed spaces...

        Returns a list of (phrase, phrase_start) tuples
        """
        condensed = ''
        ctos = []  # condensed-to-source indices
        stoc = [0] * len(text)  # source-to-condensed indices
        cindex = 0
        for i in range(len(text)):
            a = text[i]
            if a not in PhrasePositionFinder.space_symbols:
                stoc[i] = cindex
                ctos.append(i)
                cindex += 1
                condensed += a
                continue
            stoc[i] = cindex

        phrases = [(p, 0) for p in phrases]
        start = 0
        for i in range(len(phrases)):
            if start >= len(stoc):
                break
            phrase = phrases[i]
            word = phrase[0]
            src_word = word
            pstart = text.find(word, start)
            if pstart >= 0:
                phrases[i] = (src_word, pstart)
                start = pstart + len(word)
                continue
            # phrase is modified = extra spaces were added or removed
            word = PhrasePositionFinder.reg_space.sub('', word)
            cstart = stoc[start]
            con_word_start = condensed.find(word, cstart)
            con_word_start = con_word_start if con_word_start >= 0 else cstart
            src_index = ctos[con_word_start]
            start = src_index + len(word)
            phrases[i] = (src_word, src_index)

        return phrases
