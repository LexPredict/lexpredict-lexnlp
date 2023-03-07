__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import copy
import logging

import dateparser
import regex as re
from dateutil import tz, parser
from typing import Tuple, List, Dict, Optional

from lexnlp.extract.all_locales.languages import Locale


logger = logging.getLogger('datefinder')


class DateFragment:
    """
    This class describes big chunks of text that may contain date strings
    Each chunk includes of one of more tokens
    Each token is build upon DATE_REGEX matches
    """

    def __init__(self):
        self.match_str = ''
        self.indices = (0, 0)
        self.captures = {}  # type:Dict[str, List[str]]
        self.matches_count = 0

    def __repr__(self):
        str_capt = ', '.join(['"{}": [{}]'.format(c, self.captures[c]) for c in self.captures])
        return '{} [{}, {}]\nCaptures: {}'.format(self.match_str, self.indices[0], self.indices[1], str_capt)

    def get_captures_count(self):
        return sum([len(self.captures[m]) for m in self.captures])

    def get_captures_group_count(self):
        return sum([1 if len(self.captures[m]) > 0 else 0 for m in self.captures])


def refine_pattern_start_end(pattern: str) -> str:
    """
    The updated Regex pattern doesn't allow alpha characters prepended or appended
    to the match.
    :param pattern: monday|tuesday
    :return: (?<![^\W\d_])monday(?![^\W\d_])|(?<![^\W\d_])tuesday(?![^\W\d_])
    """
    return '|'.join([fr'(?<![^\W\d_]){p}(?![^\W\d_])' for p in pattern.split('|')])


