#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Imports

from nltk.corpus import wordnet
from nose.tools import assert_list_equal, nottest

from lexnlp.nlp.en.segments.sentences import get_sentences
from lexnlp.nlp.en.tokens import get_adjectives, get_adverbs, get_lemma_generator, get_lemmas, get_nouns, \
    get_stem_generator, get_stems, get_token_generator, get_tokens, get_verbs, get_wordnet_pos

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

EXAMPLE_TEXT_1 = """Dear Jerry:
This amended and restated letter agreement sets forth the terms of your employment with Logitech Inc., a California 
corporation (the “Company”), as well as our understanding with respect to any termination of that employment 
relationship. Effective on the date set forth above, this letter agreement supersedes your offer letter dated January
28, 2008, in its entirety.
1. Position and Duties. You will be employed by the Company as President and Chief Executive Officer and will serve in
the positions set forth on Exhibit A. In such positions, you will have the duties and authority at a level consistent 
with the duties and authority set forth on Exhibit A. You accept employment with the Company on the terms and conditions
set forth in this Agreement, and you agree to devote your full business time, energy and skill to your duties.
2. Term of Employment. Your employment with the Company will continue for no specified term and may be terminated by
you or the Company at any time, with or without cause, subject to the provisions of Paragraphs 4, 5 and 6 below."""

EXAMPLE_TEXT_1_TOKENS = [
    ['Dear', 'Jerry', ':', 'This', 'amended', 'and', 'restated', 'letter', 'agreement', 'sets', 'forth', 'the', 'terms',
     'of', 'your', 'employment', 'with', 'Logitech', 'Inc.', ',', 'a', 'California', 'corporation', '(', 'the', '“',
     'Company', '”', ')', ',', 'as', 'well', 'as', 'our', 'understanding', 'with', 'respect', 'to', 'any',
     'termination', 'of', 'that', 'employment', 'relationship', '.'],
    ['Effective', 'on', 'the', 'date', 'set', 'forth', 'above', ',', 'this', 'letter', 'agreement', 'supersedes',
     'your', 'offer', 'letter', 'dated', 'January', '28', ',', '2008', ',', 'in', 'its', 'entirety', '.'],
    ['1', '.'],
    ['Position', 'and', 'Duties', '.'],
    ['You', 'will', 'be', 'employed', 'by', 'the', 'Company', 'as', 'President', 'and', 'Chief', 'Executive',
     'Officer', 'and', 'will', 'serve', 'in', 'the', 'positions', 'set', 'forth', 'on', 'Exhibit', 'A', '.'],
    ['In', 'such', 'positions', ',', 'you', 'will', 'have', 'the', 'duties', 'and', 'authority', 'at', 'a', 'level',
     'consistent', 'with', 'the', 'duties', 'and', 'authority', 'set', 'forth', 'on', 'Exhibit', 'A', '.'],
    ['You', 'accept', 'employment', 'with', 'the', 'Company', 'on', 'the', 'terms', 'and', 'conditions', 'set',
     'forth', 'in', 'this', 'Agreement', ',', 'and', 'you', 'agree', 'to', 'devote', 'your', 'full', 'business',
     'time', ',', 'energy', 'and', 'skill', 'to', 'your', 'duties', '.'],
    ['2', '.'],
    ['Term', 'of', 'Employment', '.'],
    ['Your', 'employment', 'with', 'the', 'Company', 'will', 'continue', 'for', 'no', 'specified', 'term', 'and',
     'may', 'be', 'terminated', 'by', 'you', 'or', 'the', 'Company', 'at', 'any', 'time', ',', 'with', 'or',
     'without', 'cause', ',', 'subject', 'to', 'the', 'provisions', 'of', 'Paragraphs', '4', ',', '5', 'and', '6',
     'below', '.']]
