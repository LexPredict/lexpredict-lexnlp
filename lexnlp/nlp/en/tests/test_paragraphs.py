#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Imports
import string

# Test imports
from nose.tools import assert_dict_equal, nottest

# Project imports
from lexnlp.nlp.en.segments.paragraphs import get_paragraphs
from lexnlp.nlp.en.segments.utils import build_document_distribution

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

DOCUMENT_EXAMPLE_1 = "this is a test 123!"
DOCUMENT_EXAMPLE_1_RESULT_LC = {'doc_char_s': 0.2727272727272727, 'doc_char_p': 0.0, 'doc_char_a': 0.09090909090909091,
                                'doc_char_f': 0.0, 'doc_char_q': 0.0, 'doc_char_j': 0.0, 'doc_char_z': 0.0,
                                'doc_char_n': 0.0, 'doc_char_r': 0.0, 'doc_char_m': 0.0, 'doc_char_y': 0.0,
                                'doc_char_t': 0.2727272727272727, 'doc_char_b': 0.0, 'doc_char_w': 0.0,
                                'doc_char_v': 0.0, 'doc_char_c': 0.0, 'doc_char_h': 0.09090909090909091,
                                'doc_char_i': 0.18181818181818182, 'doc_char_e': 0.09090909090909091, 'doc_char_k': 0.0,
                                'doc_char_x': 0.0, 'doc_char_g': 0.0, 'doc_char_l': 0.0, 'doc_char_d': 0.0,
                                'doc_char_o': 0.0, 'doc_char_u': 0.0}
DOCUMENT_EXAMPLE_1_RESULT_DI = {'doc_char_1': 0.3333333333333333, 'doc_char_3': 0.3333333333333333,
                                'doc_char_2': 0.3333333333333333, 'doc_char_6': 0.0, 'doc_char_0': 0.0,
                                'doc_char_7': 0.0, 'doc_char_9': 0.0, 'doc_char_5': 0.0, 'doc_char_4': 0.0,
                                'doc_char_8': 0.0}
DOCUMENT_EXAMPLE_1_RESULT_CUSTOM = {'doc_char_1': 0.3333333333333333, 'doc_char_3': 0.3333333333333333,
                                    'doc_char_2': 0.3333333333333333}
