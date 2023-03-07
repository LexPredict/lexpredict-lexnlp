__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import Generator, List, Tuple

from lexnlp.extract.common.annotation_locator_type import AnnotationLocatorType
from lexnlp.extract.common.annotations.definition_annotation import DefinitionAnnotation
from lexnlp.extract.en.definition_parsing_methods import DefinitionCaught, get_definition_list_in_sentence, \
    filter_definitions_for_self_repeating
from lexnlp.extract.ml.en.definitions.layered_definition_detector import LayeredDefinitionDetector
from lexnlp.nlp.en.segments.sentences import get_sentence_span


def get_definitions_in_sentence(sentence: str,
                                return_sources=False,
                                decode_unicode=True) -> Generator:
    definitions = get_definition_list_in_sentence((0, len(sentence), sentence), decode_unicode)
    for df in definitions:
        if return_sources:
            yield df.name, df.text
        else:
            yield df.name


def get_definition_objects_list(text, decode_unicode=True) -> List[DefinitionCaught]:
    """
    :param text: text to search for definitions
    :param decode_unicode:
    :return: a list of found definitions - objects of class DefinitionCaught
    """
    definitions = []
    for sentence in get_sentence_span(text):  # type: Tuple[int, int, str]
        definitions += get_definition_list_in_sentence(sentence, decode_unicode)
    definitions = filter_definitions_for_self_repeating(definitions)
    return definitions


parser_ml_classifier = LayeredDefinitionDetector()


def get_definition_annotations(text: str,
                               **kwargs) \
        -> Generator[DefinitionAnnotation, None, None]:
    decode_unicode = kwargs.get('decode_unicode', True)
    locator_type = kwargs.get('locator_type', AnnotationLocatorType.RegexpBased)

    if locator_type == AnnotationLocatorType.MlWordVectorBased:
        if not parser_ml_classifier.initialized:
            raise Exception('"parser_ml_classifier" object should be initialized (call load_compressed method)')
        ants = parser_ml_classifier.get_annotations(text)
        for ant in ants:
            yield ant
        return

    # use Regexp-based locator
    for d in get_definition_objects_list(
            text, decode_unicode=decode_unicode):
        ant = DefinitionAnnotation(
            coords=d.coords, text=d.text, name=d.name)
        yield ant


def get_definitions(text: str,
                    return_sources=False,
                    decode_unicode=True,
                    return_coords=False,
                    locator_type: AnnotationLocatorType = AnnotationLocatorType.RegexpBased) -> Generator:
    """
    Find possible definitions in natural language in text.
    The text will be split to sentences first.
    :param return_coords: returns a (x, y) tuple in each record. x - definition's text start, y - definition's text end
    :param decode_unicode:
    :param return_sources: returns a tuple with the extracted term and the source sentence
    :param text: the input text
    :param locator_type: use default (Regexp-based) or ML-based locator
    :return: Generator[name] or Generator[name, text] or Generator[name, text, coords]
    """
    if locator_type == AnnotationLocatorType.MlWordVectorBased:
        if not parser_ml_classifier.initialized:
            raise Exception('"parser_ml_classifier" object should be initialized (call load_compressed method)')
        definitions = parser_ml_classifier.get_annotations(text)
    else:
        definitions = get_definition_objects_list(text, decode_unicode)

    for df in definitions:
        if return_coords:
            yield df.name, df.text, (df.coords[0], df.coords[1])
        elif return_sources:
            yield df.name, df.text
        else:
            yield df.name


def get_definitions_explicit(text,
                             decode_unicode=True,
                             locator_type: AnnotationLocatorType = AnnotationLocatorType.RegexpBased) -> Generator:
    yield from get_definitions(text,
                               return_sources=True,
                               decode_unicode=decode_unicode,
                               return_coords=True,
                               locator_type=locator_type)
