__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

import datetime
import itertools

import joblib
import pandas as pd
from typing import List, Tuple, Callable, Dict, Union

import sklearn
import sklearn.ensemble


def build_date_model(input_examples: List[Tuple[str, List[datetime.date]]],
                     output_file: str,
                     parse_dates: Callable[[str], List[Union[Tuple[int, int], Dict[str, List[str]]]]],
                     characters: List[str],
                     verbose=True):
    """
    Build a sklearn model for classifying date strings as potential false positives.
    """
    # Build feature and target data
    feature_data = []
    target_data = []
    example_data = []

    # Counts
    total = 0
    correct = 0

    # Iterate through examples
    for example in input_examples:
        # Get raw dates
        date_results = parse_dates(example[0])
        dates = [d[0] for d in date_results]

        try:
            l_diff = set(dates) - set(example[1])
        # pylint: disable=broad-except
        except:
            print(dates)
            print(example)
            raise
        r_diff = set(example[1]) - set(dates)
        if len(l_diff) > 0 or len(r_diff) > 0:
            print(example[0])
            print((l_diff, r_diff, dates))
            print("=" * 16)
        else:
            correct += 1
        total += 1

        for d_date, d_pos in date_results:
            feature_row = get_date_features(example[0], d_pos[0], d_pos[1], characters)
            example_data.append(example[0][d_pos[0]:d_pos[1]])
            feature_data.append(feature_row)
            target_data.append(int(d_date in example[1]))

    # Get data frame
    feature_df = pd.DataFrame(feature_data).fillna(-1)

    if verbose:
        print("In-Sample Assessment:")
        print("Raw Dates:")
        print("Accuracy: {0}% on {1} samples".format(100. * float(correct) / total, total))
        print("Feature data: {0}".format(feature_df.shape))

    model = sklearn.pipeline.Pipeline([
        ('select', sklearn.feature_selection.SelectKBest(score_func=sklearn.feature_selection.f_classif, k=400)),
        ('classify', sklearn.ensemble.RandomForestClassifier())
    ])

    model.fit(feature_df, target_data)
    model.columns = feature_df.columns

    # Assess data
    if verbose:
        predicted_log = model.predict(feature_df)
        print(sklearn.metrics.classification_report(target_data, predicted_log))

    # Output to new production model
    joblib.dump(model, output_file)


def get_date_features(text,
                      start_index: int,
                      end_index: int,
                      characters: List[str],
                      include_bigrams=True,
                      window=5,
                      norm=True):
    """
    Get features to use for classification of date as false positive.
    :param text: raw text around potential date
    :param start_index: date start index
    :param end_index: date end index
    :param include_bigrams: whether to include bigram/bicharacter features
    :param window: window around match
    :param characters: characters to use for feature generation, e.g., digits only, alpha only
    :param norm: whether to norm, i.e., transform to proportion
    :return:
    """
    # Get text window
    window_start = max(0, start_index - window)
    window_end = min(len(text), end_index + window)
    feature_text = text[window_start:window_end].strip()

    # Build character vector
    char_vec = {}
    char_keys = []
    bigram_keys = {}
    for character in characters:
        key = f'char_{character}'
        char_vec[key] = feature_text.count(character)
        char_keys.append(key)

    # Build character bigram vector
    if include_bigrams:
        bigram_set = [''.join(s) for s in itertools.permutations(characters, 2)]
        bigram_keys = []
        for character in bigram_set:
            key = f'bigram_{character}'
            char_vec[key] = feature_text.count(character)
            bigram_keys.append(key)

    # Norm if requested
    if norm:
        # Norm by characters
        char_sum = sum([char_vec[k] for k in char_keys])
        if char_sum > 0:
            for key in char_keys:
                char_vec[key] /= float(char_sum)

        # Norm by bigrams
        if include_bigrams:
            bigram_sum = sum([char_vec[k] for k in bigram_keys])
            if bigram_sum > 0:
                for key in bigram_keys:
                    char_vec[key] /= float(bigram_sum)

    return char_vec
