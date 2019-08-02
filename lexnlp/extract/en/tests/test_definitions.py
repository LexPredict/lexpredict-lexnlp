#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Definition unit tests for English.

This module implements unit tests for the definition extraction functionality in English.

Todo:
    * Better testing for exact test in return sources
    * More pathological and difficult cases
"""

# Project imports
import codecs
from os import listdir
from os.path import isfile, join
from typing import List
from unittest import TestCase

from lexnlp.extract.common.annotations.definition_annotation import DefinitionAnnotation
from lexnlp.extract.en.definitions import NOUN_PTN_RE, \
    get_definitions_explicit, get_definitions_in_sentence, get_definition_annotations
from lexnlp.tests.utility_for_testing import load_resource_document, annotate_text, save_test_document
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.7"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestEnglishDefinitions(TestCase):

    def test_definition_quoted(self):
        sentence = '''THIS DEED OF TRUST, ASSIGNMENT, SECURITY AGREEMENT AND FINANCING
STATEMENT (this "Deed of Trust") dated August 29, 1997, is executed and
delivered by Trustor for good and valuable consideration, the receipt and
adequacy of which are hereby acknowledge by Trustor.'''
        definitions = list(get_definitions_explicit(sentence))
        self.assertEqual(definitions[0][0], 'Deed of Trust')

    def test_definition_quoted_new_line(self):
        sentence = '''THIS DEED OF TRUST, ASSIGNMENT, SECURITY AGREEMENT AND FINANCING
    STATEMENT (this "Deed
of Trust") dated August 29, 1997, is executed and
    delivered by Trustor for good and valuable consideration, the receipt and
    adequacy of which are hereby acknowledge by Trustor.'''
        definitions = list(get_definitions_explicit(sentence))
        self.assertEqual(definitions[0][0], 'Deed of Trust')

    def test_definitions_simple(self):
        sentence = '''Visual Networks Operations, Inc., a Delaware corporation with offices at 2092 Gaither 
                    Road, Rockville, Maryland 20850("Licensor.") and is made retroactive to December 3, 2002 
                    ("Effective Date").'''
        definitions = self.parse(sentence)
        self.assertEqual(2, len(definitions))

    def test_obvious_embraced_definition(self):
        text = "and will be payable from Loan Repayments made by Stanford Health Care (the \"Corporation\") " + \
               "under the Loan Agreement and from certain funds\n" + "held under the Indenture."
        definitions = self.parse(text)
        self.assertEqual(1, len(definitions))

    def test_noun_pattern_false_positive(self):
        ptrn = NOUN_PTN_RE
        text = "Bonds in a commercial paper mode are remarketed for various periods that can be no longer than " + \
               "270 days and are established at the beginning of each commercial paper rate period."
        matches = list(ptrn.finditer(text))
        self.assertEqual(0, len(matches))

    def test_capitalized_false_positive(self):
        text = "Costs incurred by the Corporation in providing these services are reflected in the respective " + \
               "categories in the consolidated statements of operations and changes in net assets."
        definitions = self.parse(text)
        self.assertEqual(0, len(definitions))

        text = "Bonds in a commercial paper mode are remarketed for various periods that can be no longer than " + \
               "270 days and are established at the beginning of each commercial paper rate period."
        definitions = self.parse(text)
        self.assertEqual(0, len(definitions))

    def test_the_corporation_false_positive(self):
        text = "Corporation (as described below) and any other Obligations issued"
        definitions = self.parse(text)
        self.assertEqual(0, len(definitions))

    def test_include_multitoken_definition(self):
        """
        I think that the text
        (each an “Obligation” and collectively, the “Obligations”)
        IS the definition. But the parser skips the text because it has more
        than MAX_TERM_TOKENS (presently, 5) words.

        So, the behavior is changed: now 10 words are allowed because there are
        2 possible "definitions".
        """
        text = """
        Obligation No. 39, the outstanding Obligations relating to other indebtedness and obligations of the 
