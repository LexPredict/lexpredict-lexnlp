#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Definition unit tests for English.

This module implements unit tests for the definition extraction functionality in English.

Todo:
    * Better testing for exact test in return sources
    * More pathological and difficult cases
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# Project imports
import datetime
import os
from unittest import TestCase

from lexnlp.extract.common.annotation_locator_type import AnnotationLocatorType
from lexnlp.extract.ml.environment import ENV_EN_DATA_DIRECTORY
from lexnlp.extract.en.definition_parsing_methods import trim_defined_term, NOUN_PTN_RE, get_definition_list_in_sentence
from lexnlp.extract.en.definitions import \
    get_definitions_explicit, get_definitions_in_sentence, get_definition_annotations, parser_ml_classifier, \
    get_definitions
from lexnlp.tests.utility_for_testing import load_resource_document


TRAINED_MODEL_PATH = os.path.join(ENV_EN_DATA_DIRECTORY, 'definition_model_layered.pickle.gzip')
parser_ml_classifier.load_compressed(TRAINED_MODEL_PATH)


class TestEnglishDefinitions(TestCase):
    def test_catastrophic_repetative_text(self):
        text = 'X' * 500
        start = datetime.datetime.now()
        defs = get_definition_list_in_sentence((0, len(text), text), False)
        elapsed = (datetime.datetime.now() - start).total_seconds()
        self.assertLess(elapsed, 2)
        self.assertEqual(0, len(defs))

    def test_trim_defined_term(self):
        term = 'this "Deed of Trust"'
        term_cleared, _, _, _ = trim_defined_term(term, 5, 31)
        self.assertEqual('Deed of Trust', term_cleared)

    def test_definition_quoted(self):
        sentence = '''THIS DEED OF TRUST, ASSIGNMENT, SECURITY AGREEMENT AND FINANCING
STATEMENT (this "Deed of Trust") dated August 29, 1997, is executed and
delivered by Trustor for good and valuable consideration, the receipt and
adequacy of which are hereby acknowledge by Trustor.'''
        definitions = list(get_definitions_explicit(sentence))
        self.assertEqual('Deed of Trust', definitions[0][0])

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
        definitions = list(get_definition_annotations(sentence))
        self.assertEqual(2, len(definitions))

    def test_obvious_embraced_definition(self):
        text = "and will be payable from Loan Repayments made by Stanford Health Care (the \"Corporation\") " + \
               "under the Loan Agreement and from certain funds\n" + "held under the Indenture."
        definitions = list(get_definition_annotations(text))
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
        definitions = list(get_definition_annotations(text))
        self.assertEqual(0, len(definitions))

        text = "Bonds in a commercial paper mode are remarketed for various periods that can be no longer than " + \
               "270 days and are established at the beginning of each commercial paper rate period."
        definitions = list(get_definition_annotations(text))
        self.assertEqual(0, len(definitions))

    def test_the_corporation_false_positive(self):
        text = "Corporation (as described below) and any other Obligations issued"
        definitions = list(get_definition_annotations(text))
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
        definitions = list(get_definition_annotations(text))
        self.assertEqual(3, len(definitions))
        for df in definitions:
            self.assertTrue('Obligation' in df.name)

    def test_capitalized_with_trigger(self):
        text = "Beneficial Owner means any Person which has or shares the power, directly " + \
               "or indirectly, to make\ninvestment decisions"
        definitions = list(get_definition_annotations(text))
        self.assertEqual(1, len(definitions))

    def test_capitalized_with_trigger_in_the_middle_of_sentense(self):
        text = "This is the intro Required Lenders means the people that agree to do the thing " \
               "with the detectthis and the quick brown fox jumps over the lazy dog."
        definitions = list(get_definition_annotations(text))
        self.assertEqual(1, len(definitions))
        text = 'This is the intro\n"Required Lenders" means the people that agree to do the thing ' \
               'with the detectthis and the quick brown fox jumps over the lazy dog.'
        definitions = list(get_definition_annotations(text))
        self.assertEqual(1, len(definitions))
        text = 'This is the intro “Required Lenders” means the people that agree to do the thing ' \
               'with the detectthis and the quick brown fox jumps over the lazy dog.'
        definitions = list(get_definition_annotations(text))
        self.assertEqual(1, len(definitions))

    def test_start_word_shall_be_false_positive(self):
        text = "Bonds shall be deemed to have been paid pursuant to the provisions of the Indenture"
        _ = list(get_definition_annotations(text))
        # self.assertEqual(0, len(definitions))
        print('Bonds shall be deemed to: false positive but OK for now')

    def test_reffered_to_def(self):
        text = """any such excess being referred to as a "Combined EBIDATA Deficit" """
        defs = list(get_definition_annotations(text))
        self.assertEqual(1, len(defs))

        text = '"Aggregate Revolving Loan Commitment" means the combined Revolving Loan Commitments of the United Earth'
        defs = list(get_definition_annotations(text))
        self.assertEqual(1, len(defs))

    def test_reffered_to_def_excess_words(self):
        text = '“Aggregate Delayed Draw Term Loan Ending Commitment” shall mean the combined Revolving Loan ' + \
               'Commitments of the Revolving Lenders, which shall initially on the Closing Date be in the amount ' + \
               'of $99,000,000, as such amount may be increased in accordance with Section 9.92(b).'
        defs = list(get_definition_annotations(text))
        self.assertEqual(0, len(defs))

    def test_too_long_definition(self):
        text = '''any such excess being referred to as a "Combined BISS Deficit Alpha Beta Gamma Cappa Zeta"'''
        defs = list(get_definition_annotations(text))
        self.assertEqual(0, len(defs))

        text = '''any such excess being referred to as a "Combined EDITT Deficit Alpha Beta Gamma Cappa"'''
        defs = list(get_definition_annotations(text))
        self.assertEqual(1, len(defs))

    def test_parse_moodys(self):
        text = '''together with any successor thereto, "Moody's"'''
        defs = list(get_definition_annotations(text))
        self.assertEqual(1, len(defs))

    def test_parse_in_extra_quotes(self):
        text = '''""Consolidated EBITDA" means, for any period, for the Company and its Subsidiaries ''' + \
               '''on a consolidated basis, an amount equal to Consolidated Net Income for such period'''
        defs = list(get_definition_annotations(text))
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
        defs = list(get_definition_annotations(text))
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
        defs = list(get_definition_annotations(text))
        self.assertGreater(len(defs), 12)
        self.assertLess(len(defs), 25)
        for df in defs:
            txt = df.name.strip('''"[]'{}.\t ''')
            self.assertGreater(len(txt), 0)
            txt = df.name.strip('''"[]'{}.\t ''')
            self.assertGreater(len(txt), 0)

    def test_apostrophe_in_definition(self):
        text = '''“Bankers’ Acceptance” or “BA” means a time draft'''
        definitions = sorted(list(get_definition_annotations(text)), key=lambda i: i.coords[0])
        self.assertEqual(definitions[0].name, "Bankers' Acceptance")
        self.assertEqual(definitions[1].name, 'BA')

    def test_dot_in_definition(self):
        text = '''“U.S. Person” means any Person that is a “United States Person” as defined 
                  in Section 7701(a)(30) of the Code.'''
        definitions = list(get_definition_annotations(text))
        self.assertEqual(definitions[0].name, 'U.S. Person')

    def test_trigger_word_fullmatches(self):
        text = '''(i)\nThe meanings given to terms defined herein shall be equally applicable to both\n
                  the singular and plural forms of such terms.'''
        definitions = list(get_definition_annotations(text))
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

        text = "(b) In the exercise of the authorities gcanted in subsection ' + \
            '(a) of this section, the term \"Agency\n" + \
            "head' shall mean the Director, the Deputy Director, or the Executive of the Agency."
        definitions = list(get_definition_annotations(text))
        self.assertEqual(len(definitions), 0)

    def test_emma(self):
        text = '''This website, emma.msrb.org, including the Electronic Municipal 
        Market Access (EMMA®) system and all subdomains and areas of this website, (the "Website")  
        is administered by the Municipal Securities Rulemaking Board ("MSRB", "we", "us" or "our").'''
        definitions = list(get_definition_annotations(text))
        self.assertEqual(len(definitions), 6)

    def test_misbrackets(self):
        text = '''
(bq) Subject to paragraph (e) below, a party may not take any step to:
(i) have an administrator appointed to the Trustee;
(ii) have a receiver appointed to the Trustee, other than a receiver of all or part of the assets of the Fund only;
(iii) have the Trustee wound up, or prove in any winding up of the Trustee;
(iv) obtain a judgement against the Trustee for the payment of money;
(v) carry out any distress or execution on any property of the Trustee; or
(A) right of set-off;
(B) right to combine or consolidate accounts; or
(C) banker's lien,
against the Trustee in connection with the Trustee's obligations under or in connection with this document.
        '''
        definitions = list(get_definition_annotations(text))
        self.assertEqual(0, len(definitions))

    def test_unpared_brackets(self):
        text = '''
         FATCA Application Date means:                                                                                                                                                                                                            
         0. in relation to a "withholdable payment" described in s 1473(1)(A)(i) of the Code (which relates
         to payments of interest and certain other payments from sources within the US), 1 July 2014;
         in relation to a "withholdable payment" described in s 1473(1)(A)(ii) of the Code (which relates to 
         "gross proceeds" from the disposition of property of a type that can produce interest from sources within 
         the US), 1 January 2019; or
         in relation to a "passthru payment" described in s 1471(d)(7) of the Code not falling within paragraphs
         (a) or (b), 1 January 2019,
         or, in each case, such other date from which such payment may become subject to a deduction or withholding
         required by FATCA as a result of any change in FATCA after the date of this Agreement.
        '''
        definitions = list(get_definition_annotations(text))
        self.assertEqual(1, len(definitions))
        self.assertEqual('FATCA Application Date', definitions[0].name)

    def test_merge_defs(self):
        text = '("MSRB", "we", "us" or "our").'
        definitions = list(get_definition_annotations(text))
        self.assertEqual(4, len(definitions))

    def test_merge_defs_consumed(self):
        text = '(each an “Obligation” and collectively, the “Obligations”)'
        definitions = list(get_definition_annotations(text))
        self.assertEqual(2, len(definitions))

    def test_newlines(self):
        text = """
“Interest Coverage Ratio” means, for any period of four consecutive fiscal quarters of the Borrower, the ratio of
Adjusted Funds From Operations for such period to Net Interest Expense for such period.
“Interest Expense” means, for any
period, “interest expense” as shown on a consolidated statement of income of the Borrower for such period prepared in accordance with GAAP plus Interest Expense to Affiliates for such period.
“Interest Expense to Affiliates” means, for any period, “Interest Expense to Affiliates” as shown on a consolidated statement
of income of the Borrower for such period.        
        """
        definitions = list(get_definition_annotations(text))
        self.assertEqual(3, len(definitions))

        text = "“Interest Coverage Ratio” means, for any period of four consecutive fiscal quarters of the Borrower, " + \
               "the ratio of Adjusted Funds From Operations for such period to Net Interest Expense for such period. " + \
               "“Interest Expense” means, for any " + \
               "period, “interest expense” as shown on a consolidated statement of income of the Borrower for such " + \
               "period prepared in accordance with GAAP plus Interest Expense to Affiliates for such period. " + \
               "“Interest Expense to Affiliates” means, for any period, “Interest Expense to Affiliates” as shown " + \
               "on a consolidated statement of income of the Borrower for such period."

        definitions = list(get_definition_annotations(text))
        self.assertEqual(3, len(definitions))

    def test_enquoted(self):
        text = 'increase or otherwise modify Facility LCs ("Modify," and each such action a "Modification") ' + \
               'for the Borrower, from time to time from the date'
        definitions = list(get_definition_annotations(text))
        self.assertEqual(3, len(definitions))

    def test_quotes_removed(self):
        text = '(each an “Obligation” and collectively, the “Obligations”)'
        definitions = list(get_definition_annotations(text))
        definitions.sort(key=lambda d: d.coords[0])
        self.assertEqual(2, len(definitions))
        self.assertEqual((10, 20), definitions[0].coords)
        self.assertEqual((45, 56), definitions[1].coords)

    def test_definition_ml(self):
        sentence = '''THIS DEED OF TRUST, ASSIGNMENT, SECURITY AGREEMENT AND FINANCING
        STATEMENT (this "Deed of Trust") dated August 29, 1997, is executed and
        delivered by Trustor for good and valuable consideration, the receipt and
        adequacy of which are hereby acknowledge by Trustor.'''
        _ = list(get_definition_annotations(sentence,
                                            locator_type=AnnotationLocatorType.MlWordVectorBased))
        # self.assertGreater(len(definitions), 0)
        # self.assertEqual('Deed of Trust', definitions[0].name)

    def test_overlapping_defs(self):
        text = load_resource_document(
            'lexnlp/extract/en/tests/test_definitions/bad_def.txt', 'utf-8')
        defs = list(get_definitions(text))
        self.assertGreater(len(defs), 12)

    def test_superscript_numerical(self):
        text = "“Definiendum”²³ shall mean a word, phrase, or symbol which is the subject of a definition."
        definitions = list(get_definitions(text))
        self.assertEqual(1, len(definitions))

    def test_subscript_numerical(self):
        text = "“Definiendum”₁ shall mean a word, phrase, or symbol which is the subject of a definition."
        definitions = list(get_definitions(text))
        self.assertEqual(1, len(definitions))

    def test_superscript_alphabetical_lower(self):
        text = "“Definiendum”ᵃ shall mean a word, phrase, or symbol which is the subject of a definition."
        definitions = list(get_definitions(text))
        self.assertEqual(1, len(definitions))

    def test_superscript_alphabetical_upper(self):
        text = "“Definiendum”ᴮ shall mean a word, phrase, or symbol which is the subject of a definition."
        definitions = list(get_definitions(text))
        self.assertEqual(1, len(definitions))

    def test_subscript_alphabetical_lower(self):
        text = "“Definiendum”ₐ shall mean a word, phrase, or symbol which is the subject of a definition."
        definitions = list(get_definitions(text))
        self.assertEqual(1, len(definitions))

    def test_subscript_alphabetical_upper(self):
        text = "“Definiendum”ₜ shall mean a word, phrase, or symbol which is the subject of a definition."
        definitions = list(get_definitions(text))
        self.assertEqual(1, len(definitions))