class DateFinder:
    """
    Locates dates in a text
    """

    DIGITS_MODIFIER_PATTERN = r'\d+st|\d+th|\d+rd|first|second|third|fourth|fifth|sixth|seventh|eighth|nineth|tenth|next|last'
    DIGITS_PATTERN = r'\d{1,4}'
    DAYS_PATTERN = 'monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|tues|wed|thur|thurs|fri|sat|sun'
    DAYS_PATTERN = refine_pattern_start_end(DAYS_PATTERN)
    MONTHS_PATTERN = 'january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec'
    MONTHS_PATTERN = refine_pattern_start_end(MONTHS_PATTERN)

    TIMEZONES_PATTERN = 'ACDT|ACST|ACT|ACWDT|ACWST|ADDT|ADMT|ADT|AEDT|AEST|AFT|AHDT|AHST|AKDT|AKST|AKTST|AKTT|ALMST|ALMT|AMST|AMT|ANAST|ANAT|ANT|APT|AQTST|AQTT|ARST|ART|ASHST|ASHT|AST|AWDT|AWST|AWT|AZOMT|AZOST|AZOT|AZST|AZT|BAKST|BAKT|BDST|BDT|BEAT|BEAUT|BIOT|BMT|BNT|BORT|BOST|BOT|BRST|BRT|BST|BTT|BURT|CANT|CAPT|CAST|CAT|CAWT|CCT|CDDT|CDT|CEDT|CEMT|CEST|CET|CGST|CGT|CHADT|CHAST|CHDT|CHOST|CHOT|CIST|CKHST|CKT|CLST|CLT|CMT|COST|COT|CPT|CST|CUT|CVST|CVT|CWT|CXT|ChST|DACT|DAVT|DDUT|DFT|DMT|DUSST|DUST|EASST|EAST|EAT|ECT|EDDT|EDT|EEDT|EEST|EET|EGST|EGT|EHDT|EMT|EPT|EST|ET|EWT|FET|FFMT|FJST|FJT|FKST|FKT|FMT|FNST|FNT|FORT|FRUST|FRUT|GALT|GAMT|GBGT|GEST|GET|GFT|GHST|GILT|GIT|GMT|GST|GYT|HAA|HAC|HADT|HAE|HAP|HAR|HAST|HAT|HAY|HDT|HKST|HKT|HLV|HMT|HNA|HNC|HNE|HNP|HNR|HNT|HNY|HOVST|HOVT|HST|ICT|IDDT|IDT|IHST|IMT|IOT|IRDT|IRKST|IRKT|IRST|ISST|IST|JAVT|JCST|JDT|JMT|JST|JWST|KART|KDT|KGST|KGT|KIZST|KIZT|KMT|KOST|KRAST|KRAT|KST|KUYST|KUYT|KWAT|LHDT|LHST|LINT|LKT|LMT|LMT|LMT|LMT|LRT|LST|MADMT|MADST|MADT|MAGST|MAGT|MALST|MALT|MART|MAWT|MDDT|MDST|MDT|MEST|MET|MHT|MIST|MIT|MMT|MOST|MOT|MPT|MSD|MSK|MSM|MST|MUST|MUT|MVT|MWT|MYT|NCST|NCT|NDDT|NDT|NEGT|NEST|NET|NFT|NMT|NOVST|NOVT|NPT|NRT|NST|NT|NUT|NWT|NZDT|NZMT|NZST|OMSST|OMST|ORAST|ORAT|PDDT|PDT|PEST|PET|PETST|PETT|PGT|PHOT|PHST|PHT|PKST|PKT|PLMT|PMDT|PMMT|PMST|PMT|PNT|PONT|PPMT|PPT|PST|PT|PWT|PYST|PYT|QMT|QYZST|QYZT|RET|RMT|ROTT|SAKST|SAKT|SAMT|SAST|SBT|SCT|SDMT|SDT|SET|SGT|SHEST|SHET|SJMT|SLT|SMT|SRET|SRT|SST|STAT|SVEST|SVET|SWAT|SYOT|TAHT|TASST|TAST|TBIST|TBIT|TBMT|TFT|THA|TJT|TKT|TLT|TMT|TOST|TOT|TRST|TRT|TSAT|TVT|ULAST|ULAT|URAST|URAT|UTC|UYHST|UYST|UYT|UZST|UZT|VET|VLAST|VLAT|VOLST|VOLT|VOST|VUST|VUT|WARST|WART|WAST|WAT|WDT|WEDT|WEMT|WEST|WET|WFT|WGST|WGT|WIB|WIT|WITA|WMT|WSDT|WSST|WST|WT|XJT|YAKST|YAKT|YAPT|YDDT|YDT|YEKST|YEKST|YEKT|YEKT|YERST|YERT|YPT|YST|YWT|zzz'
    ## explicit north american timezones that get replaced
    NA_TIMEZONES_PATTERN = 'pacific|eastern|mountain|central'
    NA_TIMEZONES_PATTERN = refine_pattern_start_end(NA_TIMEZONES_PATTERN)
    ALL_TIMEZONES_PATTERN = TIMEZONES_PATTERN + '|' + NA_TIMEZONES_PATTERN
    DELIMITERS_PATTERN = r'[/\:\-\,\.\s\_\+\@]+'
    TIME_PERIOD_PATTERN = r'a\.m\.|am|p\.m\.|pm'
    ## can be in date strings but not recognized by dateutils
    EXTRA_TOKENS_PATTERN = 'due|by|on|during|standard|daylight|savings|time|date|dated|day|of|from|to|through|between|until|z|at|t'

    ## TODO: Get english numbers?
    ## http://www.rexegg.com/regex-trick-numbers-in-english.html

    RELATIVE_PATTERN = 'before|after|next|last|ago'
    TIME_SHORTHAND_PATTERN = 'noon|midnight|today|yesterday'
    UNIT_PATTERN = 'second|minute|hour|day|week|month|year'

    ## Time pattern is used independently, so specified here.
    TIME_PATTERN = r"""
    (?P<time>
        ## Captures in format XX:YY(:ZZ) (PM) (EST)
        (
            (?P<hours>\d{{1,2}})
            \:
            (?P<minutes>\d{{1,2}})
            (\:(?<seconds>\d{{1,2}}))?
            ([\.\,](?<microseconds>\d{{1,6}}))?
            (\s*(?P<time_periods>{time_periods}))?
            (\s*(?P<timezones>{timezones}))?
        )
        |
        ## Captures in format 11 AM (EST)
        ## Note with single digit capture requires time period
        (
            (?P<hours>\d{{1,2}})
            (\s*(?P<time_periods>{time_periods}))
            (\s*(?P<timezones>{timezones}))*
        )
    )
    """.format(
        time_periods=TIME_PERIOD_PATTERN,
        timezones=ALL_TIMEZONES_PATTERN
    )

    DATES_PATTERN = r"""
    (
        (
            {time}
            |
            ## Grab any digits
            (?P<digits_modifier>{digits_modifier})
            |
            (?P<digits>{digits})
            |
            (?P<days>{days})
            |
            (?P<months>{months})
            |
            ## These abbreviations could be in phrases and make parsing date harder.
            ## Should be located before delimiters in regular expression pattern
            (?:\s)(?:[A-Z][a-z]{{1,3}}\.)(\s*[^a-zA-Z\s]+)(?![\w\d])
            |
            ## Delimiters, ie Tuesday[,] July 18 or 6[/]17[/]2008
            ## as well as blank space
            (?P<delimiters>{delimiters})
            |
            ## These tokens could be in phrases that dateutil does not yet recognize
            ## Some are US Centric
            (?<![\w\d])(?P<extra_tokens>({extra_tokens}))(?![\w\d])

        ## We need at least three items to match for minimal datetime parsing
        ## ie 10pm
        ){{1,1}}
    )
    """

    ALL_GROUPS = ['time', 'digits_modifier', 'digits', 'days', 'months', 'delimiters',
                  'extra_tokens', 'timezones', 'time_periods', 'hours', 'minutes', 'seconds',
                  'microseconds']

    DATES_PATTERN = DATES_PATTERN.format(
        time=TIME_PATTERN,
        digits=DIGITS_PATTERN,
        digits_modifier=DIGITS_MODIFIER_PATTERN,
        days=DAYS_PATTERN,
        months=MONTHS_PATTERN,
        delimiters=DELIMITERS_PATTERN,
        extra_tokens=EXTRA_TOKENS_PATTERN,
    )

    DATE_REGEX = re.compile(DATES_PATTERN,
                            re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL | re.VERBOSE)

    TIME_REGEX = re.compile(TIME_PATTERN,
                            re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL | re.VERBOSE)

    # split ranges
    RANGE_SPLIT_PATTERN = r'\Wto\W|\Wthrough\W'

    RANGE_SPLIT_REGEX = re.compile(RANGE_SPLIT_PATTERN,
                                   re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

    ## These tokens can be in original text but dateutil
    ## won't handle them without modification
    REPLACEMENTS = {
        "standard": " ",
        "daylight": " ",
        "savings": " ",
        "time": " ",
        "date": " ",
        "by": " ",
        "due": " ",
        "on": " ",
        "to": " ",
    }

    TIMEZONE_REPLACEMENTS = {
        "pacific": "PST",
        "eastern": "EST",
        "mountain": "MST",
        "central": "CST",
    }

    ## Characters that can be removed from ends of matched strings
    STRIP_CHARS = ' \n\t:-.,_'

    def __init__(self, base_date=None):
        self.base_date = base_date

    def tokenize_string(self, text: str) -> List[Tuple[str, str, Dict[str, List[str]]]]:
        last_index: int = 0
        items: List[Tuple[str, str, Dict[str, List[str]]]] = []

        for match in self.DATE_REGEX.finditer(text):
            match_str = match.group(0)
            indices = match.span(0)
            captures = {k: v for k, v in match.capturesdict().items() if v}
            for capt_key in captures:
                captures[capt_key] = [c.strip() for c in captures[capt_key]]
            group = self.get_token_group(captures)

            if indices[0] > last_index:
                items.append((text[last_index:indices[0]], '', {}))
            items.append((match_str, group, captures))
            last_index = indices[1]
        if last_index < len(text):
            items.append((text[last_index:len(text)], '', {}))
        return items

    def merge_tokens(self, tokens: List[Tuple[str, str]]) -> List[DateFragment]:
        MIN_MATCHES = 2
        fragments: List[DateFragment] = []
        frag = DateFragment()

        start_char, total_chars = 0, 0

        for token in tokens:
            total_chars += len(token[0])

            tok_text, group, tok_capts = token[0], token[1], token[2]
            if not group:
                if frag.indices[1] > 0:
                    if frag.matches_count >= MIN_MATCHES:
                        fragments.append(frag)
                frag = DateFragment()
                start_char = total_chars
                continue

            if group != 'delimiters':
                frag.matches_count += 1
            if frag.indices[1] == 0:
                frag.indices = (start_char, total_chars)
            else:
                frag.indices = (frag.indices[0], total_chars)  # -1

            frag.match_str += tok_text

            for capt in tok_capts:
                if capt in frag.captures:
                    frag.captures[capt] += tok_capts[capt]
                else:
                    frag.captures[capt] = tok_capts[capt]

            start_char = total_chars

        if frag.matches_count >= MIN_MATCHES:  # frag.matches
            fragments.append(frag)

        for frag in fragments:
            for gr in self.ALL_GROUPS:
                if gr not in frag.captures:
                    frag.captures[gr] = []

        return fragments

    @staticmethod
    def get_token_group(captures: Dict[str, List[str]]) -> str:
        for gr in DateFinder.ALL_GROUPS:
            lst = captures.get(gr)
            if lst and len(lst) > 0:
                return gr
        return ''

    def extract_date_strings(self, text: str, strict=False):
        return self.extract_date_strings_inner(text, text_start=0, strict=strict)

    def extract_date_strings_inner(self, text: str, text_start: int = 0, strict=False):
        rng = self.split_date_range(text)
        if rng and len(rng) > 1:
            range_strings = []
            for range_str in rng:
                range_strings.extend(self.extract_date_strings_inner(range_str[0],
                                                                     range_str[1][0],
                                                                     strict=strict))
            for range_string in range_strings:
                yield range_string
            return

        tokens = self.tokenize_string(text)
        items = self.merge_tokens(tokens)

        for match in items:
            match_str = match.match_str
            indices = (match.indices[0] + text_start, match.indices[1] + text_start)

            ## Get individual group matches
            captures = match.captures
            #time = captures.get('time')
            digits = captures.get('digits')
            #digits_modifiers = captures.get('digits_modifiers')
            #days = captures.get('days')
            months = captures.get('months')
            #timezones = captures.get('timezones')
            delimiters = captures.get('delimiters')
            #time_periods = captures.get('time_periods')
            #extra_tokens = captures.get('extra_tokens')

            if delimiters and match_str.endswith(delimiters[-1]):
                captures['delimiters'] = captures['delimiters'][:-1]

            if strict:
                complete = False
                ## 12-05-2015
                if len(digits) == 3:
                    complete = True
                    ## 19 February 2013 year 09:10
                elif (len(months) == 1) and (len(digits) == 2):
                    complete = True

                if not complete:
                    continue

            ## sanitize date string
            ## replace unhelpful blank space characters with single blank space

            match_str = re.sub(r'[\n\t\s\xa0]+', ' ', match_str)
            match_str, indices = self.strip_string_entry(match_str, indices, self.STRIP_CHARS)
            match_str = match_str.strip(self.STRIP_CHARS)

            ## Save sanitized source string
            yield match_str, indices, captures

    @classmethod
    def strip_string_entry(cls,
                           text: str,
                           text_coords: Tuple[int, int],
                           strip_chars: Optional[str] = None) -> Tuple[str, Tuple[int, int]]:
        ln = len(text)
        text = text.rstrip(strip_chars)
        text_coords = (text_coords[0], text_coords[1] - ln + len(text),)

        ln = len(text)
        text = text.lstrip(strip_chars)
        text_coords = (text_coords[0] + ln - len(text), text_coords[1],)
        return text, text_coords

    @staticmethod
    def split_date_range(text: str) -> List[Tuple[str, Tuple[int, int]]]:
        st_matches = DateFinder.RANGE_SPLIT_REGEX.finditer(text)
        start = 0
        parts = []  # List[Tuple[str, Tuple[int, int]]]

        for match in st_matches:
            match_start = match.start()
            if match_start > start:
                parts.append((text[start:match_start], (start, match_start)))
            start = match.end()

        if start < len(text):
            parts.append((text[start:], (start, len(text))))

        return parts

    def find_dates(self, text, source=False, index=False, strict=False):

        for date_string, indices, captures in self.extract_date_strings(text, strict=strict):

            as_dt = self.parse_date_string(date_string, captures)
            if as_dt is None:
                ## Dateutil couldn't make heads or tails of it
                ## move on to next
                continue

            returnables = (as_dt,)
            if source:
                returnables = returnables + (date_string,)
            if index:
                returnables = returnables + (indices,)

            if len(returnables) == 1:
                returnables = returnables[0]
            yield returnables

    def parse_date_string(self,
                          date_string: str,
                          captures: Dict[str, List],
                          locale: Locale):
        # For well formatted string, we can already let dateparser parse them
        # otherwise self._find_and_replace method might corrupt them
        was_raised_error = False
        as_dt = None

        if not locale:
            try:
                as_dt = dateparser.parse(date_string,
                                         settings={'RELATIVE_BASE': self.base_date})
                # Dateparser has issues with time when parsing something like `29MAY19 1350`
                as_dateutil = parser.parse(date_string, default=self.base_date)
                if as_dt != as_dateutil:
                    as_dt = as_dateutil
            except ValueError:
                was_raised_error = True
        else:
            try:
                as_dt = dateparser.parse(date_string,
                                         settings={'RELATIVE_BASE': self.base_date},
                                         locales=[locale.get_locale()])
            except ValueError:
                was_raised_error = True

        # Try to parse date using only language
        if was_raised_error:
            try:
                as_dt = dateparser.parse(date_string,
                                         settings={'RELATIVE_BASE': self.base_date},
                                         languages=[locale.language])
                was_raised_error = False
            except ValueError:
                pass

        if was_raised_error:
            # replace tokens that are problematic for dateutil
            date_string, tz_string = self._find_and_replace(date_string, captures)

            # One last sweep after removing
            date_string = date_string.strip(self.STRIP_CHARS)
            # Match strings must be at least 3 characters long
            # < 3 tends to be garbage
            if len(date_string) < 3:
                return None

            try:
                debug_msg = 'Parsing {} with dateutil'.format(date_string)
                logger.debug(debug_msg)
                as_dt = parser.parse(date_string, default=self.base_date)
            except Exception as e:  # pylint: disable=broad-except
                logger.debug(e)
                as_dt = None
            if tz_string:
                as_dt = self._add_tzinfo(as_dt, tz_string)
        return as_dt

    def _add_tzinfo(self, datetime_obj, tz_string):
        """
        take a naive datetime and add dateutil.tz.tzinfo object

        :param datetime_obj: naive datetime object
        :return: datetime object with tzinfo
        """
        if datetime_obj is None:
            return None

        tzinfo_match = tz.gettz(tz_string)
        return datetime_obj.replace(tzinfo=tzinfo_match)

    def _find_and_replace(self, date_string, captures):
        """
        :warning: when multiple tz matches exist the last sorted capture will trump
        :param date_string:
        :return: date_string, tz_string
        """
        # add timezones to replace
        cloned_replacements = copy.copy(self.REPLACEMENTS)  # don't mutate
        for tz_string in captures.get('timezones', []):
            cloned_replacements.update({tz_string: ' '})

        date_string = date_string.lower()
        for key, replacement in cloned_replacements.items():
            # we really want to match all permutations of the key surrounded by blank space chars except one
            # for example: consider the key = 'to'
            # 1. match 'to '
            # 2. match ' to'
            # 3. match ' to '
            # but never match r'(\s|)to(\s|)' which would make 'october' > 'ocber'
            date_string = re.sub(r'(^|\s)' + key + r'(\s|$)', replacement, date_string, flags=re.IGNORECASE)

        return date_string, self._pop_tz_string(sorted(captures.get('timezones', [])))

    def _pop_tz_string(self, list_of_timezones):
        try:
            tz_string = list_of_timezones.pop()
            # make sure it's not a timezone we
            # want replaced with better abbreviation
            return self.TIMEZONE_REPLACEMENTS.get(tz_string, tz_string)
        except IndexError:
            return ''


def find_dates(
        text,
        source=False,
        index=False,
        strict=False,
        base_date=None
):
    """
    Extract datetime strings from text

    :param text:
        A string that contains one or more natural language or literal
        datetime strings
    :type text: str|unicode
    :param source:
        Return the original string segment
    :type source: boolean
    :param index:
        Return the indices where the datetime string was located in text
    :type index: boolean
    :param strict:
        Only return datetimes with complete date information. For example:
        `July 2016` of `Monday` will not return datetimes.
        `May 16, 2015` will return datetimes.
    :type strict: boolean
    :param base_date:
        Set a default base datetime when parsing incomplete dates
    :type base_date: datetime

    :return: Returns a generator that produces :mod:`datetime.datetime` objects,
        or a tuple with the source text and index, if requested
    """
    date_finder = DateFinder(base_date=base_date)
    return date_finder.find_dates(text, source=source, index=index, strict=strict)