DOCUMENT_EXAMPLE_1_RESULT_CUSTOM_NO_NORM = {'doc_char_1': 1, 'doc_char_3': 1, 'doc_char_2': 1}
DOCUMENT_EXAMPLE_1_RESULT_PRINT = {'doc_char_1': 0.05263157894736842, 'doc_char_Q': 0.0, 'doc_char_y': 0.0,
                                   'doc_char_W': 0.0, 'doc_char_6': 0.0, 'doc_char_j': 0.0, 'doc_char_|': 0.0,
                                   'doc_char_n': 0.0, 'doc_char_?': 0.0, 'doc_char_4': 0.0, 'doc_char__': 0.0,
                                   'doc_char_m': 0.0, 'doc_char_Y': 0.0, 'doc_char_E': 0.0, 'doc_char_[': 0.0,
                                   'doc_char_b': 0.0, 'doc_char_O': 0.0, 'doc_char_K': 0.0, 'doc_char_`': 0.0,
                                   'doc_char_h': 0.05263157894736842, 'doc_char_"': 0.0, 'doc_char_U': 0.0,
                                   'doc_char_B': 0.0, 'doc_char_V': 0.0, 'doc_char_%': 0.0, 'doc_char_8': 0.0,
                                   'doc_char_!': 0.05263157894736842, 'doc_char_<': 0.0, 'doc_char_(': 0.0,
                                   'doc_char_,': 0.0, 'doc_char_w': 0.0, 'doc_char_*': 0.0, 'doc_char_g': 0.0,
                                   'doc_char_H': 0.0, 'doc_char_I': 0.0, 'doc_char_/': 0.0,
                                   'doc_char_ ': 0.21052631578947367, 'doc_char_\x0c': 0.0, 'doc_char_L': 0.0,
                                   'doc_char_-': 0.0, 'doc_char_\\': 0.0, 'doc_char_9': 0.0, 'doc_char_5': 0.0,
                                   'doc_char_N': 0.0, 'doc_char_>': 0.0, 'doc_char_7': 0.0, 'doc_char_$': 0.0,
                                   'doc_char_\r': 0.0, 'doc_char_i': 0.10526315789473684, 'doc_char_\n': 0.0,
                                   'doc_char_.': 0.0, 'doc_char_k': 0.0, 'doc_char_C': 0.0, 'doc_char_R': 0.0,
                                   'doc_char_u': 0.0, 'doc_char_p': 0.0, 'doc_char_f': 0.0, 'doc_char_q': 0.0,
                                   'doc_char_3': 0.05263157894736842, 'doc_char_z': 0.0, 'doc_char_F': 0.0,
                                   'doc_char_r': 0.0, 'doc_char_M': 0.0, 'doc_char_;': 0.0,
                                   'doc_char_a': 0.05263157894736842, 'doc_char_D': 0.0,
                                   'doc_char_t': 0.15789473684210525, "doc_char_'": 0.0, 'doc_char_x': 0.0,
                                   'doc_char_X': 0.0, 'doc_char_~': 0.0, 'doc_char_:': 0.0, 'doc_char_&': 0.0,
                                   'doc_char_{': 0.0, 'doc_char_o': 0.0, 'doc_char_l': 0.0, 'doc_char_d': 0.0,
                                   'doc_char_^': 0.0, 'doc_char_s': 0.15789473684210525, 'doc_char_S': 0.0,
                                   'doc_char_}': 0.0, 'doc_char_v': 0.0, 'doc_char_+': 0.0, 'doc_char_P': 0.0,
                                   'doc_char_T': 0.0, 'doc_char_\t': 0.0, 'doc_char_0': 0.0, 'doc_char_G': 0.0,
                                   'doc_char_#': 0.0, 'doc_char_=': 0.0, 'doc_char_\x0b': 0.0, 'doc_char_]': 0.0,
                                   'doc_char_c': 0.0, 'doc_char_A': 0.0, 'doc_char_e': 0.05263157894736842,
                                   'doc_char_2': 0.05263157894736842, 'doc_char_J': 0.0, 'doc_char_)': 0.0,
                                   'doc_char_@': 0.0, 'doc_char_Z': 0.0}

# Real world example 2
DOCUMENT_EXAMPLE_2 = """SECTION 1.1. LINE OF CREDIT.

(a) Line of Credit. Subject to the terms and conditions of this
Agreement, Bank hereby agrees to make advances to Borrower from time to time up
to and including May 1, 1998, not to exceed at any time the aggregate principal
amount of Twenty Million Dollars ($20,000,000.00) ("Line of Credit"), the
proceeds of which shall be used for working capital purposes. Borrower's
obligation to repay advances under the Line of Credit shall be evidenced by a
promissory note substantially in the form of Exhibit A attached hereto ("Line of
Credit Note"), all terms of which are incorporated herein by this reference.

(b) Subfeature. Subject to the terms and conditions of this Agreement,
Bank hereby agrees to make advances to Smart(Europe) from time to time up to and
including May 1, 1998, not to exceed at any time the aggregate principal amount
of Ten Million Dollars ($10,000,000.00) ("Subfeature"), the proceeds of which
shall be used for working capital purposes. Smart(Europe)'s obligation to repay
advances under the Subfeature shall be evidenced by a promissory note
substantially in the form of Exhibit B attached hereto ("Smart (Europe) Note"),
all terms of which are incorporated herein by this reference. The outstanding
principal balance of advances and the available undrawn balance of Letters of
Credit issued under the Subfeature


<PAGE>   2
shall be reserved under the Line of Credit and shall not be available for
advances or Letters of Credit thereunder.

(c) Letter of Credit Subfeature. As a subfeature under the Line of
Credit and Subfeature, Bank agrees from time to time during the term thereof to
issue sight commercial and standby letters of credit for the account of Borrower
or Smart(Europe), respectively, to finance working capital and business
requirements (each, a "Letter of Credit" and collectively, "Letters of Credit");
provided however, that the form and substance of each Letter of Credit shall be
subject to approval by Bank, in its sole discretion; and provided further, that
the aggregate undrawn amount of all outstanding Letters of Credit shall not at
any time exceed Four Million Dollars ($4,000,000.00). No Letter of Credit shall
have an expiration date subsequent to the maturity date of the Line of Credit.
The undrawn amount of all Letters of Credit for the account of Borrower shall be
reserved under the Line of Credit and the undrawn amount of all Letters of
Credit for the account of Smart(Europe) shall be reserved under the Subfeature
and shall not be available for borrowings thereunder. Each Letter of Credit
shall be subject to the additional terms and conditions of the Letter of Credit
Agreement and related documents, if any, required by Bank in connection with the
issuance thereof (each, a "Letter of Credit Agreement" and collectively, "Letter
of Credit Agreements"). Each draft paid by Bank under a Letter of Credit shall
be deemed an advance under the Line of Credit or Subfeature, as applicable, and
shall be repaid by Borrower or Smart(Europe), in accordance with the terms and
conditions of this Agreement applicable to such advances; provided however, that
if advances under the Line of Credit or Subfacility, as applicable, are not
available, for any reason, at the time any draft is paid by Bank, then Bank
shall so notify Borrower or Smart(Europe), as applicable, and Borrower or
Smart(Europe) shall immediately pay to Bank the full amount of such draft,
together with interest thereon from the date such amount is paid by Bank to the
date such amount is fully repaid by Borrower or Smart(Europe), at the rate of
interest applicable to advances under the Line of Credit. In such event Borrower
agrees that Bank, in its sole discretion, may debit any demand deposit account
maintained by Borrower with Bank for the amount of any such draft.

(d) Borrowing and Repayment. Borrower or Smart(Europe) may from time to
time during the terms of the Line of Credit and Subfeature, respectively borrow,
partially or wholly repay its outstanding borrowings, and reborrow, subject to
all of the limitations, terms and conditions contained herein or in the Line of
Credit Note and Smart(Europe) Note, respectively; provided however, that the
total outstanding borrowings under the Line of Credit an Subfeature shall not at
any time exceed the respective



<PAGE>   3

"""

