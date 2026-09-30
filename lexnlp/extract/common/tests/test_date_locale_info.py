"""Regional date order must inherit language defaults without losing overrides."""

import pytest

from lexnlp.extract.all_locales.languages import Locale
from lexnlp.extract.common.dates import LocaleInfoImport


@pytest.mark.parametrize('name, expected', [
    ('es-ES', 'DMY'),
    ('es-MX', 'DMY'),
    ('es-PA', 'MDY'),
    ('es-PR', 'MDY'),
    ('de-AT', 'DMY'),
    ('xx-XX', 'MDY'),
])
def test_regional_date_order_inheritance(name, expected):
    assert LocaleInfoImport(Locale(name)).date_order == expected
