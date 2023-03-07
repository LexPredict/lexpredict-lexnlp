__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import Callable, Dict, Set, List, Any, Tuple
from enum import Enum

from lexnlp.extract.common.annotation_type import AnnotationType
from lexnlp.extract.en.acts import get_acts_annotations, get_acts
from lexnlp.extract.en.amounts import get_amounts, get_amount_annotations
from lexnlp.extract.en.citations import get_citation_annotations, get_citations
from lexnlp.extract.en.conditions import get_condition_annotations, get_conditions
from lexnlp.extract.en.constraints import get_constraint_annotations, get_constraints
from lexnlp.extract.en.copyright import get_copyright_annotations, get_copyrights
from lexnlp.extract.en.courts import get_court_annotations, get_courts
from lexnlp.extract.en.cusip import get_cusip_annotations, get_cusip
from lexnlp.extract.en.dates import get_date_annotations, get_dates
from lexnlp.extract.en.definitions import get_definition_annotations, get_definitions
from lexnlp.extract.en.distances import get_distance_annotations, get_distances
from lexnlp.extract.en.durations import get_duration_annotations, get_durations
from lexnlp.extract.en.geoentities import get_geoentity_annotations, get_geoentities
from lexnlp.extract.en.money import get_money_annotations, get_money
from lexnlp.extract.en.percents import get_percent_annotations, get_percents
from lexnlp.extract.en.pii import get_pii_annotations, get_pii, get_us_phone_annotations, \
    get_us_phones, get_ssn_annotations, get_ssns
from lexnlp.extract.en.ratios import get_ratio_annotations, get_ratios
from lexnlp.extract.en.regulations import get_regulation_annotations, get_regulations
from lexnlp.extract.en.trademarks import get_trademark_annotations, get_trademarks
from lexnlp.extract.en.urls import get_url_annotations, get_urls

from lexnlp.extract.de.amounts import get_amount_annotations as get_de_amount_annotations
from lexnlp.extract.de.amounts import get_amounts as get_de_amounts
from lexnlp.extract.de.citations import get_citation_annotations as get_de_citation_annotations
from lexnlp.extract.de.citations import get_citations as get_de_citations
from lexnlp.extract.de.copyrights import get_copyright_annotations as get_de_copyright_annotations
from lexnlp.extract.de.copyrights import get_copyrights as get_de_copyrights
from lexnlp.extract.de.court_citations import get_court_citation_annotations as get_de_court_citation_annotations
from lexnlp.extract.de.court_citations import get_court_citations as get_de_court_citations
from lexnlp.extract.de.courts import get_court_annotations as get_de_court_annotations
from lexnlp.extract.de.courts import get_courts as get_de_courts
from lexnlp.extract.de.dates import get_date_annotations as get_de_date_annotations
from lexnlp.extract.de.dates import get_dates as get_de_dates
from lexnlp.extract.de.definitions import get_definition_annotations as get_de_definition_annotations
from lexnlp.extract.de.definitions import get_definitions as get_de_definitions
from lexnlp.extract.de.durations import get_duration_annotations as get_de_duration_annotations
from lexnlp.extract.de.durations import get_durations as get_de_durations
from lexnlp.extract.de.geoentities import get_geoentity_annotations as get_de_geoentity_annotations, \
    get_geoentities as get_de_geoentities
from lexnlp.extract.de.laws import get_law_annotations as get_de_law_annotations
from lexnlp.extract.de.laws import get_laws as get_de_laws
from lexnlp.extract.de.percents import get_percent_annotations as get_de_percent_annotations
from lexnlp.extract.de.percents import get_percents as get_de_percents