EXAMPLE_TEXT_1_TOKENS_LC = [
    ['dear', 'jerry', ':', 'this', 'amended', 'and', 'restated', 'letter', 'agreement', 'sets', 'forth', 'the', 'terms',
     'of', 'your', 'employment', 'with', 'logitech', 'inc.', ',', 'a', 'california', 'corporation', '(', 'the', '“',
     'company', '”', ')', ',', 'as', 'well', 'as', 'our', 'understanding', 'with', 'respect', 'to', 'any',
     'termination', 'of', 'that', 'employment', 'relationship', '.'],
    ['effective', 'on', 'the', 'date', 'set', 'forth', 'above', ',', 'this', 'letter', 'agreement', 'supersedes',
     'your', 'offer', 'letter', 'dated', 'january', '28', ',', '2008', ',', 'in', 'its', 'entirety', '.'],
    ['1', '.'],
    ['position', 'and', 'duties', '.'],
    ['you', 'will', 'be', 'employed', 'by', 'the', 'company', 'as', 'president', 'and', 'chief', 'executive', 'officer',
     'and', 'will', 'serve', 'in', 'the', 'positions', 'set', 'forth', 'on', 'exhibit', 'a', '.'],
    ['in', 'such', 'positions', ',', 'you', 'will', 'have', 'the', 'duties', 'and', 'authority', 'at', 'a', 'level',
     'consistent', 'with', 'the', 'duties', 'and', 'authority', 'set', 'forth', 'on', 'exhibit', 'a', '.'],
    ['you', 'accept', 'employment', 'with', 'the', 'company', 'on', 'the', 'terms', 'and', 'conditions', 'set', 'forth',
     'in', 'this', 'agreement', ',', 'and', 'you', 'agree', 'to', 'devote', 'your', 'full', 'business', 'time', ',',
     'energy', 'and', 'skill', 'to', 'your', 'duties', '.'],
    ['2', '.'],
    ['term', 'of', 'employment', '.'],
    ['your', 'employment', 'with', 'the', 'company', 'will', 'continue', 'for', 'no', 'specified', 'term', 'and', 'may',
     'be', 'terminated', 'by', 'you', 'or', 'the', 'company', 'at', 'any', 'time', ',', 'with', 'or', 'without',
     'cause', ',', 'subject', 'to', 'the', 'provisions', 'of', 'paragraphs', '4', ',', '5', 'and', '6', 'below', '.']]

EXAMPLE_TEXT_1_TOKENS_LC_SW = [
    ['dear', 'jerry', ':', 'amended', 'restated', 'letter', 'agreement', 'sets', 'terms', 'employment', 'logitech',
     'inc.', ',', 'california', 'corporation', '(', '“', 'company', '”', ')', ',', 'well', 'understanding', 'respect',
     'termination', 'employment', 'relationship', '.'],
    ['effective', 'date', 'set', ',', 'letter', 'agreement', 'supersedes', 'offer', 'letter', 'dated', 'january', '28',
     ',', '2008', ',', 'entirety', '.'],
    ['1', '.'],
    ['position', 'duties', '.'],
    ['employed', 'company', 'president', 'chief', 'executive', 'officer', 'serve', 'positions', 'set', 'exhibit', '.'],
    ['positions', ',', 'duties', 'authority', 'level', 'consistent', 'duties', 'authority', 'set', 'exhibit', '.'],
    ['accept', 'employment', 'company', 'terms', 'conditions', 'set', 'agreement', ',', 'agree', 'devote', 'full',
     'business', 'time', ',', 'energy', 'skill', 'duties', '.'],
    ['2', '.'],
    ['term', 'employment', '.'],
    ['employment', 'company', 'continue', 'specified', 'term', 'terminated', 'company', 'time', ',', 'cause', ',',
     'subject', 'provisions', 'paragraphs', '4', ',', '5', '6', '.']]

# Real world example 2
EXAMPLE_TEXT_2 = """It has been  approved  and endorsed by The  Associated  General  Contractors  of America."""
EXAMPLE_TEXT_2_TOKENS = ["It", "has", "been", "approved", "and", "endorsed", "by", "The", "Associated", "General",
                         "Contractors", "of", "America", "."]
EXAMPLE_TEXT_2_VERBS = ["has", "been", "approved", "endorsed"]
EXAMPLE_TEXT_2_VERB_LEMMAS = ["have", "be", "approve", "endorse"]
EXAMPLE_TEXT_2_STEMS = ['It', 'has', 'been', 'approv', 'and', 'endors', 'by', 'the', 'Associ', 'General', 'Contractor',
                        'of', 'America', '.']
EXAMPLE_TEXT_2_STEMS_LC = ['it', 'has', 'been', 'approv', 'and', 'endors', 'by', 'the', 'associ', 'general',
                           'contractor', 'of', 'america', '.']
EXAMPLE_TEXT_2_STEMS_LC_SW = ['approv', 'endors', 'associ', 'general', 'contractor', 'america', '.']
EXAMPLE_2_LEMMAS = ['It', 'have', 'be', 'approve', 'and', 'endorse', 'by', 'The', 'Associated', 'General',
                    'Contractors', 'of', 'America', '.']
