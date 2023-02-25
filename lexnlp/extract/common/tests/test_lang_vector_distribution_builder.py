__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import os
from tempfile import NamedTemporaryFile
from typing import List
from unittest import TestCase

from lexnlp.extract.common.ocr_rating.lang_vector_distribution_builder import LangVectorDistributionBuilder
from lexnlp.extract.common.ocr_rating.ocr_rating_calculator \
    import CosineSimilarityOcrRatingCalculator


class TestLangVectorDistributionBuilder(TestCase):
    def test_build_from_texts(self):
        sample = 'chi ka nu chi nu kachika kanu unka'
        file_even_dist = NamedTemporaryFile(mode='w', delete=False)
        file_even_dist.writelines(sample * 200)
        file_even_dist.close()

        sample = 'uka'
        file_odd_dist = NamedTemporaryFile(mode='w', delete=False)
        file_odd_dist.writelines(sample * 600)
        file_odd_dist.close()

        bld = LangVectorDistributionBuilder()
        distr = bld.build_files_reference_distribution([file_even_dist.name, file_odd_dist.name])
        os.unlink(file_even_dist.name)
        os.unlink(file_odd_dist.name)

        self.assertIsNotNone(distr)

        # test texts
        calc = CosineSimilarityOcrRatingCalculator()
        calc.distribution_by_lang['chi'] = distr

        sample_text = 'Chika ka nuunchi chi ka' * 5000
        grade = calc.get_rating(sample_text, 'chi')
        self.assertGreater(grade, 5)

    def collect_paths(self, root: str, paths: List[str]):
        for path in os.listdir(root):
            full_path = os.path.join(root, path)
            if path.endswith('.txt'):
                paths.append(full_path)
                continue
            if os.path.isdir(full_path):
                self.collect_paths(full_path, paths)
