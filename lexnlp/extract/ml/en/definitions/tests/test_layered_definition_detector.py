__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import os
from pathlib import Path
from unittest import TestCase
from zipfile import ZipFile

import pandas
import pytest

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


class RecordingDetector:
    def __init__(self):
        self.payload = None

    def load_from_stream(self, stream):
        self.payload = stream.read()


def test_compressed_model_loads_exact_members_without_extracting_to_disk(
    tmp_path: Path,
):
    archive_path = tmp_path / "definition-model.zip"
    with ZipFile(archive_path, "w") as archive:
        archive.writestr("definition.pickle", b"definition model")
        archive.writestr("term.pickle", b"term model")

    detector = LayeredDefinitionDetector()
    detector.model_definition = RecordingDetector()
    detector.model_term = RecordingDetector()

    detector.load_compressed(str(archive_path))

    assert detector.initialized is True
    assert detector.model_definition.payload == b"definition model"
    assert detector.model_term.payload == b"term model"
    assert sorted(path.name for path in tmp_path.iterdir()) == ["definition-model.zip"]


@pytest.mark.parametrize(
    "members",
    [
        {"definition.pickle": b"definition"},
        {
            "definition.pickle": b"definition",
            "term.pickle": b"term",
            "../outside.pickle": b"unexpected",
        },
        {
            "definition.pickle": b"definition",
            "term.pickle": b"term",
            "notes.txt": b"unexpected",
        },
    ],
)
def test_compressed_model_rejects_missing_or_unexpected_members(
    tmp_path: Path,
    members,
):
    archive_path = tmp_path / "definition-model.zip"
    with ZipFile(archive_path, "w") as archive:
        for name, payload in members.items():
            archive.writestr(name, payload)

    detector = LayeredDefinitionDetector()
    detector.model_definition = RecordingDetector()
    detector.model_term = RecordingDetector()

    with pytest.raises(RuntimeError, match="Invalid layered definition model archive"):
        detector.load_compressed(str(archive_path))

    assert detector.initialized is False
    assert not (tmp_path.parent / "outside.pickle").exists()


class TrainingDetector:
    def __init__(self, payload: bytes):
        self.payload = payload

    def train_and_save_on_dataframe(
        self,
        _settings,
        _frame,
        save_path,
        *,
        compress,
    ):
        assert compress is False
        Path(save_path).write_bytes(self.payload)


def test_training_uses_unique_temporary_directory_and_atomic_archive(
    tmp_path: Path,
):
    destination = tmp_path / "models" / "definition-model.zip"
    detector = LayeredDefinitionDetector()
    detector.model_definition = TrainingDetector(b"definition model")
    detector.model_term = TrainingDetector(b"term model")

    detector.train_on_formatted_data(
        pandas.DataFrame(),
        pandas.DataFrame(),
        str(destination),
    )

    with ZipFile(destination) as archive:
        assert set(archive.namelist()) == {"definition.pickle", "term.pickle"}
        assert archive.read("definition.pickle") == b"definition model"
        assert archive.read("term.pickle") == b"term model"
    assert sorted(path.name for path in destination.parent.iterdir()) == [
        "definition-model.zip"
    ]
