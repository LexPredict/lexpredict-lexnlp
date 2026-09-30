from unittest.mock import patch

from lexnlp.utils.amount_delimiting import infer_delimiters


def test_known_locale_inference_does_not_change_process_locale():
    with patch('lexnlp.utils.amount_delimiting.locale.setlocale') as setlocale:
        delimiters = infer_delimiters('10.800', 'de_DE')

    assert delimiters == {
        'decimal_delimiter': None,
        'group_delimiter': '.',
    }
    setlocale.assert_not_called()


def test_en_us_decimal_and_group_delimiters():
    assert infer_delimiters('1,234.56', 'en_US') == {
        'decimal_delimiter': '.',
        'group_delimiter': ',',
    }
