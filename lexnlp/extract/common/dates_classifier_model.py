__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import datetime
import itertools

import joblib
from typing import List, Tuple, Callable, Dict, Union, Set, Optional
import regex as re

import sklearn
import sklearn.ensemble
import sklearn.neural_network
from sklearn.model_selection import cross_val_score


REG_WORD_SEPARATOR = re.compile(r'[\s\-\.\[\]\{\}\(\),;:\+\\/]+')
REG_NUMBER = re.compile(r'^\d+')


def build_date_model(input_examples: List[Tuple[str, List[datetime.date]]],
                     output_file: str,
                     parse_dates: Callable[[str], List[Union[Tuple[int, int], Dict[str, List[str]]]]],
                     characters: List[str],
                     verbose=False,
                     alphabet_char_set: Optional[Set[str]] = False,
                     count_words=False):
    """
    Build a sklearn model for classifying date strings as potential false positives.
    :param input_examples: [(date_string, date), ...]
    :param output_file: file path to save the resulted model
    :param parse_dates: function that parses a date string returning tuples: [(date, start, end,), ...]
    :param characters: all characters (both letters and digits) for the provided locale
    :param alphabet_char_set: alphabetic characters only for the provided locale
    :param count_words: if True the feature vector will include count of words and numerals
    :param verbose: log extra messages (lots of them)
    """

    # Build feature and target data
    target_data = []
    example_data = []

    # Counts
    total = 0
    correct = 0

    # iterate text: expected: actual date examples
    feature_list = []
    col_names = None
    for raw_data in input_examples:
        date_str = raw_data[0]
        expected_dates = raw_data[1]
        date_results = parse_dates(date_str)

        # get raw dates
        dates = [d[0] for d in date_results]
        try:
            l_diff = set(dates) - set(expected_dates)
        # pylint: disable=broad-except
        except:
            print(dates)
            print(date_str)
            raise
        r_diff = set(expected_dates) - set(dates)
        if len(l_diff) > 0 or len(r_diff) > 0:
            if verbose:
                print(date_str)
                print((l_diff, r_diff, dates))
                print('=' * 16)
        else:
            correct += 1
        total += 1

        for d_date, d_pos in date_results:
            feature_row = get_date_features(date_str, d_pos[0], d_pos[1], characters,
                                            alphabet_char_set=alphabet_char_set,
                                            count_words=count_words)
            if not col_names:
                col_names = [col for col in feature_row]
            example_data.append(date_str[d_pos[0]:d_pos[1]])
            feature_list.append([feature_row[col] for col in col_names])
            target_data.append(int(d_date in expected_dates))

    if verbose:
        print("In-Sample Assessment:")
        print("Raw Dates:")
        print("Accuracy: {0}% on {1} samples".format(100. * float(correct) / total, total))
        print(f'Feature data: {len(feature_list)} x {len(feature_list[0])}')

    pipelines = [
        sklearn.pipeline.Pipeline([
            ('select', sklearn.feature_selection.SelectKBest(score_func=sklearn.feature_selection.f_classif, k=100)),
            ('classify', sklearn.ensemble.RandomForestClassifier())]),
        sklearn.pipeline.Pipeline([
            ('select', sklearn.feature_selection.SelectKBest(score_func=sklearn.feature_selection.f_classif, k=200)),
            ('classify', sklearn.ensemble.RandomForestClassifier())]),
        sklearn.pipeline.Pipeline([
            ('select', sklearn.feature_selection.SelectKBest(score_func=sklearn.feature_selection.f_classif, k=300)),
            ('classify', sklearn.ensemble.RandomForestClassifier())]),
        sklearn.pipeline.Pipeline([
            ('select', sklearn.feature_selection.SelectKBest(score_func=sklearn.feature_selection.f_classif, k=400)),
            ('classify', sklearn.ensemble.RandomForestClassifier())]),
        sklearn.pipeline.Pipeline([
            ('select', sklearn.feature_selection.SelectKBest(score_func=sklearn.feature_selection.chi2, k=200)),
            ('classify', sklearn.ensemble.RandomForestClassifier())]),
        sklearn.pipeline.Pipeline([
            ('select', sklearn.feature_selection.VarianceThreshold()),
            ('classify', sklearn.ensemble.RandomForestClassifier())]),
        sklearn.pipeline.Pipeline([
            ('select', sklearn.feature_selection.SelectKBest(score_func=sklearn.feature_selection.f_classif, k=200)),
            ('classify', sklearn.linear_model.LogisticRegressionCV())]),
        sklearn.pipeline.Pipeline([
            ('select', sklearn.feature_selection.VarianceThreshold()),
            ('classify', sklearn.linear_model.LogisticRegressionCV())]),
            # sklearn.pipeline.Pipeline([
            # ('select', sklearn.feature_selection.SelectKBest(score_func=sklearn.feature_selection.f_classif, k=300)),
            # ('classify', sklearn.neural_network.MLPClassifier(activation='tanh', solver='sgd', max_iter=1000))]),
    ]

    best_score, best_model = 0.0, None

    for i, model in enumerate(pipelines):
        start = datetime.datetime.now()
        model.fit(feature_list, target_data)
        print(f'{i}) Fitting the model took {(datetime.datetime.now() - start).total_seconds()}s')
        model.columns = col_names

        start = datetime.datetime.now()
        scores = cross_val_score(model, feature_list, target_data, cv=5, scoring='f1_macro')
        print(f'{i}) Cross-validating took {(datetime.datetime.now() - start).total_seconds()}s')
        avg_score = (sum(scores) or 0) / len(scores)
        print(f'{i + 1}) Avg. score is {avg_score}, scores are: {scores}]')
        if avg_score > best_score:
            best_model = model
            best_score = avg_score
        # Assess data
        if verbose:
            predicted_log = model.predict(feature_list)
            print(sklearn.metrics.classification_report(target_data, predicted_log))

    # Output to new production model
    joblib.dump(best_model, output_file)


