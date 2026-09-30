__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from unittest.mock import patch

from lexnlp.extract.common.annotations.address_annotation import AddressAnnotation
from lexnlp.extract.en.addresses.addresses import (
    _safe_index,
    get_address_annotations,
    get_address_spans,
)
from lexnlp.tests import lexnlp_tests


def test_get_address():
    lexnlp_tests.test_extraction_func_on_test_data(func=get_address_spans,
                                                   actual_data_converter=lambda spans: [span[0] for span in spans])


def test_safe_index():
    actual = _safe_index('hello world', 'world', 1)
    assert actual == 6


def test_safe_index_not_found():
    try:
        _safe_index('hello world', 'world', 7)
        raise AssertionError('Should raise ValueError before this line')
    except ValueError as e:
        assert 'start' in str(e)


def test_address_annotation_constructor_and_source_span():
    text = 'Send notice to 10 Main Street, London promptly.'
    start = text.index('10 Main Street')
    end = start + len('10 Main Street, London')

    with patch(
        'lexnlp.extract.en.addresses.addresses.get_address_spans',
        return_value=[('10 Main Street, London', start, end)],
    ):
        annotations = list(get_address_annotations(text))

    assert len(annotations) == 1
    annotation = annotations[0]
    assert isinstance(annotation, AddressAnnotation)
    assert annotation.coords == (start, end)
    assert annotation.text == text[start:end]
    assert annotation.to_dictionary()['tags']['Extracted Entity Text'] == text[start:end]

# def test_bad_cases():
#    lexnlp_tests.test_extraction_func_on_test_data(get_addresses)
