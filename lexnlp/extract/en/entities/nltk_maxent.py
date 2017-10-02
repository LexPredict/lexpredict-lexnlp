"""Entity extraction for English using NLTK and NLTK pre-trained maximum entropy classifier.

This module implements basic entity extraction functionality in English relying on the pre-trained
NLTK functionality, including POS tagger and NE (fuzzy) chunkers.

Todo:
  * Better define interface for sentences vs. raw text
  * Standardize generator vs list
"""

# Imports
import string

import nltk

from lexnlp.config.en.company_types import COMPANY_TYPES
from lexnlp.extract.en.entities import nltk_re
from lexnlp.extract.en.utils import strip_unicode_punctuation
from lexnlp.nlp.en.segments.sentences import get_sentences
from lexnlp.nlp.en.tokens import get_tokens

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

VALID_PUNCTUATION = [",", ".", "&"]


def get_persons(text, strict=False, return_source=False, window=2):
    """
    Get names from text.
    :param window:
    :param return_source:
    :param strict:
    :param text:
    :return:
    """
    # Iterate through sentences
    for sentence in get_sentences(text):
        # Tag sentence
        sentence_pos = nltk.pos_tag(get_tokens(sentence))

        # Iterate through chunks
        persons = []
        last_person_pos = None
        for i, chunk in enumerate(nltk.ne_chunk(sentence_pos)):
            if type(chunk) == nltk.tree.Tree:
                # Check label
                if chunk.label() == 'PERSON':
                    if not strict and last_person_pos is not None and (i - last_person_pos) < window:
                        persons[-1] += " " + " ".join([c[0] for c in chunk])
                    else:
                        persons.append(" ".join([c[0] for c in chunk]))
                    last_person_pos = i
            elif not strict and last_person_pos is not None and (i - last_person_pos) < window:
                if chunk[1] in ["NNP", "NNPS"]:
                    persons[-1] += " " + chunk[0]
                    last_person_pos = i
                elif chunk[1] in ["CC"] or chunk[0] in VALID_PUNCTUATION:
                    if chunk[0].lower() in ["or"]:
                        continue
                    persons[-1] += (" " if chunk[0].lower() in ["&", "and"] else "") + chunk[0]
                    last_person_pos = i
                else:
                    last_person_pos = None

        # Cleanup and yield
        for person in persons:
            # Cleanup
            person = person.strip()
            if len(person) <= 2:
                continue

            if person.lower().endswith(" and"):
                person = person[0:-4]
            elif person.endswith(" &"):
                person = person[0:-2]

            person = strip_unicode_punctuation(person).strip(string.punctuation).strip(string.whitespace)
            if return_source:
                yield person, sentence
            else:
                yield person


def get_organizations(text, strict=False, return_source=False, window=2):
    """
    Get organizations from text.
    :param window:
    :param return_source:
    :param strict:
    :param text:
    :return:
    """
    # Iterate through sentences
    for sentence in get_sentences(text):
        # Tag sentence
        sentence_pos = nltk.pos_tag(get_tokens(sentence))

        # Iterate through chunks
        organizations = []
        last_org_pos = None
        for i, chunk in enumerate(nltk.ne_chunk(sentence_pos)):
            if type(chunk) == nltk.tree.Tree:
                # Check label
                if chunk.label() in ['ORGANIZATION']:
                    if not strict and last_org_pos is not None and (i - last_org_pos) < window:
                        organizations[-1] += " " + " ".join([c[0] for c in chunk])
                    else:
                        organizations.append(" ".join([c[0] for c in chunk]))
                    last_org_pos = i
            elif not strict and last_org_pos is not None and (i - last_org_pos) < window:
                if chunk[1] in ["NNP", "NNPS"]:
                    organizations[-1] += " " + chunk[0]
                    last_org_pos = i
                elif chunk[1] in ["CC"] or chunk[0] in VALID_PUNCTUATION:
                    if chunk[0].lower() in ["or"]:
                        continue
                    organizations[-1] += (" " if chunk[0].lower() in ["&", "and"] else "") + chunk[0]
                    last_org_pos = i
                else:
                    last_org_pos = None

        for org in organizations:
            # Cleanup
            org = org.strip()
            if len(org) <= 2:
                continue

            if org.lower().endswith(" and"):
                org = org[0:-4]
            elif org.endswith(" &"):
                org = org[0:-2]

            org = strip_unicode_punctuation(org).strip(string.punctuation).strip(string.whitespace)
            if return_source:
                yield org, sentence
            else:
                yield org