DOCUMENT_EXAMPLE_2_RESULT = [
    'SECTION 1.1. LINE OF CREDIT.',
    '(a) Line of Credit. Subject to the terms and conditions of this Agreement, Bank hereby agrees to make advances to '
    'Borrower from time to time up to and including May 1, 1998, not to exceed at any time the aggregate principal '
    'amount of Twenty Million Dollars ($20,000,000.00) ("Line of Credit"), the proceeds of which shall be used for '
    'working capital purposes. Borrower\'s obligation to repay advances under the Line of Credit shall be evidenced by '
    'a promissory note substantially in the form of Exhibit A attached hereto ("Line of Credit Note"), all terms of '
    'which are incorporated herein by this reference.',
    '(b) Subfeature. Subject to the terms and conditions of this Agreement, Bank hereby agrees to make advances to '
    'Smart(Europe) from time to time up to and including May 1, 1998, not to exceed at any time the aggregate '
    'principal amount of Ten Million Dollars ($10,000,000.00) ("Subfeature"), the proceeds of which shall be used for '
    'working capital purposes. Smart(Europe)\'s obligation to repay advances under the Subfeature shall be evidenced '
    'by a promissory note substantially in the form of Exhibit B attached hereto ("Smart (Europe) Note"), all terms '
    'of which are incorporated herein by this reference. The outstanding principal balance of advances and the '
    'available undrawn balance of Letters of Credit issued under the Subfeature',
    '<PAGE>   2 shall be reserved under the Line of Credit and shall not be available for advances or Letters of '
    'Credit thereunder.',
    '(c) Letter of Credit Subfeature. As a subfeature under the Line of Credit and Subfeature, Bank agrees from time '
    'to time during the term thereof to issue sight commercial and standby letters of credit for the account of '
    'Borrower or Smart(Europe), respectively, to finance working capital and business requirements (each, a "Letter '
    'of Credit" and collectively, "Letters of Credit"); provided however, that the form and substance of each Letter '
    'of Credit shall be subject to approval by Bank, in its sole discretion; and provided further, that the aggregate '
    'undrawn amount of all outstanding Letters of Credit shall not at any time exceed Four Million Dollars '
    '($4,000,000.00). No Letter of Credit shall have an expiration date subsequent to the maturity date of the Line '
    'of Credit. The undrawn amount of all Letters of Credit for the account of Borrower shall be reserved under the '
    'Line of Credit and the undrawn amount of all Letters of Credit for the account of Smart(Europe) shall be '
    'reserved under the Subfeature and shall not be available for borrowings thereunder. Each Letter of Credit shall '
    'be subject to the additional terms and conditions of the Letter of Credit Agreement and related documents, if '
    'any, required by Bank in connection with the issuance thereof (each, a "Letter of Credit Agreement" and '
    'collectively, "Letter of Credit Agreements"). Each draft paid by Bank under a Letter of Credit shall be deemed '
    'an advance under the Line of Credit or Subfeature, as applicable, and shall be repaid by Borrower or '
    'Smart(Europe), in accordance with the terms and conditions of this Agreement applicable to such advances; '
    'provided however, that if advances under the Line of Credit or Subfacility, as applicable, are not available, '
    'for any reason, at the time any draft is paid by Bank, then Bank shall so notify Borrower or Smart(Europe), as '
    'applicable, and Borrower or Smart(Europe) shall immediately pay to Bank the full amount of such draft, together '
    'with interest thereon from the date such amount is paid by Bank to the date such amount is fully repaid by '
    'Borrower or Smart(Europe), at the rate of interest applicable to advances under the Line of Credit. In such '
    'event Borrower agrees that Bank, in its sole discretion, may debit any demand deposit account maintained by '
    'Borrower with Bank for the amount of any such draft.',
    '(d) Borrowing and Repayment. Borrower or Smart(Europe) may from time to time during the terms of the Line of '
    'Credit and Subfeature, respectively borrow, partially or wholly repay its outstanding borrowings, and reborrow, '
    'subject to all of the limitations, terms and conditions contained herein or in the Line of Credit Note and '
    'Smart(Europe) Note, respectively; provided however, that the total outstanding borrowings under the Line of '
    'Credit an Subfeature shall not at any time exceed the respective',
    '<PAGE>   3'
]