EXAMPLE_2_LEMMAS_LC = ['it', 'have', 'be', 'approve', 'and', 'endorse', 'by', 'the', 'associated', 'general',
                       'contractors', 'of', 'america', '.']
EXAMPLE_2_LEMMAS_LC_SW = ['approve', 'endorse', 'associated', 'general', 'contractors', 'america', '.']
EXAMPLE_2_LEMMAS_SW = ['approve', 'endorse', 'Associated', 'General', 'Contractors', 'America', '.']

# Real example 3
EXAMPLE_TEXT_3 = """Builder shall comply with laws, rules, regulations and requirements of any Regulatory Authorities
that are applicable and existing at the time of the execution of this Agreement that are in effect or which shall
become effective as to any vessels built during the Project Schedule and which affect the construction of works, plants
and vessels, in or on navigable waters and the shores thereof, and all other waters subject to the control of the United
States as set forth in the Contract Documents and shall procure at its own expense such permits from the United States
and from state and local authorities in the jurisdiction in which Builder is constructing the Vessels as may be
necessary in connection with beginning or carrying on the completion of the Work, and shall at times comply with all
United States, state and local laws in the jurisdiction in which Builder is constructing the Vessels in any way
affecting the Work and affecting any documentation of such work with the U.S. Coast Guard."""
EXAMPLE_TEXT_3_STEMS_LC = ['builder', 'shall', 'compli', 'with', 'law', ',', 'rule', ',', 'regul', 'and', 'requir',
                           'of', 'ani', 'regulatori', 'author', 'that', 'are', 'applic', 'and', 'exist', 'at', 'the',
                           'time', 'of', 'the', 'execut', 'of', 'this', 'agreement', 'that', 'are', 'in', 'effect',
                           'or', 'which', 'shall', 'becom', 'effect', 'as', 'to', 'ani', 'vessel', 'built', 'dure',
                           'the', 'project', 'schedul', 'and', 'which', 'affect', 'the', 'construct', 'of', 'work', ',',
                           'plant', 'and', 'vessel', ',', 'in', 'or', 'on', 'navig', 'water', 'and', 'the', 'shore',
                           'thereof', ',', 'and', 'all', 'other', 'water', 'subject', 'to', 'the', 'control', 'of',
                           'the', 'unit', 'state', 'as', 'set', 'forth', 'in', 'the', 'contract', 'document', 'and',
                           'shall', 'procur', 'at', 'it', 'own', 'expens', 'such', 'permit', 'from', 'the', 'unit',
                           'state', 'and', 'from', 'state', 'and', 'local', 'author', 'in', 'the', 'jurisdict', 'in',
                           'which', 'builder', 'is', 'construct', 'the', 'vessel', 'as', 'may', 'be', 'necessari', 'in',
                           'connect', 'with', 'begin', 'or', 'carri', 'on', 'the', 'complet', 'of', 'the', 'work', ',',
                           'and', 'shall', 'at', 'time', 'compli', 'with', 'all', 'unit', 'state', ',', 'state', 'and',
                           'local', 'law', 'in', 'the', 'jurisdict', 'in', 'which', 'builder', 'is', 'construct', 'the',
                           'vessel', 'in', 'ani', 'way', 'affect', 'the', 'work', 'and', 'affect', 'ani', 'document',
                           'of', 'such', 'work', 'with', 'the', 'u.s.', 'coast', 'guard', '.']
EXAMPLE_TEXT_3_STEMS_LC_SW = ['builder', 'compli', 'law', ',', 'rule', ',', 'regul', 'requir', 'regulatori', 'author',
                              'applic', 'exist', 'time', 'execut', 'agreement', 'effect', 'becom', 'effect', 'vessel',
                              'built', 'project', 'schedul', 'affect', 'construct', 'work', ',', 'plant', 'vessel', ',',
                              'navig', 'water', 'shore', ',', 'water', 'subject', 'control', 'unit', 'state', 'set',
                              'contract', 'document', 'procur', 'expens', 'permit', 'unit', 'state', 'state', 'local',
                              'author', 'jurisdict', 'builder', 'construct', 'vessel', 'necessari', 'connect', 'begin',
                              'carri', 'complet', 'work', ',', 'time', 'compli', 'unit', 'state', ',', 'state', 'local',
                              'law', 'jurisdict', 'builder', 'construct', 'vessel', 'way', 'affect', 'work', 'affect',
                              'document', 'work', 'u.s.', 'coast', 'guard', '.']


