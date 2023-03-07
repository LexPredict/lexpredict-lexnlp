__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import List, Optional

import numpy

from lexnlp.extract.ml.classifier.base_token_sequence_classifier_model import BaseTokenSequenceClassifierModel


class TokenSequenceClassifierModel(BaseTokenSequenceClassifierModel):
    """
    Classifier for generic text sequence objects.
    TODO: Implement skipgram.
    TODO: Implement sum and normalize.
    """

    def __init__(self, letter_set=None, digit_set=None, punc_set=None, symbol_set=None, match_tokens=None,
                 pre_window=0, post_window=0, calculate_sum=False, normalize=False, string_checks=False):
        super().__init__(letter_set=letter_set, digit_set=digit_set, punc_set=punc_set,
                         symbol_set=symbol_set, match_tokens=match_tokens, pre_window=pre_window,
                         post_window=post_window, calculate_sum=calculate_sum,
                         normalize=normalize, string_checks=string_checks)

    def get_feature_list(self,
                         letter_set=None,
                         digit_set=None,
                         punc_set=None,
                         symbol_set=None,
                         pre_window: Optional = None,
                         post_window: Optional = None):
        """
        Return set of features for a character tokenizer.
        """
        # handle params
        if letter_set is None:
            letter_set = self.letter_set

        if digit_set is None:
            digit_set = self.digit_set

        if punc_set is None:
            punc_set = self.punc_set

        if symbol_set is None:
            symbol_set = self.symbol_set

        if pre_window is None:
            pre_window = self.pre_window

        if post_window is None:
            post_window = self.post_window

        # initialize
        token_feature_list = ['position',
                              'length',
                              'mask']

        # iterate across window positions
        # pylint: disable=invalid-unary-operand-type
        for i in range(-pre_window, post_window + 1):
            o = str(i)
            token_feature_list.append(o + "_is_start")
            token_feature_list.append(o + "_is_end")
            if self.string_checks:
                token_feature_list.append(o + "_is_title")
                token_feature_list.append(o + "_is_lower")
                token_feature_list.append(o + "_is_upper")

            for c in letter_set:
                token_feature_list.append(o + "_char_" + c)
                token_feature_list.append(o + "_lchar_" + c)
                token_feature_list.append(o + "_first_char_" + c)
                token_feature_list.append(o + "_first_lchar_" + c)
                token_feature_list.append(o + "_last_char_" + c)
                token_feature_list.append(o + "_last_lchar_" + c)

            for c in digit_set:
                token_feature_list.append(o + "_digit_" + c)
                token_feature_list.append(o + "_first_digit_" + c)
                token_feature_list.append(o + "_last_digit_" + c)

            for c in punc_set:
                token_feature_list.append(o + "_punc_" + c)
                token_feature_list.append(o + "_first_punc_" + c)
                token_feature_list.append(o + "_last_punc_" + c)

            for c in symbol_set:
                token_feature_list.append(o + "_symbol_" + c)
                token_feature_list.append(o + "_first_symbol_" + c)
                token_feature_list.append(o + "_last_symbol_" + c)

            token_feature_list.append(o + "_char_other")
            token_feature_list.append(o + "_first_char_other")
            token_feature_list.append(o + "_last_char_other")

            for c in self.unicode_category_set:
                token_feature_list.append(o + "_cat_" + c)
                token_feature_list.append(o + "_first_cat_" + c)
                token_feature_list.append(o + "_last_cat_" + c)
            for c in self.unicode_top_category_set:
                token_feature_list.append(o + "_tcat_" + c)
                token_feature_list.append(o + "_first_tcat_" + c)
                token_feature_list.append(o + "_last_tcat_" + c)

            for token in self.match_tokens:
                token_feature_list.append(o + "_token_" + token)

        if self.calculate_sum:
            token_feature_list.append("sum_char_other")

            for c in self.letter_set:
                token_feature_list.append("sum_char_" + c)

            for c in self.digit_set:
                token_feature_list.append("sum_digit_" + c)

            for c in self.punc_set:
                token_feature_list.append("sum_punc_" + c)

            for c in self.symbol_set:
                token_feature_list.append("sum_symbol_" + c)

        return token_feature_list

    # TODO: add "hints" alongside with the text? areas with special
    def get_feature_data(self,
                         text: str,
                         feature_mask: List[int] = None):
        """
        Get features based on character model.
        feature_mask - array of numbers, has the same length as text
        """
        # setup return data
        text_len = len(text)
        text_lower = [c.lower() for c in text]
        text_data = [(self.unicode_character_top_category_mapping[
                          c] if c in self.unicode_character_top_category_mapping else "C",
                      self.unicode_character_category_mapping[
                          c] if c in self.unicode_character_category_mapping else "Cc",
                      ord(c)
                      ) for c in text]

        tokens = []
        token_start = 0
        # calculate token offsets
        for i in range(text_len - 1):
            if text_data[i][0] not in ['Z', 'C'] and text_data[i + 1][0] in ['Z', 'C']:
                tokens.append((token_start, i + 1))
                token_start = min(i + 2, text_len)
            elif text_data[i][0] in ['Z', 'C'] and text_data[i + 1][0] in ['Z', 'C']:
                token_start += 1
        tokens.append((token_start, text_len))
        num_tokens = len(tokens)

        # Setup return structure
        feature_data = numpy.zeros((num_tokens, len(self.feature_list)), dtype=numpy.int8)

        for i in range(num_tokens):
            o = str(0)
            token_text = text[tokens[i][0]:tokens[i][1]]

            feature_data[i, self._feature_index_map['position']] = i
            feature_data[i, self._feature_index_map['length']] = tokens[i][1] - tokens[i][0]
            feature_data[i, self._feature_index_map['mask']] = 0

            feature_data[i, self._feature_index_map[o + "_is_start"]] = int(i == 0)
            feature_data[i, self._feature_index_map[o + "_is_end"]] = int(i == num_tokens - 1)
            if self.string_checks:
                feature_data[i, self._feature_index_map[o + "_is_title"]] = int(token_text == token_text.title())
                feature_data[i, self._feature_index_map[o + "_is_lower"]] = int(token_text == token_text.lower())
                feature_data[i, self._feature_index_map[o + "_is_upper"]] = int(token_text == token_text.upper())

            if token_text in self.match_tokens:
                feature_data[i, self._feature_index_map[o + "_token_" + token_text]] = 1

            for j in range(tokens[i][0], tokens[i][1]):
                c = text[j]
                cl = text_lower[j]
                if feature_mask:
                    feature_data[i, self._feature_index_map['mask']] = max(
                        feature_data[i, self._feature_index_map['mask']], feature_mask[j])

                if c in self.letter_set:
                    feature_data[i, self._feature_index_map[o + "_char_" + c]] += 1
                    feature_data[i, self._feature_index_map[o + "_lchar_" + cl]] += 1
                    if j == tokens[i][0]:
                        feature_data[i, self._feature_index_map[o + "_first_char_" + c]] += 1
                        feature_data[i, self._feature_index_map[o + "_first_lchar_" + cl]] += 1
                    if j == tokens[i][1] - 1:
                        feature_data[i, self._feature_index_map[o + "_last_char_" + c]] += 1
                        feature_data[i, self._feature_index_map[o + "_last_lchar_" + cl]] += 1
                elif c in self.digit_set:
                    feature_data[i, self._feature_index_map[o + "_digit_" + c]] += 1
                    if j == tokens[i][0]:
                        feature_data[i, self._feature_index_map[o + "_first_digit_" + c]] += 1
                    if j == tokens[i][1] - 1:
                        feature_data[i, self._feature_index_map[o + "_last_digit_" + c]] += 1
                elif c in self.punc_set:
                    feature_data[i, self._feature_index_map[o + "_punc_" + c]] += 1
                    if j == tokens[i][0]:
                        feature_data[i, self._feature_index_map[o + "_first_punc_" + c]] += 1
                    if j == tokens[i][1] - 1:
                        feature_data[i, self._feature_index_map[o + "_last_punc_" + c]] += 1
                elif c in self.symbol_set:
                    feature_data[i, self._feature_index_map[o + "_symbol_" + c]] += 1
                    if j == tokens[i][0]:
                        feature_data[i, self._feature_index_map[o + "_first_symbol_" + c]] += 1
                    if j == tokens[i][1] - 1:
                        feature_data[i, self._feature_index_map[o + "_last_symbol_" + c]] += 1
                else:
                    feature_data[i, self._feature_index_map[o + "_char_other"]] += 1
                    if j == tokens[i][0]:
                        feature_data[i, self._feature_index_map[o + "_first_char_other"]] += 1
                    if j == tokens[i][1] - 1:
                        feature_data[i, self._feature_index_map[o + "_last_char_other"]] += 1

                feature_data[i, self._feature_index_map[o + "_cat_" + text_data[j][1]]] += 1
                feature_data[i, self._feature_index_map[o + "_tcat_" + text_data[j][0]]] += 1

                if j == tokens[i][0]:
                    feature_data[i, self._feature_index_map[o + "_first_cat_" + text_data[j][1]]] += 1
                    feature_data[i, self._feature_index_map[o + "_first_tcat_" + text_data[j][0]]] += 1
                if j == tokens[i][1] - 1:
                    feature_data[i, self._feature_index_map[o + "_last_cat_" + text_data[j][1]]] += 1
                    feature_data[i, self._feature_index_map[o + "_last_tcat_" + text_data[j][0]]] += 1

        # handle window feature calculations
        if self.pre_window + self.post_window > 0:
            for i in range(num_tokens):
                j_start = (i - self.pre_window) if (i - self.pre_window >= 0) else 0
                j_end = (i + self.post_window) if (i + self.post_window + 1 < num_tokens) else num_tokens
                for j in range(j_start, j_end):
                    if j == i:
                        continue
                    o = str(j - i)
                    for f in self._base_feature_list:
                        feature_data[i, self._feature_index_map[o + '_' + f]] = \
                            feature_data[j, self._feature_index_map['0_' + f]]

        return feature_data, tokens