DOCUMENT_EXAMPLE_3 = """
12. It is understood and agreed by the parties that this is a compromise agreement and that the furnishing by the 
Company of the consideration for this Agreement shall not be deemed or construed as an admission of liability or 
wrongdoing. The liability for any and all released claims is expressly denied by the Company.

13. No breach of any provision hereof can be waived unless in writing. Waiver
of any one breach of any provision hereof shall not be deemed to be a waiver of any other breach of the same or any 
other provision hereof.

14. This Agreement is to be interpreted without regard to the draftsman. The terms and intent of this Agreement, with 
respect to the rights and obligations of the parties, shall be interpreted and construed on the express assumption that 
each party participated equally in its drafting.

15. Employee represents and certifies that he/she has carefully read and fully understands all of the provisions and 
effects of this Agreement, and that he/she is voluntarily entering into this Agreement free of any duress or coercion.
"""

DOCUMENT_EXAMPLE_3_RESULT = [
    "12. It is understood and agreed by the parties that this is a compromise agreement and that the furnishing by "
    "the Company of the consideration for this Agreement shall not be deemed or construed as an admission of "
    "liability or wrongdoing. The liability for any and all released claims is expressly denied by the Company.",
    "13. No breach of any provision hereof can be waived unless in writing. Waiver of any one breach of any "
    "provision hereof shall not be deemed to be a waiver of any other breach of the same or any other provision "
    "hereof.",
    "14. This Agreement is to be interpreted without regard to the draftsman. The terms and intent of this Agreement, "
    "with respect to the rights and obligations of the parties, shall be interpreted and construed on the express "
    "assumption that each party participated equally in its drafting.",
    "15. Employee represents and certifies that he/she has carefully read and fully understands all of the provisions "
    "and effects of this Agreement, and that he/she is voluntarily entering into this Agreement free of any duress "
    "or coercion."
]

