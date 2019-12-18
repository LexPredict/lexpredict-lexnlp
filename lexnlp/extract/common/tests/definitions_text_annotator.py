from typing import List
from lexnlp.extract.common.annotations.definition_annotation import DefinitionAnnotation
from lexnlp.tests.utility_for_testing import save_test_document, annotate_text

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def annotate_definitions_text(text: str,
                              definitions: List[DefinitionAnnotation],
                              save_path: str) -> None:
    markup = annotate_text(text, definitions)
    save_test_document(save_path, markup)