def get_geopolitical(text, strict=False, return_source=False, window=2):
    """
    Get GPEs from text.
    :param window:
    :param return_source:
    :param strict:
    :param text:
    :return:
    """
    # Iterate through sentences
    for sentence in get_sentences(text):
        # Tag sentence
        sentence_pos = nltk.pos_tag(get_tokens(sentence))

        # Iterate through chunks
        gpes = []
        last_gpe_pos = None
        for i, chunk in enumerate(nltk.ne_chunk(sentence_pos)):
            if type(chunk) == nltk.tree.Tree:
                # Check label
                if chunk.label() == 'GPE':
                    if not strict and last_gpe_pos is not None and (i - last_gpe_pos) < window:
                        gpes[-1] += " " + " ".join([c[0] for c in chunk])
                    else:
                        gpes.append(" ".join([c[0] for c in chunk]))
                    last_gpe_pos = i
            elif not strict and last_gpe_pos is not None and (i - last_gpe_pos) < window:
                if chunk[1] in ["NNP", "NNPS"]:
                    gpes[-1] += " " + chunk[0]
                    last_gpe_pos = i
                elif chunk[1] in ["CC"] or chunk[0] in VALID_PUNCTUATION:
                    if chunk[0].lower() in ["or"]:
                        continue
                    gpes[-1] += (" " if chunk[0].lower() in ["&", "and"] else "") + chunk[0]
                    last_gpe_pos = i
                else:
                    last_gpe_pos = None

        # Clean up names and yield
        for gpe in gpes:
            # Cleanup
            gpe = gpe.strip()
            if len(gpe) <= 2:
                continue

            if gpe.lower().endswith(" and"):
                gpe = gpe[0:-4]
            elif gpe.endswith(" &"):
                gpe = gpe[0:-2]

            gpe = strip_unicode_punctuation(gpe).strip(string.punctuation).strip(string.whitespace)
            if return_source:
                yield gpe, sentence
            else:
                yield gpe


def get_noun_phrases(text, strict=False, return_source=False, window=3):
    """
    Get NNP phrases from text.
    :param window:
    :param return_source:
    :param strict:
    :param text:
    :return:
    """
    # Iterate through sentences
    for sentence in get_sentences(text):
        # Tag sentence
        sentence_pos = nltk.pos_tag(get_tokens(sentence))

        # Iterate through chunks
        nnps = []
        last_nnp_pos = None
        for i, chunk in enumerate(sentence_pos):
            # Check label
            if chunk[1] in ["NNP", "NNPS"]:
                if not strict and last_nnp_pos is not None and (i - last_nnp_pos) < window:
                    nnps[-1] += " " + chunk[0]
                else:
                    nnps.append(chunk[0])
                last_nnp_pos = i
            elif not strict and last_nnp_pos is not None and (i - last_nnp_pos) < window:
                if chunk[1] in ["NNP", "NNPS"]:
                    nnps[-1] += " " + chunk[0]
                    last_nnp_pos = i
                elif chunk[1] in ["CC"] or chunk[0] in VALID_PUNCTUATION:
                    if chunk[0].lower() in ["or"]:
                        continue
                    nnps[-1] += (" " if chunk[0].lower() in ["&", "and"] else "") + chunk[0]
                    last_nnp_pos = i
                else:
                    last_nnp_pos = None

        # Clean up names and yield
        for nnp in nnps:
            # Cleanup
            nnp = nnp.strip()
            if len(nnp) <= 2:
                continue

            if nnp.lower().endswith(" and"):
                nnp = nnp[0:-4].strip()
            elif nnp.endswith(" &"):
                nnp = nnp[0:-2].strip()

            nnp = strip_unicode_punctuation(nnp).strip(string.punctuation).strip(string.whitespace)
            if return_source:
                yield nnp, sentence
            else:
                yield nnp


def get_companies(text, strict=False, return_source=False):
    """
    Find company names in text, optionally using the stricter article/prefix expression.
    :param text:
    :param strict:
    :param return_source:
    :return:
    """
    # Iterate through sentences
    for sentence in get_sentences(text):
        for phrase in get_noun_phrases(sentence, strict=strict):
            for company_type in COMPANY_TYPES:
                if phrase.lower().endswith(company_type.lower().strip(string.punctuation)):
                    for result in nltk_re.get_companies(phrase):
                        if result[0] == result[1]:
                            continue
                        elif return_source:
                            yield result[0], result[1], sentence
                        else:
                            yield result[0], result[1]