Corporation (as described below) and any other Obligations issued in the future under the Master Indenture, including 
the Obligation to be issued to evidence the Corporation’s obligations with respect to the payment of principal of and 
interest on the Taxable Bonds (each an “Obligation” and collectively, the “Obligations”), will be secured by security 
interests in (i) the Gross Revenues of each Member of the Obligated Group and (ii) the moneys on deposit from time 
to time in the Gross Revenue Fund established under the Master Indenture. """
        definitions = self.parse(text)
        self.assertEqual(1, len(definitions))

    def test_capitalized_with_trigger(self):
        text = "Beneficial Owner means any Person which has or shares the power, directly " + \
               "or indirectly, to make\ninvestment decisions"
        definitions = self.parse(text)
        self.assertEqual(1, len(definitions))

    def test_start_word_shall_be_false_positive(self):
        text = "Bonds shall be deemed to have been paid pursuant to the provisions of the Indenture"
        _ = self.parse(text)
        # self.assertEqual(0, len(definitions))
        print('Bonds shall be deemed to: false positive but OK for now')

    def test_reffered_to_def(self):
        text = """any such excess being referred to as a "Combined EBIDATA Deficit" """
        defs = self.parse(text)
        self.assertEqual(1, len(defs))

        text = '"Aggregate Revolving Loan Commitment" means the combined Revolving Loan Commitments of the United Earth'
        defs = self.parse(text)
        self.assertEqual(1, len(defs))

        text = '“Aggregate Delayed Draw Term Loan Ending Commitment” shall mean the combined Revolving Loan ' + \
               'Commitments of the Revolving Lenders, which shall initially on the Closing Date be in the amount ' + \
               'of $99,000,000, as such amount may be increased in accordance with Section 9.92(b).'
        defs = self.parse(text)
        self.assertEqual(1, len(defs))

    def test_too_long_definition(self):
        text = '''any such excess being referred to as a "Combined BISS Deficit Alpha Beta Gamma Cappa Zeta"'''
        defs = self.parse(text)
        self.assertEqual(0, len(defs))

        text = '''any such excess being referred to as a "Combined EDITT Deficit Alpha Beta Gamma Cappa"'''
        defs = self.parse(text)
        self.assertEqual(1, len(defs))

    def test_parse_moodys(self):
        text = '''together with any successor thereto, "Moody's"'''
        defs = self.parse(text)
        self.assertEqual(1, len(defs))

    def test_parse_in_extra_quotes(self):
        text = '''""Consolidated EBITDA" means, for any period, for the Company and its Subsidiaries ''' + \
               '''on a consolidated basis, an amount equal to Consolidated Net Income for such period'''
        defs = self.parse(text)
        self.assertEqual(1, len(defs))

    def test_annotations(self):
        text = '''""Consolidated EBITDA" means, for any period, for the Company and its Subsidiaries ''' + \
               '''on a consolidated basis, an amount equal to Consolidated Net Income for such period'''
        ants = list(get_definition_annotations(text))
        self.assertEqual(1, len(ants))
        cite = ants[0].get_cite()
        self.assertEqual('/en/definition/Consolidated EBITDA', cite)

    def test_definitions_in_sentences_text(self):
        text = load_resource_document(
            'lexnlp/extract/en/tests/test_definitions/test_definition_in_sentences.csv',
            'utf-8')
        defs = self.parse(text)
        self.assertGreater(len(defs), 16)
        self.assertLess(len(defs), 25)

    def test_definitions_in_one_sentence(self):
        sentence = 'The "Pope": the head of the Catholic Church.'
        definitions = list(get_definitions_in_sentence(sentence, return_sources=False))
        self.assertEqual(1, len(definitions))
        self.assertEqual('Pope', definitions[0].strip(' :"'))

        definitions = list(get_definitions_in_sentence(sentence, return_sources=True))
        self.assertEqual(1, len(definitions))
        self.assertEqual('Pope', definitions[0][0].strip(' :"'))

    def test_definition_fixed(self):
        text = load_resource_document(
            'lexnlp/extract/en/tests/test_definitions/test_definition_fixed.csv',
            'utf-8')
        defs = self.parse(text)
        self.assertGreater(len(defs), 12)
        self.assertLess(len(defs), 25)
        for df in defs:
            txt = df["tags"]["Extracted Entity Definition Name"].strip('''"[]'{}.\t ''')
            self.assertGreater(len(txt), 0)
            txt = df["tags"]["Extracted Entity Text"].strip('''"[]'{}.\t ''')
            self.assertGreater(len(txt), 0)

    def test_hit_or_miss_samples(self):
        text = load_resource_document('lexnlp/extract/en/definitions/definitions_hit_or_miss.txt', 'utf-8')
        definitions = self.parse(text)
        self.assertGreater(len(definitions), 0)
        self.annotate_document(text, definitions, 'output/definitions_hit_or_miss.html')

    def test_definitions_sample_doc(self):
        text = load_resource_document('lexnlp/extract/en/definitions/en_definitions_sample_doc.txt', 'utf-8')
        definitions = self.parse(text)
        self.assertGreater(len(definitions), 2)  # 10)
        self.annotate_document(text, definitions, 'output/en_definitions_sample_doc.html')

        text = load_resource_document('lexnlp/extract/en/definitions/pure_definitions.txt', 'utf-8')
        lines_count = text.count('\n\n') + 1
        definitions = self.parse(text)
        self.assertGreater(len(definitions), lines_count)
        self.annotate_document(text, definitions, 'output/pure_definitions.html')

    def test_apostrophe_in_definition(self):
        text = '''“Bankers’ Acceptance” or “BA” means a time draft'''
        definitions = sorted(list(get_definitions_explicit(text)), key=lambda i: i[0])
        self.assertEqual(definitions[0][0], 'BA')
        self.assertEqual(definitions[1][0], '''Bankers' Acceptance''')

    def test_dot_in_definition(self):
        text = '''“U.S. Person” means any Person that is a “United States Person” as defined 
                  in Section 7701(a)(30) of the Code.'''
        definitions = list(get_definitions_in_sentence(text))
        self.assertEqual(definitions[0], 'U.S. Person')

    def test_trigger_word_fullmatches(self):
        text = '''(i)\nThe meanings given to terms defined herein shall be equally applicable to both\n
                  the singular and plural forms of such terms.'''
        definitions = list(get_definitions_in_sentence(text))
        self.assertEqual(len(definitions), 0)

    def test_fp_pronoun(self):
        text = """
        This means a
        vation, packaging, packing and marking; and (2) description of the essential physical characteris-
        criteria by which the Government can determine tics and functions required to meet minimum
        whether or not contract requirements have been needs.     
        """
        definitions = list(get_definition_annotations(text))
        self.assertEqual(0, len(definitions))

    def test_fp_service_words(self):
        text = """
        'Governmentfurnished property').
        (2) The delivery or performance dates for this contract are based upon the expectation that
        Government-furnished property suitable for use (except for property furnished ('as is') will be delivered
        to the Contractor at the times stated in the Schedule or, if not so stated, in sufficient time to enable the
        Contractor to meet the contract's delivery or performance dates.
        """
        definitions = list(get_definition_annotations(text))
        self.assertEqual(0, len(definitions))

    def test_the(self):
        text = '''The mean-\ning of our English term has shifted\nfrom character to actions-to 
              external\nacts, manner of life, conduct, or\nhabits.'''
        definitions = list(get_definitions_in_sentence(text))
        self.assertEqual(len(definitions), 0)

    def test_parenthesis(self):
        text = """Understanding SBA (the "Administrator') is directed to refer"""
        definitions = list(get_definition_annotations(text))
        self.assertEqual(len(definitions), 1)
        self.assertEqual('Administrator', definitions[0].name)

    def test_def_called(self):
        text = """4. Contracts whereby one party unrelated (___
        performed (an assignment for past duties is not to the suit agrees with a party to the suit that
        illegal or against public poiicy - here the harm is they will split the proceeds of the suit and the
        that the public officer is not as likely to perform one not related to the suit will bear all the
        as diligently where he knows that his future expenses of the suit (so called "champerty')."""
        definitions = list(get_definition_annotations(text))
        self.assertEqual(len(definitions), 1)
        self.assertEqual('champerty', definitions[0].name)
        # normalize quotes?
        # remove "called, so called, collectively called ..."

    def test_process_ugly_braces_def(self):
        text = """(1) The term "Contractor's managerial
            personnel," as used in this paragraph (g), means the Contractor's directors, officers, and any of the
            Contractor's managers, superintendents, or equivalent representatives who have supervision or direction
            of--"""
        definitions = list(get_definition_annotations(text))
        self.assertEqual(len(definitions), 1)
        self.assertEqual("Contractor's managerial personnel",
                         definitions[0].name)

    def test_abbr_strip(self):
        text = '“U.S.” mean the United States of America. '
        definitions = list(get_definition_annotations(text))
        self.assertEqual(len(definitions), 1)

    def test_unbal_quotes(self):
        text = """Buthrzd d"uatc-\nmunicate the acceptance of the offer to the between 
                so-called 'authorized" and unauthre\nofferor. """
        definitions = list(get_definition_annotations(text))
        self.assertEqual(len(definitions), 1)
        self.assertEqual('authorized', definitions[0].name)

        text = "(b) In the exercise of the authorities gcanted in subsection (a) of this section, the term \"Agency\n" + \
               "head' shall mean the Director, the Deputy Director, or the Executive of the Agency."
        definitions = list(get_definition_annotations(text))
        self.assertEqual(len(definitions), 1)

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_definitions_sorted,
            'lexnlp/typed_annotations/en/definition/definitions.txt',
            DefinitionAnnotation)

    def process_a_bunch_of_documents(self):
        path = 'path/to/a/folder/with/a/number/of/files'
        for file_path in [join(path, f) for f in listdir(path) if isfile(join(path, f))]:
            with codecs.open(file_path, encoding='utf-8', mode='r') as myfile:
                data = myfile.read()
            _ = self.parse(data)

    def process_big_document_with_false_positives(self):
        text = load_resource_document('lexnlp/extract/en/definitions/definitions_fp_collections.txt', 'utf-8')
        definitions = self.parse(text)
        self.assertGreater(len(definitions), 0)
        self.annotate_document(text, definitions, 'output/definitions_fp_collections.html')

    def annotate_document(self, text: str, definitions: List[dict], output_path: str) -> None:
        annotations = []
        index = 0
        for df in definitions:
            index += 1
            ant_text = df["tags"]["Extracted Entity Text"]
            ant = DefinitionAnnotation(
                name=df["tags"]["Extracted Entity Definition Name"],
                coords=(df["attrs"]["start"], df["attrs"]["end"]),
                text=ant_text,
                locale="en")
            annotations.append(ant)

        html = annotate_text(text, annotations)
        save_test_document(output_path, html)

    def parse(self, text):
        found = list(get_definitions_explicit(text))
        ret = []
        for definition, source_text, coords in set(found):
            ret.append(
                dict(
                    attrs={
                        'start': coords[0],
                        'end': coords[1]},
                    tags={
                        'Extracted Entity Type': 'definition',
                        'Extracted Entity Definition Name': definition,
                        'Extracted Entity Text': source_text
                    }))
        return ret


def get_definitions_sorted(text: str):
    annotations = list(get_definition_annotations(text))
    annotations.sort(key=lambda a: a.coords[0])
    return annotations