@nottest
def run_sentence_token_gen_test(text, result, lowercase=False, stopword=False):
    """
    Base test method to run against text with given results.
    """
    # Get list from text
    sentence_list = get_sentences(text)

    # Check length first
    assert len(sentence_list) == len(result)

    # Check each sentence matches
    for i in range(len(sentence_list)):
        tokens = list(get_token_generator(sentence_list[i], lowercase=lowercase, stopword=stopword))
        assert_list_equal(tokens, result[i])


@nottest
def run_sentence_token_test(text, result, lowercase=False, stopword=False):
    """
    Base test method to run against text with given results.
    """
    # Get list from text
    sentence_list = get_sentences(text)

    # Check length first
    assert len(sentence_list) == len(result)

    # Check each sentence matches
    for i in range(len(sentence_list)):
        tokens = get_tokens(sentence_list[i], lowercase=lowercase, stopword=stopword)
        assert_list_equal(tokens, result[i])


@nottest
def run_stem_gen_test(text, result, lowercase=False, stopword=False):
    """
    Base test method to run against text with given results.
    """
    # Get list from text
    stem_list = list(get_stem_generator(text, lowercase=lowercase, stopword=stopword))

    # Check length first
    assert len(stem_list) == len(result)

    # Check each sentence matches
    assert_list_equal(stem_list, result)


@nottest
def run_stem_test(text, result, lowercase=False, stopword=False):
    """
    Base test method to run against text with given results.
    """
    # Get list from text
    stem_list = get_stems(text, lowercase=lowercase, stopword=stopword)

    # Check length first
    assert len(stem_list) == len(result)

    # Check each sentence matches
    assert_list_equal(stem_list, result)


@nottest
def run_lemma_gen_test(text, result, lowercase=False, stopword=False):
    """
    Base test method to run against text with given results.
    """
    # Get list from text
    lemma_list = list(get_lemma_generator(text, lowercase=lowercase, stopword=stopword))

    # Check length first
    assert len(lemma_list) == len(result)

    # Check each sentence matches
    assert_list_equal(lemma_list, result)


@nottest
def run_lemma_test(text, result, lowercase=False, stopword=False):
    """
    Base test method to run against text with given results.
    """
    # Get list from text
    lemma_list = get_lemmas(text, lowercase=lowercase, stopword=stopword)

    # Check length first
    assert len(lemma_list) == len(result)

    # Check each sentence matches
    assert_list_equal(lemma_list, result)


def test_token_gen_example_1():
    run_sentence_token_gen_test("This is a test.", [["This", "is", "a", "test", "."]])


def test_token_gen_example_1_lc():
    run_sentence_token_gen_test("This is a test.", [["this", "is", "a", "test", "."]], lowercase=True)


def test_token_gen_example_1_sw():
    run_sentence_token_gen_test("This is a Test.", [["Test", "."]], stopword=True)


def test_token_example_1():
    run_sentence_token_test("This is a test.", [["This", "is", "a", "test", "."]])


def test_token_example_1_lc():
    run_sentence_token_test("This is a test.", [["this", "is", "a", "test", "."]], lowercase=True)


def test_stem_example_1():
    # Snowball returns lowercase always
    run_stem_test(EXAMPLE_TEXT_2, EXAMPLE_TEXT_2_STEMS_LC, lowercase=False)


def test_stem_example_1_lc():
    # Snowball returns lowercase always
    run_stem_test(EXAMPLE_TEXT_2, EXAMPLE_TEXT_2_STEMS_LC, lowercase=True)


def test_stem_example_1_lc_sw():
    # Snowball returns lowercase always
    run_stem_test(EXAMPLE_TEXT_2, EXAMPLE_TEXT_2_STEMS_LC_SW, lowercase=True, stopword=True)


def test_stem_example_2():
    # Snowball returns lowercase always
    run_stem_test(EXAMPLE_TEXT_3, EXAMPLE_TEXT_3_STEMS_LC, lowercase=False)


def test_stem_example_2_lc():
    # Snowball returns lowercase always
    run_stem_test(EXAMPLE_TEXT_3, EXAMPLE_TEXT_3_STEMS_LC, lowercase=True)


def test_stem_example_2_lc_sw():
    # Snowball returns lowercase always
    run_stem_test(EXAMPLE_TEXT_3, EXAMPLE_TEXT_3_STEMS_LC_SW, lowercase=True, stopword=True)