from lexnlp.extract.es.copyrights import get_copyright_annotations as get_es_copyright_annotations
from lexnlp.extract.es.copyrights import get_copyrights as get_es_copyrights
from lexnlp.extract.es.courts import get_court_annotations as get_es_court_annotations
from lexnlp.extract.es.courts import get_courts as get_es_courts
from lexnlp.extract.es.dates import get_date_annotations as get_es_date_annotations
from lexnlp.extract.es.dates import get_dates as get_es_dates
from lexnlp.extract.es.definitions import get_definition_annotations as get_es_definition_annotations
from lexnlp.extract.es.definitions import get_definitions as get_es_definitions
from lexnlp.extract.es.regulations import get_regulation_annotations as get_es_regulation_annotations
from lexnlp.extract.es.regulations import get_regulations as get_es_regulations


class ExtractorResultFormat(Enum):
    """
    What output format we expect:
    - fmt_class produces collections of classes, derived from TextAnnotation
    - fmt_dict collects TextAnnotations, then makes dictionaries of them
      ({ 'attrs': { 'start': 105, 'end': 119 }, 'tags': ... })
    - fmt_object gives tuples or other "legacy" formats
    """
    fmt_class = 1
    fmt_dict = 2
    fmt_object = 3


class ExtractingFunction:
    def __init__(self,
                 method: Callable,
                 fact_type: AnnotationType = None,
                 lang: str = '',
                 result_fmt: ExtractorResultFormat = None):
        self.method = method  # <get_acts_annotations>
        self.fact_type = fact_type  # act
        self.language = lang  # "en"
        self.result_fmt = result_fmt  # fmt_class


