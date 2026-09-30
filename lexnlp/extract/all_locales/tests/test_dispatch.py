from datetime import datetime
from unittest.mock import patch

import pytest

from lexnlp.extract.all_locales import amounts, court_citations, dates
from lexnlp.extract.all_locales.languages import Locale


def test_german_amount_dispatch_uses_named_arguments_in_the_right_order():
    calls = []

    def parse_amounts(*, text, float_digits, return_sources):
        calls.append((text, float_digits, return_sources))
        yield 'amount'

    with patch.dict(amounts.ROUTINE_BY_LOCALE, {'de': parse_amounts}):
        result = list(
            amounts.get_amount_annotations(
                'de-DE',
                'zehn',
                extended_sources=False,
                float_digits=2,
            )
        )

    assert result == ['amount']
    assert calls == [('zehn', 2, False)]


def test_german_date_dispatch_uses_the_supported_signature():
    calls = []
    base_date = datetime(2026, 7, 29)

    def parse_dates(*, text, strict, locale, base_date, threshold):
        calls.append((text, strict, locale, base_date, threshold))
        yield 'date'

    with patch.dict(dates.ROUTINE_BY_LOCALE, {'de': parse_dates}):
        result = list(
            dates.get_date_annotations(
                'de-DE',
                '29. Juli 2026',
                strict=False,
                base_date=base_date,
                threshold=0.75,
            )
        )

    assert result == ['date']
    assert calls[0][:2] == ('29. Juli 2026', False)
    assert isinstance(calls[0][2], Locale)
    assert calls[0][2].get_locale() == 'de-DE'
    assert calls[0][3:] == (base_date, 0.75)


def test_german_date_dispatch_runs_with_default_options():
    text = '5. Oktober 2011'
    annotations = list(dates.get_date_annotations('de-DE', text))

    assert len(annotations) == 1
    assert annotations[0].coords == (0, len(text))
    assert annotations[0].text == text


@pytest.mark.parametrize('locale', ['es', 'es-ES', 'es-MX'])
def test_spanish_date_dispatch_preserves_date_text_and_source_offsets(locale):
    text = 'La fecha es 1 de enero de 2020.'
    annotations = list(dates.get_date_annotations(locale, text))

    assert len(annotations) == 1
    annotation = annotations[0]
    assert annotation.date == datetime(2020, 1, 1)
    assert text[slice(*annotation.coords)] == annotation.text == '1 de enero de 2020'
    assert annotation.locale == 'es'


def test_spanish_date_dispatch_uses_the_requested_base_date_without_leaking_state():
    text = 'La fecha es 15 de febrero.'
    years = []
    for year in (2024, 2030, 2024):
        annotations = list(dates.get_date_annotations(
            'es-ES', text, strict=False, base_date=datetime(year, 6, 1),
        ))
        assert len(annotations) == 1
        years.append(annotations[0].date.year)
    assert years == [2024, 2030, 2024]


def test_spanish_date_dispatch_honors_strict_parsing():
    assert list(dates.get_date_annotations(
        'es-ES', 'La fecha es 15 de febrero.', strict=True,
        base_date=datetime(2024, 6, 1),
    )) == []


@pytest.mark.parametrize('separator', ['\n', '\r\n', '\t', '  '])
def test_spanish_date_annotations_keep_original_whitespace(separator):
    text = f'La fecha es 1 de{separator}enero de 2020.'
    annotations = list(dates.get_date_annotations('es-MX', text))
    assert len(annotations) == 1
    annotation = annotations[0]
    assert annotation.date == datetime(2020, 1, 1)
    assert annotation.text == text[slice(*annotation.coords)]
    assert separator in annotation.text


def test_spanish_repeated_dates_keep_each_original_span():
    text = '1 de\r\nenero de 2020 y 1 de\tenero de 2020.'
    annotations = sorted(dates.get_date_annotations('es-ES', text), key=lambda item: item.coords)
    assert [(item.text, item.date) for item in annotations] == [
        ('1 de\r\nenero de 2020', datetime(2020, 1, 1)),
        ('1 de\tenero de 2020', datetime(2020, 1, 1)),
    ]
    assert all(text[slice(*item.coords)] == item.text for item in annotations)


def test_date_fallback_passes_the_original_string_locale_to_english():
    calls = []

    def parse_dates(**kwargs):
        calls.append(kwargs)
        yield 'date'

    with patch.dict(dates.ROUTINE_BY_LOCALE, {'en': parse_dates}, clear=True):
        assert list(dates.get_date_annotations('de-DE', 'January 1, 2020')) == ['date']
    assert calls[0]['locale'] == 'de-DE'


def test_all_locale_entry_point_preserves_english_fallback():
    calls = []

    def parse_amounts(*, text, extended_sources, float_digits):
        calls.append((text, extended_sources, float_digits))
        yield 'amount'

    with patch.dict(
        amounts.ROUTINE_BY_LOCALE,
        {'en': parse_amounts},
        clear=True,
    ):
        result = list(
            amounts.get_amount_annotations(
                'fr-FR',
                'dix',
                extended_sources=False,
                float_digits=2,
            )
        )

    assert result == ['amount']
    assert calls == [('dix', False, 2)]


def test_court_citation_dispatch_defaults_language_from_locale():
    calls = []

    def parse_citations(text, language):
        calls.append((text, language))
        yield 'citation'

    with patch.dict(
        court_citations.ROUTINE_BY_LOCALE,
        {'de': parse_citations},
    ):
        result = list(
            court_citations.get_court_citation_annotations('de-DE', 'BStBl')
        )

    assert result == ['citation']
    assert calls == [('BStBl', 'de')]


def test_court_citation_dispatch_preserves_german_fallback():
    calls = []

    def parse_citations(text, language):
        calls.append((text, language))
        yield 'citation'

    with patch.dict(
        court_citations.ROUTINE_BY_LOCALE,
        {'de': parse_citations},
        clear=True,
    ):
        result = list(
            court_citations.get_court_citation_annotations('fr-FR', 'BStBl')
        )

    assert result == ['citation']
    assert calls == [('BStBl', 'de')]