def get_date_features(text,
                      start_index: int,
                      end_index: int,
                      characters: List[str],
                      alphabet_char_set: Optional[Set[str]] = False,
                      include_bigrams=True,
                      window=5,
                      norm=True,
                      count_words=False):
    """
    Get features to use for classification of date as false positive.
    :param text: raw text around potential date
    :param start_index: date start index
    :param end_index: date end index
    :param include_bigrams: whether to include bigram/bicharacter features
    :param window: window around match
    :param characters: characters to use for feature generation, e.g., digits only, alpha only
    :param alphabet_char_set: alphabetic characters only for the provided locale
    :param norm: whether to norm, i.e., transform to proportion
    :param count_words: words count in the string
    :return:
    """
    # Get text window
    window_start = max(0, start_index - window)
    window_end = min(len(text), end_index + window)
    feature_text = text[window_start:window_end].strip()
    date_text = text[start_index:end_index]

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

    if count_words:
        # calculate numbers below 31, numbers above 31, words and capitalized words
        numbers_above_31, numbers_below_31, words, cap_words = 0, 0, 0, 0
        for wrd in split_date_words(date_text):  # type: str
            if not wrd:
                continue
            if wrd[0] in alphabet_char_set:
                is_cap = len(wrd) > 1 and wrd[0].lower() != wrd[0] and wrd[1].lower() == wrd[1]
                if is_cap:
                    cap_words += 1
                else:
                    words += 1
                continue
            numbers = [int(n.group(0)) for n in REG_NUMBER.finditer(wrd)]
            if numbers:
                if numbers[0] < 31:
                    numbers_below_31 += 1
                else:
                    numbers_above_31 += 1
        if norm:
            sum_words = numbers_above_31 + numbers_below_31 + words + cap_words
            if sum_words:
                numbers_above_31, numbers_below_31, words, cap_words = \
                    numbers_above_31 / sum_words, numbers_below_31 / sum_words, words / sum_words, cap_words / sum_words
        char_vec['nb31'] = numbers_below_31
        char_vec['na31'] = numbers_above_31
        char_vec['wr_l'] = words
        char_vec['wr_u'] = cap_words

    return char_vec


def split_date_words(date_str: str) -> List[str]:
    return REG_WORD_SEPARATOR.split(date_str)