class FactExtractor:
    """
    Takes text and language.
    Returns collection of entities (acts, amounts, geoentities etc)
    in desired (ExtractorResultFormat) format.

    Some parsers require additional arguments - for example, geolocation lists
    for EN and DE geoentities parsers. Provide these arguments in
    ensure_parser_arguments_en and ensure_parser_arguments_de.
    """

    ALL_ANT_TYPES = set(AnnotationType)
    LANGUAGE_EN = 'en'
    LANGUAGE_DE = 'de'
    LANGUAGE_ES = 'es'
    # { "en": { "class": { "amount": <routine>, ...
    func_by_lang = {}  # type:Dict[str, Dict[ExtractorResultFormat, Dict[AnnotationType, ExtractingFunction]]]

    parser_extra_arguments = {}  # type:Dict[str, Dict[ExtractorResultFormat, Dict[AnnotationType, Tuple]]]

    @staticmethod
    def parse_text(text: str,
                   lang: str,
                   result_fmt: ExtractorResultFormat = ExtractorResultFormat.fmt_class,
                   extract_all: bool = True,
                   include_types: Set[AnnotationType] = None,
                   exclude_types: Set[AnnotationType] = None) -> Dict[AnnotationType, List[Any]]:
        if lang not in FactExtractor.func_by_lang:
            langs = ', '.join(FactExtractor.func_by_lang)
            raise Exception(f'Language "{lang}" was not found among {langs}')
        lang_extractors = FactExtractor.func_by_lang[lang]
        result_fmt_key = ExtractorResultFormat.fmt_class \
            if result_fmt == ExtractorResultFormat.fmt_dict else result_fmt

        if result_fmt_key not in lang_extractors:
            raise Exception(f'Format "{result_fmt_key.name}" is not supported for {lang}')
        extractors = lang_extractors[result_fmt_key]

        target_types = set()  # type:  Set[AnnotationType]

        if not extract_all and not include_types:
            return {}
        if not extract_all and include_types:
            target_types = include_types
        elif extract_all:
            target_types = FactExtractor.ALL_ANT_TYPES
            if exclude_types:
                target_types -= exclude_types

        if not target_types:
            return {}
        extractors = [extractors.get(t) for t in target_types]
        extractors = [e for e in extractors if e]  # type: List[ExtractingFunction]

        extra_args = FactExtractor.parser_extra_arguments.get(lang)
        if extra_args:
            extra_args = extra_args.get(result_fmt)
        extra_args = extra_args or {}  # type: Dict[AnnotationType, Tuple]

        facts = {}  # type: Dict[AnnotationType, List[Any]]
        for extractor in extractors:
            extras = extra_args.get(extractor.fact_type)
            func_args = (text,) + extras if extras else (text,)
            typed_facts = list(extractor.method(*func_args))
            if not typed_facts:
                continue
            if result_fmt == ExtractorResultFormat.fmt_dict:
                typed_facts = [f.to_dictionary() for f in typed_facts]
            facts[extractor.fact_type] = typed_facts

        return facts

    @staticmethod
    def ensure_parser_arguments_en(
            geo_config: List[Any] = None) -> None:
        for fmt in ExtractorResultFormat:
            FactExtractor.ensure_parser_arguments(FactExtractor.LANGUAGE_EN,
                                                  fmt,
                                                  AnnotationType.geoentity,
                                                  (geo_config,))

    @staticmethod
    def ensure_parser_arguments_de(
            geo_config: List[Any] = None) -> None:
        for fmt in ExtractorResultFormat:
            FactExtractor.ensure_parser_arguments(FactExtractor.LANGUAGE_DE,
                                                  fmt,
                                                  AnnotationType.geoentity,
                                                  (geo_config,))

    @staticmethod
    def initialize():
        FactExtractor.initialize_en()
        FactExtractor.initialize_de()
        FactExtractor.initialize_es()

    @staticmethod
    def ensure_parser_arguments(lang: str,
                                result_fmt: ExtractorResultFormat,
                                ant_type: AnnotationType,
                                func_args: Tuple) -> None:
        lang_args = FactExtractor.parser_extra_arguments.get(lang)
        if not lang_args:
            lang_args = {}
            FactExtractor.parser_extra_arguments[lang] = lang_args

        fmt_args = lang_args.get(result_fmt)
        if not fmt_args:
            fmt_args = {}
            lang_args[result_fmt] = fmt_args

        fmt_args[ant_type] = func_args

    @staticmethod
    def initialize_en():
        all_functs = [
            ExtractingFunction(method=get_acts_annotations, fact_type=AnnotationType.act,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_acts, fact_type=AnnotationType.act,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_amount_annotations, fact_type=AnnotationType.amount,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_amounts, fact_type=AnnotationType.amount,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_citation_annotations, fact_type=AnnotationType.citation,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_citations, fact_type=AnnotationType.citation,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_condition_annotations, fact_type=AnnotationType.condition,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_conditions, fact_type=AnnotationType.condition,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_constraint_annotations, fact_type=AnnotationType.constraint,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_constraints, fact_type=AnnotationType.constraint,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_copyright_annotations, fact_type=AnnotationType.copyright,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_copyrights, fact_type=AnnotationType.copyright,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_court_annotations, fact_type=AnnotationType.court,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_courts, fact_type=AnnotationType.court,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_cusip_annotations, fact_type=AnnotationType.cusip,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_cusip, fact_type=AnnotationType.cusip,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_date_annotations, fact_type=AnnotationType.date,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_dates, fact_type=AnnotationType.date,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_definition_annotations, fact_type=AnnotationType.definition,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_definitions, fact_type=AnnotationType.definition,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_distance_annotations, fact_type=AnnotationType.distance,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_distances, fact_type=AnnotationType.distance,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_duration_annotations, fact_type=AnnotationType.duration,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_durations, fact_type=AnnotationType.duration,
                               result_fmt=ExtractorResultFormat.fmt_object),

            # SIC! dictionary is required
            ExtractingFunction(method=get_geoentity_annotations, fact_type=AnnotationType.geoentity,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_geoentities, fact_type=AnnotationType.geoentity,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_money_annotations, fact_type=AnnotationType.money,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_money, fact_type=AnnotationType.money,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_percent_annotations, fact_type=AnnotationType.percent,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_percents, fact_type=AnnotationType.percent,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_pii_annotations, fact_type=AnnotationType.pii,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_pii, fact_type=AnnotationType.pii,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_us_phone_annotations, fact_type=AnnotationType.phone,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_us_phones, fact_type=AnnotationType.phone,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_ssn_annotations, fact_type=AnnotationType.ssn,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_ssns, fact_type=AnnotationType.ssn,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_ratio_annotations, fact_type=AnnotationType.ratio,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_ratios, fact_type=AnnotationType.ratio,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_regulation_annotations, fact_type=AnnotationType.regulation,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_regulations, fact_type=AnnotationType.regulation,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_trademark_annotations, fact_type=AnnotationType.trademark,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_trademarks, fact_type=AnnotationType.trademark,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_url_annotations, fact_type=AnnotationType.url,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_urls, fact_type=AnnotationType.url,
                               result_fmt=ExtractorResultFormat.fmt_object),
        ]
        FactExtractor.store_functions(all_functs, FactExtractor.LANGUAGE_EN)

    @staticmethod
    def initialize_de():
        all_functs = [
            ExtractingFunction(method=get_de_amount_annotations, fact_type=AnnotationType.amount,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_de_amounts, fact_type=AnnotationType.amount,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_de_citation_annotations, fact_type=AnnotationType.citation,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_de_citations, fact_type=AnnotationType.citation,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_de_copyright_annotations, fact_type=AnnotationType.copyright,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_de_copyrights, fact_type=AnnotationType.copyright,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_de_court_citation_annotations, fact_type=AnnotationType.court_citation,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_de_court_citations, fact_type=AnnotationType.court_citation,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_de_court_annotations, fact_type=AnnotationType.court,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_de_courts, fact_type=AnnotationType.court,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_de_date_annotations, fact_type=AnnotationType.date,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_de_dates, fact_type=AnnotationType.date,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_de_definition_annotations, fact_type=AnnotationType.definition,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_de_definitions, fact_type=AnnotationType.definition,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_de_duration_annotations, fact_type=AnnotationType.duration,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_de_durations, fact_type=AnnotationType.duration,
                               result_fmt=ExtractorResultFormat.fmt_object),

            # SIC! dictionary is required
            ExtractingFunction(method=get_de_geoentity_annotations, fact_type=AnnotationType.geoentity,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_de_geoentities, fact_type=AnnotationType.geoentity,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_de_law_annotations, fact_type=AnnotationType.laws,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_de_laws, fact_type=AnnotationType.laws,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_de_percent_annotations, fact_type=AnnotationType.percent,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_de_percents, fact_type=AnnotationType.percent,
                               result_fmt=ExtractorResultFormat.fmt_object),
        ]
        FactExtractor.store_functions(all_functs, FactExtractor.LANGUAGE_DE)

    @staticmethod
    def initialize_es():
        all_functs = [
            ExtractingFunction(method=get_es_copyright_annotations, fact_type=AnnotationType.copyright,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_es_copyrights, fact_type=AnnotationType.copyright,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_es_court_annotations, fact_type=AnnotationType.court,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_es_courts, fact_type=AnnotationType.court,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_es_date_annotations, fact_type=AnnotationType.date,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_es_dates, fact_type=AnnotationType.date,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_es_definition_annotations, fact_type=AnnotationType.definition,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_es_definitions, fact_type=AnnotationType.definition,
                               result_fmt=ExtractorResultFormat.fmt_object),

            ExtractingFunction(method=get_es_regulation_annotations, fact_type=AnnotationType.regulation,
                               result_fmt=ExtractorResultFormat.fmt_class),
            ExtractingFunction(method=get_es_regulations, fact_type=AnnotationType.regulation,
                               result_fmt=ExtractorResultFormat.fmt_object),
        ]
        FactExtractor.store_functions(all_functs, FactExtractor.LANGUAGE_ES)

    @staticmethod
    def store_functions(all_functs: List[ExtractingFunction], lang: str):
        func_by_ret_fmt = {}  # { "class": { "amount": <routine>, ...
        for func in all_functs:
            func.lang = lang
            tp_func_dict = func_by_ret_fmt.get(func.result_fmt)
            if not tp_func_dict:
                tp_func_dict = {}
                func_by_ret_fmt[func.result_fmt] = tp_func_dict
            tp_func_dict[func.fact_type] = func

        FactExtractor.func_by_lang[lang] = func_by_ret_fmt


FactExtractor.initialize()