def test_stem_gen_example_1():
    # Snowball returns lowercase always
    run_stem_gen_test(EXAMPLE_TEXT_2, EXAMPLE_TEXT_2_STEMS_LC, lowercase=False)


def test_stem_gen_example_1_lc():
    # Snowball returns lowercase always
    run_stem_gen_test(EXAMPLE_TEXT_2, EXAMPLE_TEXT_2_STEMS_LC, lowercase=True)


def test_stem_gen_example_1_lc_sw():
    # Snowball returns lowercase always
    run_stem_gen_test(EXAMPLE_TEXT_2, EXAMPLE_TEXT_2_STEMS_LC_SW, lowercase=True, stopword=True)


def test_wordnet_pos():
    # Import and setup map
    treebank_pos_map = {"JJ": wordnet.ADJ,
                        "JJR": wordnet.ADJ,
                        "JJS": wordnet.ADJ,
                        "VB": wordnet.VERB,
                        "VBD": wordnet.VERB,
                        "VBN": wordnet.VERB,
                        "NN": wordnet.NOUN,
                        "NNP": wordnet.NOUN,
                        "NNPS": wordnet.NOUN,
                        "RB": wordnet.ADV,
                        "RBR": wordnet.ADV
                        }

    # Check function output against map
    for k in treebank_pos_map:
        assert get_wordnet_pos(k) == treebank_pos_map[k]


def test_lemma_example_1():
    run_lemma_test(EXAMPLE_TEXT_2, EXAMPLE_2_LEMMAS)


def test_lemma_example_1_lc():
    run_lemma_test(EXAMPLE_TEXT_2, EXAMPLE_2_LEMMAS_LC, lowercase=True)


def test_lemma_example_1_lc_sw():
    run_lemma_test(EXAMPLE_TEXT_2, EXAMPLE_2_LEMMAS_LC_SW, lowercase=True, stopword=True)


def test_lemma_gen_example_1():
    run_lemma_gen_test(EXAMPLE_TEXT_2, EXAMPLE_2_LEMMAS)


def test_lemma_gen_example_1_lc():
    run_lemma_gen_test(EXAMPLE_TEXT_2, EXAMPLE_2_LEMMAS_LC, lowercase=True)


def test_lemma_gen_example_1_lc_sw():
    run_lemma_gen_test(EXAMPLE_TEXT_2, EXAMPLE_2_LEMMAS_LC_SW, lowercase=True, stopword=True)


def test_lemma_gen_example_1_sw():
    run_lemma_gen_test(EXAMPLE_TEXT_2, EXAMPLE_2_LEMMAS_SW, stopword=True)


def test_verbs_example_2():
    verbs = get_verbs(EXAMPLE_TEXT_2)
    assert_list_equal(verbs, EXAMPLE_TEXT_2_VERBS)


def test_verb_lemmas_example_2():
    verbs = get_verbs(EXAMPLE_TEXT_2, lemmatize=True)
    assert_list_equal(verbs, EXAMPLE_TEXT_2_VERB_LEMMAS)


def test_nouns_example_1():
    nouns = get_nouns(EXAMPLE_TEXT_2)
    assert_list_equal(nouns, ['Associated', 'General', 'Contractors', 'America'])


def test_nouns_example_1_lemma():
    nouns = get_nouns(EXAMPLE_TEXT_2, lemmatize=True)
    assert_list_equal(nouns, ['Associated', 'General', 'Contractors', 'America'])


def test_adj_example_1():
    adjs = get_adjectives(EXAMPLE_TEXT_3)
    assert_list_equal(adjs, ['applicable',
                             'effective',
                             'navigable',
                             'other',
                             'own',
                             'such',
                             'local',
                             'necessary',
                             'local',
                             'such'])


def test_adj_example_1_lemma():
    adjs = get_adjectives(EXAMPLE_TEXT_3, lemmatize=True)
    assert_list_equal(adjs,
                      ['applicable', 'effective', 'navigable', 'other', 'own', 'such', 'local', 'necessary', 'local',
                       'such'])


def test_adv_example_1():
    advs = get_adverbs("shall promptly provide notice")
    assert_list_equal(advs, ['promptly'])


def test_adv_example_1_lemma():
    advs = get_adverbs("shall promptly provide notice", lemmatize=True)
    assert_list_equal(advs, ['promptly'])
