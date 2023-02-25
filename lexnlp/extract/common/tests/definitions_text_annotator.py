__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import List
from lexnlp.extract.common.annotations.definition_annotation import DefinitionAnnotation
from lexnlp.tests.utility_for_testing import save_test_document, annotate_text


def annotate_definitions_text(text: str,
                              definitions: List[DefinitionAnnotation],
                              save_path: str) -> None:
    markup = annotate_text(text, definitions)
    save_test_document(save_path, markup)
