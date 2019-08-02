from typing import List, Tuple

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.7"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TextBeautifier:
    QUOTES = {'"', '“', '”'}
    PROPER_CLOSE_QUOTE = {'"': '"', '“': '”'}
    BRACES_O = {'(', '[', '{'}
    BRACES_C = {')', ']', '}'}
    BRACE_CL_BY_OP = {'(': ')', '{': '}', '[': ']'}

    APOS_SEPARATORS = {' ', '\t', '.', ',', ';'}
    APOS_SEPARATORS = APOS_SEPARATORS.union(BRACES_O)
    APOS_SEPARATORS = APOS_SEPARATORS.union(BRACES_C)

    @staticmethod
    def unify_quotes_braces(text: str,
                            empty_replacement: str = ''):
        try:
            return TextBeautifier.unify_quotes_braces_unsafe(text,
                                                             empty_replacement)
        except:  # pylint:disable=bare-except
            return text

    @staticmethod
    def unify_quotes_braces_unsafe(text: str,
                                   empty_replacement: str = ''):
        last_quote = None  # or ('"', 9)
        apos_coords = []  # type:List[int]
        braces_stack = [] # [("(", 18), ("[", 41)]
        replacements = [] # [(18, '{'), (82, '')]

        for i in range(len(text)):
            c = text[i]
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
            clear_text = [c for c in text]
            for rep in replacements:
                clear_text[rep[0]] = rep[1]
            text = ''.join(clear_text)
        return text

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
