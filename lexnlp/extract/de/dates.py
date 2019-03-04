from lexnlp.extract.common.dates import DateParser


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


parser = DateParser(enable_classifier_check=False, language='de')
get_dates = parser.get_dates
get_date_list = parser.get_date_list
