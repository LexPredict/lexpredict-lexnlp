import re

from lexnlp.extract.en.utils import NPExtractor
act_grammar = r"""
    NBAR:
        {<NNP.*|JJ|\(|\)|,>*<NNP.*>}  # Nouns, Adj-s, brackets, terminated with Nouns
    IN:
        {<CC|IN|,>}   # &, and, of
    NP:
        {(<NBAR><IN>)*<NBAR>(<IN><CD>)?}
"""

ACT_NPE = NPExtractor(act_grammar)
ACT_NPE.exception_sym += ['And', 'Of']
ACT_RE = re.compile('\s+Act(?:\W|$)')


def get_acts(text):
    act_names = [i for i in set(ACT_NPE.get_np(text)) if ACT_RE.search(i)]
    for act_name in act_names:
        act_name_re = re.compile(re.escape(act_name))
        for match in act_name_re.finditer(text):
            location_start, location_end = match.span()
            yield {'location_start': location_start,
                   'location_end': location_end,
                   'value': act_name}


def get_act_list(*args, **kwargs):
    return list(get_acts(*args, **kwargs))
