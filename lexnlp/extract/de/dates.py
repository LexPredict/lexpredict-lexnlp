from lexnlp.extract.common.dates import DateParser

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


parser = DateParser(enable_classifier_check=False, language='de',
                    dateparser_settings={'PREFER_DAY_OF_MONTH': 'first',
                                         'STRICT_PARSING': False,
                                         'DATE_ORDER': 'DMY'})

get_date_annotations = parser.get_date_annotations

get_dates = parser.get_dates

get_date_list = parser.get_date_list
