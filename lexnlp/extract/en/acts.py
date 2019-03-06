import regex as re


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


ACT_PARTS_RE = re.compile(r'''
(?P<text>
    (?:sections?\s+
        (?P<section>(?:\d+(?:\(\w\))*|,\s+|,?\s+and\s+)+)\s+of\s+the\s+
    )?
    (?P<act_name>
        (?:(?:[A-Z]\w+|[A-Z&]+|and|\d+(?:[a-z]{1,3})?),?\s*)*
        (?<=\s)Act
    )
    (?:\W+|$)
    (?:of\s+(?P<year>\d{4}))?
)''', re.VERBOSE|re.MULTILINE)


def get_acts(text):
    for match in ACT_PARTS_RE.finditer(text):
        captures = match.capturesdict()
        location_start, location_end = match.span()
        act_name = ''.join(captures.get('act_name') or [])
        yield {'location_start': location_start,
               'location_end': location_end,
               'act_name': act_name,
               'section': ''.join(captures.get('section') or []),
               'year': ''.join(captures.get('year') or []),
               'ambiguous': act_name == 'Act',
               'value': ''.join(captures.get('text') or [])}


def get_act_list(*args, **kwargs):
    return list(get_acts(*args, **kwargs))
