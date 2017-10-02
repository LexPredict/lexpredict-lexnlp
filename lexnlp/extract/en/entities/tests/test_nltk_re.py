#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Unit tests for the NLTK regular expression entity extraction methods.

This module implements unit tests for the named entity extraction functionality in English based on the
NLTK POS-tagging and (fuzzy) chunking methods.

Todo:
    * Better testing for exact test in return sources
    * More pathological and difficult cases
"""

from nose.tools import assert_in, assert_list_equal

from lexnlp.extract.en.entities.nltk_re import get_companies, get_parties_as

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

EXAMPLE_TEXT = ["""The Amendment, dated as of May 31,
1999, between California Federal Bank, A Federal Savings Bank, (the "Company")
successor by merger to First Nationwide Bank, A Federal Savings Bank, ("FNB")
and Christie S. Flanagan (the "Executive").""",

                """This Amendment to Employment Agreement (“Amendment”) is made and entered into this 18th day of July,
2005, by and between OSI SYSTEMS, INC. (“Company”), a California corporation, and Anuj Wadhawan (“Employee”).""",

                """(e) COMPANY hereby agrees to reimburse Mr. Gallop's actual relocation expenses,
as determined in accordance with the definition of moving expenses permitted to
be deducted under the Internal Revenue Code of 1986, as amended, as incurred, up
to $100,000, payable if and when spent, including the brokerage fee for the sale
of Mr. Gallop's current home in Danville, California and first class airfares
for Mr. Gallop and his spouse between Pleasanton, California and Perth,
Australia or such other similar destination as GALLOP may determine.""",

                """ By and between American Residential Gap LLC (ARG), a Michigan Limited Liability Company with 
                address at 380, N. Old Woodward Avenue, Ste. 300, Birmingham, MI 48009, and Progreen Construction LLC 
                (PGC), a Michigan Limited Liability Company with address at 380 N. Old Woodward Avenue, Ste. 226, 
                Birmingham, MI 48009."""
                ]

EXAMPLE_COMPANIES = [
    (
        ('California Federal', None, 'Bank'),
        ('Federal Savings', None, 'Bank')
    ),

    (
        ('OSI SYSTEMS', 'INC', None),
    ),

    (),

    (
        ('American Residential Gap', 'LLC', None),
        ('Progreen Construction', 'LLC', None)
    )
]

EXAMPLE_COMPANY_ARTICLE_RE_LIST = [
    ("""THIS CREDIT AGREEMENT, dated as of July 24, 2014, is by and among MGC DIAGNOSTICS CORPORATION, a Minnesota 
    corporation (“Holding Company”) and MEDICAL GRAPHICS CORPORATION, a Minnesota corporation (“Medical Graphics”) 
    (each of Holding Company and Medical Graphics are also referred to individually and collectively as the “Borrower”
    and each reference to the Borrower herein shall mean each such entity, collectively and individually, as the 
    context may require and as applicable), and BMO HARRIS BANK N.A., a national banking association (the “Bank”).""",
     [('MGC DIAGNOSTICS', 'CORPORATION', None),
      ('MEDICAL GRAPHICS', 'CORPORATION', None)]),

    ("""This CREDIT AGREEMENT (the “Agreement”) is entered into as of March 4, 2005, between MK GOLD EXPLORATION B.V., 
    a Dutch private company with limited liability (“Borrower”), and LEUCADIA NATIONAL CORPORATION, a New York 
    corporation (“Lender”). Capitalized terms used herein and not otherwise defined shall have the meanings set forth in
    subsection 1.1 of this Agreement.""",
     [('MK GOLD EXPLORATION', 'B.V', None),
      ('LEUCADIA NATIONAL', 'CORPORATION', None)
      ]),

    ("""CREDIT AGREEMENT

Dated as of April 20, 2011
Among
THE HANOVER INSURANCE GROUP, INC.

as Borrower
THE
LENDERS NAMED HEREIN
as Lenders
GOLDMAN SACHS BANK USA
as Sole Arranger and Bookrunner

MORGAN STANLEY SENIOR FUNDING, INC
as Syndication Agent
WELLS FARGO BANK, NATIONAL ASSOCIATION

as Documentation Agent
and
GOLDMAN SACHS BANK USA

as Administrative Agent""",
     [('THE HANOVER INSURANCE GROUP', 'INC', None),
      ('GOLDMAN SACHS', None, 'BANK'),
      ]),

    # Empty case
    ("", []),
]

EXAMPLE_COMPANY_RE_LIST = [
    ("""ACME, INC.""",
     [('ACME', 'INC', None)]),

    ("""This CREDIT AGREEMENT (the “Agreement”) is entered into as of March 4, 2005, between 
                           MK GOLD EXPLORATION B.V., a Dutch private company with limited liability (“Borrower”), and
                           LEUCADIA NATIONAL CORPORATION, a New York corporation (“Lender”). Capitalized terms used
                           herein and not otherwise defined shall have the meanings set forth in subsection 1.1 of
                           this Agreement.""",
     [("MK GOLD EXPLORATION", "B.V", None),
      ("LEUCADIA NATIONAL", "CORPORATION", None)]),

    # Empty case
    ("""""", []),
]

PARTY_AS_EXAMPLES = [("Acme, Inc. as Lead Borrower",
                      [({'company_type': ['Inc'], 'company_name': ['Acme,'], 'company_description': []},
                        'Lead Borrower')]
                      ),
                     ("""HF Logistics-SKX T1, LLC, as Borrower""",
                      [({'company_type': ['LLC'], 'company_name': ['HF Logistics-SKX T1,'], 'company_description': []},
                        'Borrower')]),
                     ("""dated as of 5 May, 2017""", []),
                     ("""""", [])
                     ]


def test_companies_in_article():
    """
    Test get_companies default behavior.
    :return:
    """
    for i, example in enumerate(EXAMPLE_TEXT):
        print("Example {0}: {1}".format(i, example[0:min(len(example), 20)]))
        companies = list(get_companies(example, use_article=True))
        for company in EXAMPLE_COMPANIES[i]:
            assert_in(company, companies)


def test_company_article_regex():
    """
    Test company regular expressions.
    :return:
    """
    i = 0
    for text, expected_result in EXAMPLE_COMPANY_ARTICLE_RE_LIST:
        print("Example {i}: {t}...".format(i=i, t=text[0:min(len(text), 20)]))
        found_results = list(get_companies(text, use_article=True))
        for er in expected_result:
            assert_in(er, found_results)
        i += 1


def test_company_regex():
    """
    Test company regular expressions.
    :return:
    """
    i = 0
    for text, expected_result in EXAMPLE_COMPANY_RE_LIST:
        print("Example {i}: {t}...".format(i=i, t=text[0:min(len(text), 20)]))
        found_results = list(get_companies(text, use_article=False))
        print(found_results)
        for er in expected_result:
            assert_in(er, found_results)
        i += 1


def test_company_as():
    """
    Text company as ... strings.
    :return:
    """
    i = 0
    for example, result in PARTY_AS_EXAMPLES:
        print("Example {i}: {t}...".format(i=i, t=example[0:min(len(example), 20)]))
        assert_list_equal(list(get_parties_as(example)), result)
        i += 1