# Real example 3
DOCUMENT_EXAMPLE_4 = """10.2  Licensor Indemnities. Licensor agrees to indemnify, hold harmless
and defend Broderbund from all claims, liabilities, damages, defense costs
(including reasonable attorneys' fees), judgments and other expenses arising out
of or on account of:

(a) the alleged infringement or violation of any copyright,
patent right, right of publicity or privacy (including but not limited to
defamation), trademark, trade secret or other proprietary right with respect to
the Products, except to the extent such claim is based on Broderbund's actions
that modify or alter the Products or any of their trademarks;

(b) any unfair trade practice, defamation or misrepresentation
claim based on any promotional material, packaging, documentation or other
materials provided by Licensor with respect to the Products, except to the
extent such claim is based on Broderbund's actions that modify or alter the
Products; and

(c) the breach of any covenant, representation or warranty set
forth in this Agreement."""

DOCUMENT_EXAMPLE_4_RESULT = ["""10.2  Licensor Indemnities. Licensor agrees to indemnify, hold harmless
and defend Broderbund from all claims, liabilities, damages, defense costs
(including reasonable attorneys' fees), judgments and other expenses arising out
of or on account of:""",
                             """(a) the alleged infringement or violation of any copyright,
patent right, right of publicity or privacy (including but not limited to
defamation), trademark, trade secret or other proprietary right with respect to
the Products, except to the extent such claim is based on Broderbund's actions
that modify or alter the Products or any of their trademarks;""",
                             """(b) any unfair trade practice, defamation or misrepresentation
claim based on any promotional material, packaging, documentation or other
materials provided by Licensor with respect to the Products, except to the
extent such claim is based on Broderbund's actions that modify or alter the
Products; and""",
                             """(c) the breach of any covenant, representation or warranty set
forth in this Agreement."""]


def test_document_distribution_1_lc():
    """
    Test lowercase letters only.
    :return:
    """
    # Check all dictionaries
    assert_dict_equal(DOCUMENT_EXAMPLE_1_RESULT_LC,
                      build_document_distribution(DOCUMENT_EXAMPLE_1, string.ascii_lowercase))


def test_document_distribution_1_digits():
    """
    Test digits only.
    :return:
    """
    # Check all dictionaries
    assert_dict_equal(DOCUMENT_EXAMPLE_1_RESULT_DI,
                      build_document_distribution(DOCUMENT_EXAMPLE_1, string.digits))


def test_document_distribution_1_custom():
    """
    Test custom set.
    :return:
    """
    # Check all dictionaries
    assert_dict_equal(DOCUMENT_EXAMPLE_1_RESULT_CUSTOM,
                      build_document_distribution(DOCUMENT_EXAMPLE_1, ['1', '2', '3']))


def test_document_distribution_1_custom_nn():
    """
    Test custom set.
    :return:
    """
    # Check all dictionaries
    assert_dict_equal(DOCUMENT_EXAMPLE_1_RESULT_CUSTOM_NO_NORM,
                      build_document_distribution(DOCUMENT_EXAMPLE_1, ['1', '2', '3'], norm=False))


def test_document_distribution_1_print():
    """
    Test all printable.
    :return:
    """
    # Check all dictionaries
    assert_dict_equal(DOCUMENT_EXAMPLE_1_RESULT_PRINT,
                      build_document_distribution(DOCUMENT_EXAMPLE_1, string.printable))


def test_document_distribution_empty():
    """
    Test all printable.
    :return:
    """
    # Check all dictionaries
    _ = build_document_distribution("", string.printable)


@nottest
def run_paragraph_test(text, result, window_pre=5, window_post=5):
    """
    Base test method to run against text with given results.
    """

    def remove_whitespace(r):
        return r.replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")

    # Get list from text
    para_list = list(get_paragraphs(text, window_pre, window_post))

    # Check length first
    assert len(para_list) == len(result)

    # Check each sentence matches
    clean_result = [remove_whitespace(para) for para in result]
    for para in para_list:
        assert remove_whitespace(para) in clean_result


def test_paragraph_example_1():
    run_paragraph_test(DOCUMENT_EXAMPLE_2, DOCUMENT_EXAMPLE_2_RESULT)


def test_paragraph_example_2():
    run_paragraph_test(DOCUMENT_EXAMPLE_3, DOCUMENT_EXAMPLE_3_RESULT)


def test_paragraph_example_3():
    run_paragraph_test(DOCUMENT_EXAMPLE_4, DOCUMENT_EXAMPLE_4_RESULT)
