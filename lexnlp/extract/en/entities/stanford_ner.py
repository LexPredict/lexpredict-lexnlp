"""Entity extraction for English using Stanford Named Entity Recognition (NER).

This module implements basic entity extraction functionality in English relying on the
pre-trained Stanford NLP NER classifiers.

Todo:
  * Better define interface for sentences vs. raw text
  * Standardize generator vs list
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# Change the path according to your system
import os
import string

from typing import Generator

from nltk.tag import StanfordNERTagger

from lexnlp.config.stanford import STANFORD_NER_PATH
from lexnlp.extract.en.utils import strip_unicode_punctuation
from lexnlp.nlp.en.segments.sentences import get_sentence_list
from lexnlp.nlp.en.stanford import get_tokens_list


# Setup Stanford NER configuration


STANFORD_NER_FILE = os.path.join(STANFORD_NER_PATH, "stanford-ner.jar")
STANFORD_NER_MODEL_MAP = {"english": "english.all.3class.distsim.crf.ser.gz",
                          "english7": "english.muc.7class.distsim.crf.ser.gz"}


def get_model_file(language):
    """
    Return the appropriate model file for each language.
    :param language:
    :return:
    """
    return os.path.join(STANFORD_NER_PATH, "classifiers", STANFORD_NER_MODEL_MAP[language])


try:
    STANFORD_NER_TAGGER = StanfordNERTagger(get_model_file("english"), STANFORD_NER_FILE, encoding='utf-8')
except LookupError:
    STANFORD_NER_TAGGER = None


def get_persons(text, strict=False, return_source=False, window=2) -> Generator:
    """
    Get persons from text using Stanford libraries.
    :param window:
    :param return_source:
    :param strict:
    :param text:
    :return:
    """
    # Iterate through sentences
    for sentence in get_sentence_list(text):
        # Tag sentence
        sentence_pos = STANFORD_NER_TAGGER.tag(get_tokens_list(text))

        # Iterate through chunks
        names = []
        last_person_pos = None
        for i, token in enumerate(sentence_pos):
            # Check label
            if token[1] == 'PERSON':
                if not strict and last_person_pos is not None and (i - last_person_pos) < window:
                    names[-1] += " " + token[0]
                else:
                    names.append(token[0])
                last_person_pos = i
            else:
                if token[0] in [".", ","]:
                    if not strict and last_person_pos is not None and (i - last_person_pos) < window:
                        names[-1] += (" " if token[0] not in string.punctuation else "") + token[0]
                        last_person_pos = i

        # Cleanup and yield
        for name in names:
            name = strip_unicode_punctuation(name).strip(string.punctuation).strip(string.whitespace)
            if return_source:
                yield name, sentence
            else:
                yield name


def get_organizations(text, strict=False, return_source=False, window=2) -> Generator:
    """
    Get organizations from text using Stanford libraries.
    :param window:
    :param return_source:
    :param strict:
    :param text:
    :return:
    """
    # Iterate through sentences
    for sentence in get_sentence_list(text):
        # Tag sentence
        sentence_pos = STANFORD_NER_TAGGER.tag(get_tokens_list(text))

        # Iterate through chunks
        orgs = []
        last_org_pos = None
        for i, token in enumerate(sentence_pos):
            # Check label
            if token[1] == 'ORGANIZATION':
                if not strict and last_org_pos is not None and (i - last_org_pos) < window:
                    orgs[-1] += " " + token[0]
                else:
                    orgs.append(token[0])
                last_org_pos = i
            else:
                if token[0] in [".", ","]:
                    if not strict and last_org_pos is not None and (i - last_org_pos) < window:
                        orgs[-1] += (" " if token[0] not in string.punctuation else "") + token[0]
                        last_org_pos = i

        # Cleanup and yield
        for org in orgs:
            org = strip_unicode_punctuation(org).strip(string.punctuation).strip(string.whitespace)
            if return_source:
                yield org, sentence
            else:
                yield org


def get_locations(text, strict=False, return_source=False, window=2) -> Generator:
    """
    Get locations from text using Stanford libraries.
    :param window:
    :param return_source:
    :param strict:
    :param text:
    :return:
    """
    # Iterate through sentences
    for sentence in get_sentence_list(text):
        # Tag sentence
        sentence_pos = STANFORD_NER_TAGGER.tag(get_tokens_list(text))

        # Iterate through chunks
        locations = []
        last_loc_pos = None
        for i, token in enumerate(sentence_pos):
            # Check label
            if token[1] == 'LOCATION':
                if not strict and last_loc_pos is not None and (i - last_loc_pos) < window:
                    locations[-1] += (" " if not token[0].startswith("'") else "") + token[0]
                else:
                    locations.append(token[0])
                last_loc_pos = i
            else:
                if token[0] in [".", ","]:
                    if not strict and last_loc_pos is not None and (i - last_loc_pos) < window:
                        locations[-1] += (" " if token[0] not in string.punctuation and not token[0].startswith(
                            "'") else "") + token[0]
                        last_loc_pos = i

        # Cleanup and yield
        for location in locations:
            location = strip_unicode_punctuation(location).strip(string.punctuation).strip(string.whitespace)
            if return_source:
                yield location, sentence
            else:
                yield location
