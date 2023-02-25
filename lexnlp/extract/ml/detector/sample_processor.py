__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import Tuple, Union, List, Callable, Any, Optional
import numpy
import pandas

from lexnlp.extract.ml.classifier.base_token_sequence_classifier_model import BaseTokenSequenceClassifierModel


def get_target_start_end_from_text(text: str,
                                   column_name_formatted: str, row) -> List[Tuple[int, int]]:
    noun_phrase_formatted = row[column_name_formatted]
    start_pos = text.find(noun_phrase_formatted)
    end_pos = start_pos + len(noun_phrase_formatted)
    return [(start_pos, end_pos)]


def get_target_start_end_from_corgetes(_: str,
                                       column_name_formatted: str, row) -> List[Tuple[int, int]]:
    return row[column_name_formatted]


def process_sample(sample_df: pandas.DataFrame,
                   s: BaseTokenSequenceClassifierModel,
                   build_target_data: bool = True,
                   pre_alloc_multiple: int = 30,
                   column_name_formatted: str = 'quantity_formatted',
                   outer_class: int = 0,
                   start_class: int = 1,
                   inner_class: int = 2,
                   end_class: int = 3,
                   get_target_start_end: Callable[[str, str, Any], List[Tuple[int, int]]] = get_target_start_end_from_text,
                   feature_mask_column: Optional[str] = None
                   ) -> Union[numpy.ndarray, Tuple[numpy.ndarray, numpy.ndarray]]:
    """
    Process a sample file to create feature and target data.
    :param sample_df: dataframe with at least 'sentence' column
    :param s: TokenSequenceClassifierModel or SpacyTokenSequenceClassifierModel
    :param build_target_data: build target data vector (if true)
    :param pre_alloc_multiple:
    :param column_name_formatted: "quantity_formatted" or "noun_phrase_formatted" ...
    :param outer_class:
    :param start_class:
    :param inner_class:
    :param end_class:
    :return: (feature_data, target_data) if build_target_data = True or just feature_data
    """

    # pre-allocate feature data approximately based on conservative sentence token count
    num_token_guess = sample_df.shape[0] * pre_alloc_multiple
    num_token = 0
    feature_data = numpy.zeros((num_token_guess, len(s.feature_list)), dtype=numpy.int8)
    if build_target_data:
        target_data = numpy.zeros((num_token_guess,))

    # iterate through rows
    for row_id, row in sample_df.iterrows():
        # set key variables
        text = row["sentence"]
        if build_target_data:
            # quantity_formatted or noun_phrase_formatted
            entity_coords = get_target_start_end(text, column_name_formatted, row)

        # set feature rows
        feature_mask = row[feature_mask_column] if feature_mask_column else None
        row_feature_data, row_tokens = s.get_feature_data(text, feature_mask=feature_mask)
        row_num_tokens = row_feature_data.shape[0]

        # check if we are within initial allocation
        if num_token + row_num_tokens <= feature_data.shape[0]:
            feature_data[num_token:(num_token + row_num_tokens), :] = row_feature_data
        else:
            # handle resize for both feature and target data if required
            rescale_multiple = sample_df.shape[0] / float(row_id)
            rescale_size = int(numpy.ceil(feature_data.shape[0] * rescale_multiple))
            feature_data.resize((rescale_size, feature_data.shape[1]), refcheck=False)
            if build_target_data:
                target_data.resize((rescale_size,), refcheck=False)
            feature_data[num_token:(num_token + row_num_tokens), :] = row_feature_data

        # set target vector entries
        if build_target_data:
            for i in range(row_num_tokens):
                token_start, token_end = row_tokens[i]

                target_data[num_token + i] = outer_class
                for start_pos, end_pos in entity_coords:
                    if token_start <= start_pos < token_end:
                        target_data[num_token + i] = start_class
                    elif token_start < end_pos <= token_end:
                        target_data[num_token + i] = end_class
                    elif start_pos < token_end and token_start < end_pos:
                        target_data[num_token + i] = inner_class

        num_token += row_num_tokens

    if build_target_data:
        return feature_data[0:num_token], target_data[0:num_token]
    return feature_data[0:num_token]
