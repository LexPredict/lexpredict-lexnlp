__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import codecs
import os
import shutil

import pandas
from typing import Tuple, List
from zipfile import ZipFile

from lexnlp.extract.common.annotations.definition_annotation import DefinitionAnnotation
from lexnlp.extract.ml.detector.detecting_settings import DetectingSettings
from lexnlp.extract.ml.detector.phrase_constructor import PhraseConstructorSettings, PhraseConstructorMethod
from lexnlp.extract.ml.en.definitions.definition_phrase_detector import DefinitionPhraseDetector
from lexnlp.extract.ml.en.definitions.definition_term_detector import DefinitionTermDetector


class LayeredDefinitionDetector:
    def __init__(self):
        # let the prase be <agrees to serve the Company in such capacity during the
        # term of employment (the "Employment Period”).

        # ... model_definition will find <term of employment (the "Employment Period”)>
        self.model_definition = DefinitionPhraseDetector()
        # ... model_term will find
        self.model_term = DefinitionTermDetector()

        self.definition_join_sets = PhraseConstructorSettings(
            method=PhraseConstructorMethod.by_score, min_token_score=2, max_zeros=0)
        self.term_join_sets = PhraseConstructorSettings(
            method=PhraseConstructorMethod.by_class, strict=False)
        self.initialized = False

    def load_compressed(self, file_path: str):
        """
        Loads archive with two model pickle files (model_definition,
        model_term)
        """
        file_folder = os.path.dirname(file_path)
        temp_folder = os.path.join(file_folder, 'unpack_def_model_temp')
        try:
            shutil.rmtree(temp_folder)
        # pylint: disable=bare-except
        except:
            pass
        os.mkdir(temp_folder)

        with ZipFile(file_path) as z:
            z.extractall(temp_folder)

        model_files = [i for i in os.listdir(temp_folder) if i.endswith('.pickle')]
        for file_name in model_files:
            if file_name == 'definition.pickle':
                self.model_definition.load(os.path.join(temp_folder, file_name))
            elif file_name == 'term.pickle':
                self.model_term.load(os.path.join(temp_folder, file_name))
            else:
                raise RuntimeError(f'Found unknown file "{file_name.filename}" in packed model')
        shutil.rmtree(temp_folder)
        self.initialized = True

    def get_annotations(self, sentence: str) -> List[DefinitionAnnotation]:
        annotations = []  # type: List[DefinitionAnnotation]
        # we go from term to definition because term is a simplier object to locate
        terms = list(self.model_term.predict_text(
                sentence, join_settings=self.term_join_sets))
        if not terms:
            return annotations

        # find definitions around the terms
        # "mask" suggests the underlying model where the term is located
        feature_mask = [0] * len(sentence)
        for term in terms:
            for i in range(term[0], term[1]):
                feature_mask[i] = 1

        definitions = list(self.model_definition.predict_text(
                    sentence, feature_mask=feature_mask,
                    join_settings=self.definition_join_sets))

        # combine terms with surrounding definitions
        # measure distance between each tearm and each definition
        definition_distances = {}  # { term0: [0:d0, 1:d1, ...N:dN], term1: ... }
        for t_s, t_e in terms:
            distances = []
            for i, definition in enumerate(definitions):
                df_s, df_e = definition
                if df_e <= t_s:
                    distance = t_s - df_e
                elif df_s >= t_e:
                    distance = df_s - t_e
                else:
                    if df_s > t_s:
                        distance = -(t_e - df_s + 1)
                    elif df_e < t_e:
                        distance = -(df_e - t_s + 1)
                    else:
                        distance = - (t_e - t_s + 1)
                distances.append((i, distance))
            distances.sort(key=lambda d: d[1])  # closest definitions go first
            definition_distances[(t_s, t_e)] = distances

        # get closest definitions for each term
        for term in terms:
            defs = definition_distances[term]
            df = defs[0] if defs else (term[0], term[1])
            def_start = min(df[0], term[0])
            def_end = max(df[1], term[1])

            term_phrase = sentence[term[0]: term[1]]
            ant = DefinitionAnnotation(
                coords=(def_start, def_end),
                name=term_phrase,
                text=sentence[def_start: def_end],
                locale='en')
            annotations.append(ant)

        # TODO: check if annotations overlap and cut overlapping parts
        return annotations

    def train_on_doccano_jsonl(self,
                               save_file_path: str,
                               exported_doc_path: str,
                               text_column_name: str = 'text',
                               labels_column_name: str = 'labels',
                               label_term: str = 'term',
                               label_definition: str = 'definition'):
        with codecs.open(exported_doc_path, 'rb', encoding='utf-8') as fr:
            df = pandas.read_json(fr, lines=True)
        df = df.drop(columns=['annotation_approver', 'id', 'meta'])

        definition_rows = []  # type: List[Tuple[str, List[Tuple[int, int]], List[int]]]
        term_rows = []  # type: List[Tuple[str, List[Tuple[int, int]]]]

        for _, row in df.iterrows():
            row_text = row[text_column_name]
            labels_definitions = []
            labels_terms = []
            for start, end, l_type in row[labels_column_name]:
                if l_type == label_definition:
                    labels_definitions.append((start, end))
                elif l_type == label_term:
                    labels_terms.append((start, end))

            # join definitions around terms because
            # definitions should (ideally) include terms, but due to
            # Doccano restrictions they !frame! terms. See:
            #   Member or sell or convey all or substantially all of its assets to any [d]Person that is not a
            #     Member (a "[/d][t]Merger Transaction[/t][d]")[/d] unless:

            definition_feature_mask, merged_def_labels = self.join_adjacent_definitions_labels(
                labels_definitions, labels_terms, row_text)

            definition_rows.append([row_text, merged_def_labels, definition_feature_mask])
            term_rows.append([row_text, labels_terms])

        df_terms = pandas.DataFrame(term_rows, columns=['sentence', 'labels'])
        df_definitions = pandas.DataFrame(definition_rows, columns=['sentence', 'labels', 'feature_mask'])
        self.train_on_formatted_data(df_definitions, df_terms, save_file_path)

    def train_on_formatted_data(self,
                                definition_frame: pandas.DataFrame,
                                term_frame: pandas.DataFrame,
                                save_file_path: str):
        """
        :param definition_frame: dataframe, [ (row_text, [(start, end), (start, end)...], feature_mask]
        :param term_frame: dataframe, [ (row_text, [(start, end), (start, end)...]]
        :param save_file_path: path to store zipped model files (as one file)
        """
        file_folder = os.path.dirname(save_file_path)
        temp_folder = os.path.join(file_folder, 'def_model_temp')
        try:
            shutil.rmtree(temp_folder)
        # pylint: disable=bare-except
        except:
            pass
        os.mkdir(temp_folder)

        file_terms = os.path.join(temp_folder, "terms")
        file_definitions = os.path.join(temp_folder, "definitions")

        self.model_term.train_and_save_on_dataframe(
            DetectingSettings(pre_window=1, post_window=1, use_spacy=False),
            term_frame,
            file_terms,
            compress=False)

        self.model_definition.train_and_save_on_dataframe(
            DetectingSettings(use_spacy=False),
            definition_frame,
            file_definitions,
            compress=False)

        with ZipFile(save_file_path, 'w') as zipObj2:
            zipObj2.write(file_terms, 'term.pickle')
            zipObj2.write(file_definitions, 'definition.pickle')
        try:
            shutil.rmtree(temp_folder)
        # pylint: disable=bare-except
        except:
            pass

    @staticmethod
    def join_adjacent_definitions_labels(labels_definitions, labels_terms, row_text):
        merged_def_labels = []
        definition_feature_mask = [0] * len(row_text)
        if not labels_definitions:
            return definition_feature_mask, merged_def_labels

        labels_definitions.sort(key=lambda l: l[0])
        ldef_end = -1
        for ld_start, ld_end in labels_definitions:
            continue_label = ldef_end >= 0 and abs(ld_start - ldef_end) < 2
            if not continue_label:
                merged_def_labels.append((ld_start, ld_end))
            else:
                merged_def_labels[-1] = (merged_def_labels[-1][0], ld_end)
            ldef_end = ld_end

            # continue current merged "definition" with "term"?
            for label_term_start, label_term_end in labels_terms:
                if abs(label_term_start - ldef_end) < 2:
                    ldef_end = label_term_end + 1
                    merged_def_labels[-1] = (merged_def_labels[-1][0], ldef_end)
                    for ci in range(label_term_start, label_term_end):
                        definition_feature_mask[ci] = 1
                    break

        return definition_feature_mask, merged_def_labels
