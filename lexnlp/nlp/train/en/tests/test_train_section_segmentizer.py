__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from shutil import copyfile
import tempfile
from unittest import TestCase
import os

import joblib

from lexnlp import get_module_path
from lexnlp.nlp.en.segments.sections import get_section_spans, SectionSegmenterModel
from lexnlp.nlp.train.en.train_section_segmanizer import SectionSegmentizerTrainManager


class TestTrainSectionSegmentizer(TestCase):
    def train_and_dump(self):
        trainer = SectionSegmentizerTrainManager()
        trainer.build_features(
            'contraxsuite/lexpredict-contraxsuite-samples/',
            'train_documents')
        model = trainer.train_decision_tree()
        trainer.dump_model_on_project_level(model)

    def find_closest_model(self):
        from lexnlp.nlp.en.segments.sections import MODULE_PATH as SECTIONS_MODULE_PATH
        target_path = os.path.join(SECTIONS_MODULE_PATH, 'section_segmenter.pickle')

        iterations = 25
        error, new_error = self.get_error(), 0
        initial_error = error
        print(f'Initial square error: {error}')

        tmpdir = tempfile.gettempdir()
        dump_model_path = os.path.join(tmpdir, 'model_dump.pickle')
        copyfile(target_path, dump_model_path)
        for _ in range(iterations):
            self.train_and_dump()
            SectionSegmenterModel.SECTION_SEGMENTER_MODEL = joblib.load(target_path)

            new_error = self.get_error()
            if new_error < error:
                print(f'Error dropped from {error} to {new_error}')
                copyfile(target_path, dump_model_path)
                error = new_error

        print(f'After {iterations} iterations error has changed from {initial_error} to {error}')
        copyfile(dump_model_path, target_path)

    def get_error(self):
        file_count = {
            '1582586_2015-08-31': 23,
            'test_get_section_spans_1.txt': 207
        }
        sum_delta = 0
        for file in file_count:
            text = self.get_text(file)
            count = len(list(get_section_spans(text, use_ml=True)))
            delta = (count - file_count[file]) / file_count[file]
            sum_delta += delta * delta
        return sum_delta

    @staticmethod
    def get_text(path):
        base_path = get_module_path()
        with open(os.path.join(base_path, "../test_data", path), "rb") as f:
            return f.read().decode("utf-8")
