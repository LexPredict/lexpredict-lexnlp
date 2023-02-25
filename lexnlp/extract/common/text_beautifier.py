__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import List, Tuple, Optional, Union


class TextBeautifier:
    QUOTES = {'"', '“', '”'}
    PROPER_CLOSE_QUOTE = {'"': '"', '“': '”'}
    BRACES_O = {'(', '[', '{'}
    BRACES_C = {')', ']', '}'}
    BRACE_CL_BY_OP = {'(': ')', '{': '}', '[': ']'}

    APOS_SEPARATORS = {' ', '\t', '.', ',', ';'}
    APOS_SEPARATORS = APOS_SEPARATORS.union(BRACES_O)
    APOS_SEPARATORS = APOS_SEPARATORS.union(BRACES_C)

    # POS tokenizer often replaces words with some other
    # "standard" words - e.g., a pair of backticks for double quotes
    # <transformed>:<original>
    TRANSFORMED_WORDS = {"''": ['"', '``', '“', '”'],
                         '(': ['(', '[', '{'],
                         ')': [')', ']', '}'],
                         '``': ['"', '``', '“', '”'],
                         ':': [':', ';', '|']}

    # text might be enclosed in pair of special symbols
    # and we would remove them
    PAIR_BRACES = {'()', '[]', '{}',
                   '""', "''", '``', '“”'}

    @staticmethod
    def normalize_smb_preserve_len(text: str) -> str:
        """
        Normalize some of the string characters, preserving original length
        :param text: string to normalize
        :return: normalized string
        """
        if not text:
            return text
        resulted = ''
        for c in text:
            if c in TextBeautifier.QUOTES:
                c = '"'
            resulted += c
        return resulted

    @staticmethod
    def strip_pair_symbols(term_coords: Union[str, Tuple[str, int, int]]) -> \
            Union[str, Tuple[str, int, int]]:
        if not term_coords:
            return term_coords
        # build stack of pair quotes and brackets
        if isinstance(term_coords, str):
            term = term_coords
            coords = None
        else:
            term = term_coords[0]
            coords = [term_coords[1], term_coords[2]]

        stripped = term.lstrip()
        if stripped != term:
            if coords:
                coords[0] = coords[0] + len(term) - len(stripped)
                term = stripped
        stripped = term.rstrip()
        if stripped != term:
            if coords:
                coords[1] = coords[1] - len(term) + len(stripped)
                term = stripped
        term_coords = (term, coords[0], coords[1]) if coords else term
        if not term:
            return term_coords

        if term[0] in TextBeautifier.QUOTES:
            open_set = TextBeautifier.QUOTES
            close_set = TextBeautifier.QUOTES
            flip_stack = True
        elif term[0] in TextBeautifier.BRACES_O:
            open_set = TextBeautifier.BRACES_O
            close_set = TextBeautifier.BRACES_C
            flip_stack = False
        else:
            return term_coords

        stack = 0
        counter = 0
        for c in term:
            counter += 1
            if c in close_set:
                if flip_stack:
                    stack = 1 if not stack else 0
                else:
                    stack -= 1
            elif c in open_set:
                if flip_stack:
                    stack = 1 if not stack else 0
                else:
                    stack += 1
            if not stack:
                if counter < len(term):
                    return term_coords
        if stack:
            return term_coords

        term = term[1:-1]
        if coords:
            coords = [coords[0] + 1, coords[1] - 1]
        term_coords = (term, coords[0], coords[1],) if coords else term
        return TextBeautifier.strip_pair_symbols(term_coords)

    @staticmethod
    def unify_quotes_braces(text: str,
                            empty_replacement: str = '') -> str:
        try:
            return TextBeautifier.unify_quotes_braces_unsafe(
                text, 0, len(text), empty_replacement)[0]
        except:  # pylint:disable=bare-except
            return text

    @staticmethod
    def unify_quotes_braces_coords(
            text: str, start: int, end: int, empty_replacement: str = '') -> Tuple[str, int, int]:
        try:
            return TextBeautifier.unify_quotes_braces_unsafe(
                text, start, end, empty_replacement)
        except:  # pylint:disable=bare-except
            return text, start, end

    @staticmethod
    def unify_quotes_braces_unsafe(text: str, start: int, end: int,
                                   empty_replacement: str = '') -> Tuple[str, int, int]:
        """
        :param text: source text to "beautify"
        :param start: start coordinate of the text
        :param end: end coordinate of the text
        :param empty_replacement: replace unbalanced braces / quotes with this substring
        :return: str with all quotes and braces replaced with their "normal" forms
        """
        last_quote = None  # or ('"', 9)
        apos_coords = []  # type:List[int]
        braces_stack = []  # [("(", 18), ("[", 41)]
        replacements = []  # [(18, '{'), (82, '')]

        for i, c in enumerate(text):
            if c == "'":
                apos_coords.append(i)
                continue

            if c in TextBeautifier.BRACES_O:
                braces_stack.append((c, i))
            if c in TextBeautifier.BRACES_C:
                if not braces_stack:
                    # unbalanced braces
                    replacements.append((i, empty_replacement))
                    continue
                last_brace = braces_stack[-1]
                proper_brace = TextBeautifier.BRACE_CL_BY_OP[last_brace[0]]
                if c != proper_brace:
                    replacements.append((i, proper_brace))
                del braces_stack[-1]
                continue

            if c in TextBeautifier.QUOTES:
                if not last_quote:
                    last_quote = (c, i)
                    continue
                if i - last_quote[1] == 1:
                    # 2 quotes follow one another
                    replacements.append((i, empty_replacement))
                    continue
                clos_quote = TextBeautifier.PROPER_CLOSE_QUOTE.get(last_quote[0])
                if not clos_quote:
                    replacements.append((last_quote[1], c))
                    clos_quote = TextBeautifier.PROPER_CLOSE_QUOTE.get(c)
                # if " is paired with “
                if clos_quote and c != clos_quote:
                    replacements.append((i, clos_quote))
                last_quote = None

        # check all stacks are empty
        if braces_stack:
            # remove all unclosed braces
            replacements += [(b[1], empty_replacement) for b in braces_stack]

        # ... check quotes
        if last_quote:
            if apos_coords:
                # try to pair quote with apostrophe
                replace = TextBeautifier.find_pair_among_apostrophe(
                    text, apos_coords, last_quote)
                replacements.append((replace, last_quote[0]))
            else:
                replacements.append((last_quote[1], empty_replacement))

        # apply replacements
        if replacements:
            clear_text = list(text)
            for rep_coord, rep_word in replacements:
                if rep_coord == 0:
                    start = start + 1 - len(rep_word)
                elif rep_coord == len(clear_text) - 1:
                    end = end - 1 + len(rep_word)
                clear_text[rep_coord] = rep_word
            text = ''.join(clear_text)
        return text, start, end

    @staticmethod
    def find_pair_among_apostrophe(text: str,
                                   apos_coords: List[int],
                                   quote: Tuple[str, int]) -> int:

        # find the nearest apostrophe to pair it with dub quote
        # but prefer those separated by spaces
        apos_weighted = []
        for coord in apos_coords:
            dist = abs(coord - quote[1])
            separated_k = 0
            if coord > 0 and text[coord - 1] in TextBeautifier.APOS_SEPARATORS:
                separated_k += 1
            if coord < len(text) - 1 and text[coord + 1] in TextBeautifier.APOS_SEPARATORS:
                separated_k += 0.5

            weight = dist - 1000 * separated_k
            apos_weighted.append((coord, weight))

        # get the candidate (apostrophe coords) with min weight
        apos_weighted.sort(key=lambda c: c[1])
        return apos_weighted[0][0]

    @staticmethod
    def find_transformed_word(txt: str, word: str, offset: int) \
            -> Optional[Tuple[str, int]]:
        """
        Searches for transformed word into text, returns
        transformed words with its start position
        """
        trans_set = TextBeautifier.TRANSFORMED_WORDS.get(word)
        if not trans_set:
            return None

        indices = [(tw, txt.find(tw, offset)) for tw in trans_set]
        indices = [i for i in indices if i[1] >= 0]
        indices.sort(key=lambda w: w[1])
        if indices:
            new_offset = indices[0][1]
            leap_size = new_offset - offset
            if leap_size < len(word) + 2:
                return indices[0]
        return None

    @staticmethod
    def strip_string_coords(text: str,
                            start: int,
                            end: int,
                            trim_symbols: Optional[str] = None) -> Tuple[str, int, int]:
        text_trimmed = text.lstrip(trim_symbols) if trim_symbols else text.lstrip()
        start = start + len(text) - len(text_trimmed)
        text = text_trimmed

        text_trimmed = text.rstrip(trim_symbols) if trim_symbols else text.rstrip()
        end = end - len(text) + len(text_trimmed)
        text = text_trimmed
        return text, start, end

    @staticmethod
    def lstrip_string_coords(text: str,
                            start: int,
                            end: int,
                            trim_symbols: Optional[str] = None) -> Tuple[str, int, int]:
        text_trimmed = text.lstrip(trim_symbols) if trim_symbols else text.lstrip()
        start = start + len(text) - len(text_trimmed)
        text = text_trimmed
        return text, start, end

    @staticmethod
    def rstrip_string_coords(text: str,
                            start: int,
                            end: int,
                            trim_symbols: Optional[str] = None) -> Tuple[str, int, int]:
        text_trimmed = text.rstrip(trim_symbols) if trim_symbols else text.rstrip()
        end = end - len(text) + len(text_trimmed)
        text = text_trimmed
        return text, start, end
