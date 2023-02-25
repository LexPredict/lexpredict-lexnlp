__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import os
from unittest import TestCase

from lexnlp.extract.ml.en.definitions.layered_definition_detector import LayeredDefinitionDetector
from lexnlp.extract.ml.environment import ENV_EN_DATA_DIRECTORY
from lexnlp.extract.common.base_path import lexnlp_test_path


TRAINED_MODEL_PATH = os.path.join(ENV_EN_DATA_DIRECTORY, 'definition_model_layered.pickle.gzip')


class TestLayeredDefinitionDetector(TestCase):
    def non_test_train(self):
        # indended to be run by user
        model = LayeredDefinitionDetector()
        train_file = os.path.join(f'{lexnlp_test_path}/lexnlp/ml/en',
                                  'layered_definitions_train_data.jsonl')
        model.train_on_doccano_jsonl(TRAINED_MODEL_PATH, train_file)

    def test_parse_trivial(self):
        model = LayeredDefinitionDetector()
        model.load_compressed(TRAINED_MODEL_PATH)
        text = """
                The Trustee shall establish, 
                maintain and hold in trust a separate fund designated as the "Redemption Fund", shall establish and 
                maintain within the Redemption Fund a separate Optional Redemption Account and a separate Special 
                Redemption Account and shall accept moneys deposited for redemption and shall deposit such moneys 
                into said Accounts, as applicable.
                """
        ants = model.get_annotations(text)
        self.assertGreater(len(ants), 0)
        ant_def = text[ants[0].coords[0]: ants[0].coords[1]]
        self.assertGreater(len(ant_def), 0)
