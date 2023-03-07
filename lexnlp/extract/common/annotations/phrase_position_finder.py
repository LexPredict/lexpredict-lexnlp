__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import regex as re
from typing import List, Tuple

from lexnlp.extract.common.text_beautifier import TextBeautifier


class PhrasePositionFinder:
    reg_space = re.compile(r'\s+')
    space_symbols = {' ', '\t'}

    @staticmethod
    def find_phrase_in_source_text(text: str,
                                   phrases: List[str],
                                   pos_start: int = 0,
                                   pos_end: int = 0) -> List[Tuple[str, int, int]]:
        """
        Though phrase is taken from text, it could be changed - e.g.,
        extra or removed spaces...

        Returns a list of (phrase, phrase_start) tuples
        :param text: text where to find phrases ([phrases])
        :param phrases: words or phrases to be found inside text
        :param pos_start: where to start (in source text)
        :param pos_end: where to stop searching
        :return: [('phrase A', 10, 18), ... ]
        """

        text = TextBeautifier.normalize_smb_preserve_len(text)
        condensed = ''
        ctos = []  # condensed-to-source indices
        stoc = [0] * len(text)  # source-to-condensed indices
        cindex = 0
        end_index = len(text)
        if pos_end:
            end_index = min(pos_end, end_index)

        for i in range(pos_start, end_index):
            a = text[i]
            if a not in PhrasePositionFinder.space_symbols:
                stoc[i] = cindex
                ctos.append(i)
                cindex += 1
                condensed += a
                continue
            stoc[i] = cindex

        phrases = [(p, 0, 0) for p in phrases]
        start = 0
        for i, phrase in enumerate(phrases):
            if start >= len(stoc):
                break
            word = TextBeautifier.normalize_smb_preserve_len(phrase[0])
            src_word = word
            pstart = text.find(word, start)
            if pstart < 0:
                transf_word = TextBeautifier.find_transformed_word(
                    text, word, start)
                if transf_word:
                    word, pstart = transf_word
            if pstart >= 0:
                start = pstart + len(word)
                phrases[i] = (phrase[0], pstart, start)
                continue
            # phrase is modified = extra spaces were added or removed
            word = PhrasePositionFinder.reg_space.sub('', word)
            cstart = stoc[start]
            con_word_start = condensed.find(word, cstart)
            con_word_start = con_word_start if con_word_start >= 0 else cstart
            src_index = ctos[con_word_start]
            w_end = src_index + len(src_word)
            if w_end < len(ctos):
                w_end = ctos[w_end]
            else:
                w_end = ctos[-1]
            start = src_index + len(src_word)
            phrases[i] = (phrase[0], src_index, w_end)

        return phrases
