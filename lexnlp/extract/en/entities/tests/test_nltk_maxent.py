#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Unit tests for the NLTK maximum entropy entity extraction methods.

This module implements unit tests for the named entity extraction functionality in English based on the
NLTK POS-tagging and (fuzzy) chunking methods.

Todo:
    * Better testing for exact test in return sources
    * More pathological and difficult cases
"""
from nose.tools import assert_set_equal, assert_in, assert_equal, assert_list_equal

from lexnlp.extract.en.entities.nltk_maxent import get_noun_phrases, get_companies, get_persons, get_geopolitical, \
    get_organizations

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.0"
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

                """AMERICAN RESIDENTIAL GAP LLC (ARG), a Michigan Limited Liability Company
with address at 380, N. Old Woodward Avenue, Ste. 300, Birmingham, MI 48009.
And
PROGREEN CONSTRUCTION LLC (PGC), a Michigan Limited Liability Company
with address at 380 N. Old Woodward Avenue, Ste. 226, Birmingham, MI 48009.
"""
                ]

EXAMPLE_NOUN_PHRASES = [("First Nationwide Bank, A Federal Savings Bank", "May",
                         "California Federal Bank, A Federal Savings Bank", "Company", "Amendment",
                         "Christie S. Flanagan", "Executive", "FNB"),

                        ('Amendment', 'Anuj Wadhawan', 'OSI SYSTEMS, INC', "Company", 'Employee', 'California',
                         'Agreement', 'July'),

                        ('GALLOP', 'Danville, California', 'COMPANY', 'Internal Revenue Code',
                         'Pleasanton, California and Perth, Australia', 'Mr. Gallop'),

                        ('ARG', 'Birmingham, MI', 'AMERICAN RESIDENTIAL GAP LLC', 'Michigan Limited Liability Company',
                         'PROGREEN CONSTRUCTION LLC', 'Old Woodward Avenue, Ste', 'PGC')
                        ]

EXAMPLE_COMPANIES = [(),

                     (('OSI SYSTEMS', 'INC'),),

                     (),

                     (('AMERICAN RESIDENTIAL GAP', 'LLC'),
                      ('PROGREEN CONSTRUCTION', 'LLC'))
                     ]

EXAMPLE_PERSONS = [('Savings Bank', 'Christie S. Flanagan', 'First Nationwide Bank, A Federal Savings Bank'),

                   ('Anuj Wadhawan',),

                   ('Mr. Gallop',),

                   ('Old Woodward Avenue, Ste',)
                   ]

EXAMPLE_GPES = [("California",),

                ('Agreement', 'California'),

                ('Danville, California', 'Pleasanton, California and Perth, Australia'),

                ('Birmingham, MI',)
                ]

EXAMPLE_ORGS = [('Amendment', 'Federal Bank, A Federal',),

                ('Company', 'OSI SYSTEMS, INC'),

                ('COMPANY', 'Internal Revenue Code', 'GALLOP'),

                ('Michigan Limited Liability Company', 'AMERICAN RESIDENTIAL GAP LLC', 'PROGREEN CONSTRUCTION LLC',
                 'ARG', 'PGC')
                ]

EXAMPLE_NAME_LIST = [("""Hello, my name is John Doe.""",
                      ["John Doe"]),
                     ("""Hello, my name is Xi.""",
                      []),
                     ("""THIS AGREEMENT is made as of this 1st day of June, 1999 (the
"Effective Date"), between LASON SYSTEMS, INC, a Delaware corporation, the
address of which is 1305 Stephenson Highway, Troy, Michigan, 48084
("Corporation"), and Gary L. Monroe, whose address is 4808 Deer Park Court,
Rochester Hills, Michigan 48306 ("Employee").""", ["Gary L. Monroe"]),
                     ("""Renée Moore will work as President, Corporate and Business Development, reporting to the CEO,
Encorium Group Inc. Renée Moore will work pursuant to all instructions given by the CEO or the Company’s board.""",
                      ["Renée Moore"]),
                     ("""(iii) in carrying out her duties hereunder, Renee engages in willful misconduct relating to the
business of the Company or any of its affiliates causing material harm to Encorium or its affiliates or their 
businesses, including, without limitation fraud, embezzlement and theft.""",
                      ["Renee"]),
                     ("""WHEREAS, SAS Software, Inc. (to which ANSYS, Inc., a Delaware corporation (the “Company”) is
successor by operation of law) and SAS Acquisition Corp., a Delaware corporation (to which the Company is successor by
operation of law) entered into an Employment Agreement with Peter J. Smith (the “Executive”) as of the 28th day of
March 1994 (the “Agreement”)""",
                      ["Peter J. Smith"]),
                     ("""THIS SECOND AMENDMENT to Employment Agreement (“Second Amendment”) is entered into as of this
21st day of December, 2006 by and between Wilsons The Leather Experts Inc. (the
“Company”), and Michael M. Searles (“Executive”).""",
                      ["Michael M. Searles"]),
                     ("""THIS AGREEMENT, is by and between Dover Motorsports, Inc. (the “Company”) and Denis McGlynn
(the “Executive”) and is effective as of this 16th day of June 2004 (the “Effective Date”).""",
                      ["Denis McGlynn"]),
                     ("""THIS FIRST AMENDMENT TO EMPLOYMENT AGREEMENT (“Amendment”) is entered into by and among
Cardtronics, LP, a Delaware limited partnership (the “Company”), Cardtronics, Inc. (the “Parent
Company”) and Rick Updyke (the “Employee”) effective as of June 20, 2008.""",
                      ["Rick Updyke"]),

                     ("""THIS FIRST AMENDMENT TO EMPLOYMENT AGREEMENT (“Amendment”) is entered into by and among
Cardtronics, LP, a Delaware limited partnership (the “Company”), Cardtronics, Inc. (the “Parent
Company”) and Rick Updyke or (the “Employee”) effective as of June 20, 2008.""",
                      ["Rick Updyke"]),

                     ("""THIS FIRST AMENDMENT TO EMPLOYMENT AGREEMENT (“Amendment”) is entered into by and among
Cardtronics, LP, a Delaware limited partnership (the “Company”), Cardtronics, Inc. (the “Parent
Company”) and Rick Updyke & (the “Employee”) effective as of June 20, 2008.""",
                      ["Rick Updyke"])
                     ]

EXAMPLE_GPE_LIST = [("""Hello, my name is John Doe.""",
                     []),
                    ("""He is from the country of France.""",
                     ["France"]),

                    ("""He is from the country of France or.""",
                     ["France"]),

                    ("""He is from the country of France &.""",
                     ["France"]),

                    ("""LASON SYSTEMS, INC is a corporation based in Delaware.""",
                     ["Delaware"]),
                    ("""This Agreement shall be interpreted and applied under the laws of the State of
New York.""",
                     ["New York"]),
                    ("""Section 3.04. Governing Law. This Amendment has been executed and delivered in the State of
Texas, and its validity, interpretation, performance and enforcement shall be governed by the laws of Texas, without
giving effect to any principles of conflicts of law.""",
                     ["Texas"]),
                    ("""In accordance with the Contract Law of the People’s Republic of China, the Construction Law of
the People’s Republic of China and relevant laws and administrative regulations, the two parties enter this Contract
for the Construction""",
                     ["China"]),
                    ("""(b) The arbitrator(s) shall apply California law to the merits of any dispute or claim, without
reference to conflicts of law rules. The arbitration""",
                     ["California"]),
                    ("""“Committed Currencies” means lawful currency of the United Kingdom of
356	Great Britain and Northern Ireland, lawful currency of The Swiss Federation, lawful currency of Japan and Euros.""",
                     ["Britain and Northern Ireland", "Swiss Federation", "Japan and Euros"])
                    ]


def test_noun_phrases():
    """
    Test get_noun_phrases methods.
    :return:
    """
    for i, example in enumerate(EXAMPLE_TEXT):
        print("Example {0}: {1}".format(i, example[0:min(len(example), 20)]))
        phrases = set(list(get_noun_phrases(example)))
        assert_set_equal(phrases, set(EXAMPLE_NOUN_PHRASES[i]))


def test_companies():
    """
    Test get_companies methods.
    :return:
    """
    for i, example in enumerate(EXAMPLE_TEXT):
        print("Example {0}: {1}".format(i, example[0:min(len(example), 20)]))
        phrases = set([(c[0], c[1]) for c in get_companies(example)])
        assert_set_equal(phrases, set(EXAMPLE_COMPANIES[i]))


def test_companies_rs():
    """
    Test get_companies methods with return_source.
    :return:
    """
    for i, example in enumerate(EXAMPLE_TEXT):
        print("Example {0}: {1}".format(i, example[0:min(len(example), 20)]))
        phrases = set([(c[0], c[1]) for c in get_companies(example, return_source=True)])
        assert_set_equal(phrases, set(EXAMPLE_COMPANIES[i]))


def test_companies_and():
    """
    Test get_companies methods with CC case.
    :return:
    """
    # Example text
    example = 'Those two organizations IBM INC and LexPredict LLC are cool.'
    results = [('IBM', 'INC'),
               ('LexPredict', 'LLC')]
    assert_list_equal(results, list(get_companies(example)))


def test_company_has_type_only():
    """
    Test get_companies methods with company without name.
    :return:
    """
    # Example text
    example = 'Those two organizations IBM INC and company without name LLC are cool.'
    results = [('IBM', 'INC')]
    assert_list_equal(results, list(get_companies(example)))


def test_persons():
    """
    Test get_persons methods.
    :return:
    """
    for i, example in enumerate(EXAMPLE_TEXT):
        print("Example {0}: {1}".format(i, example[0:min(len(example), 20)]))
        persons = set(list(get_persons(example)))
        assert_set_equal(persons, set(EXAMPLE_PERSONS[i]))


def test_persons_rs():
    """
    Test get_persons methods with return_source.
    :return:
    """
    for i, example in enumerate(EXAMPLE_TEXT):
        print("Example {0}: {1}".format(i, example[0:min(len(example), 20)]))
        persons = set([p[0] for p in get_persons(example, return_source=True)])
        assert_set_equal(persons, set(EXAMPLE_PERSONS[i]))


def test_gpes():
    """
    Test get_geopolitical methods.
    :return:
    """
    for i, example in enumerate(EXAMPLE_TEXT):
        print("Example {0}: {1}".format(i, example[0:min(len(example), 20)]))
        gpes = set(list(get_geopolitical(example)))
        assert_set_equal(gpes, set(EXAMPLE_GPES[i]))


def test_gpes_rs():
    """
    Test get_geopolitical methods with return_source
    :return:
    """
    for i, example in enumerate(EXAMPLE_TEXT):
        print("Example {0}: {1}".format(i, example[0:min(len(example), 20)]))
        gpes = set([g[0] for g in get_geopolitical(example, return_source=True)])
        assert_set_equal(gpes, set(EXAMPLE_GPES[i]))


def test_orgs():
    """
    Test get_organizations methods.
    :return:
    """
    for i, example in enumerate(EXAMPLE_TEXT):
        print("Example {0}: {1}".format(i, example[0:min(len(example), 20)]))
        gpes = set(list(get_organizations(example)))
        assert_set_equal(gpes, set(EXAMPLE_ORGS[i]))


def test_orgs_rs():
    """
    Test get_organizations methods with return_source.
    :return:
    """
    for i, example in enumerate(EXAMPLE_TEXT):
        print("Example {0}: {1}".format(i, example[0:min(len(example), 20)]))
        orgs = set([o[0] for o in get_organizations(example, return_source=True)])
        assert_set_equal(orgs, set(EXAMPLE_ORGS[i]))


def test_orgs_or():
    """
    Test get_organizations methods with CC case.
    :return:
    """
    orgs = list(get_organizations("We will work with either Acme Inc. or Beta Co."))
    num_orgs = len(orgs)
    assert_equal(num_orgs, 2)


def test_orgs_and():
    """
    Test get_organizations methods with CC case.
    :return:
    """
    orgs = list(get_organizations("We will work with either Acme Inc. and Beta Co."))
    num_orgs = len(orgs)
    assert_equal(num_orgs, 1)


def test_person_in():
    """
    Test whether large list of person examples match.
    :return:
    """
    # Iterate through examples
    for i, example in enumerate(EXAMPLE_NAME_LIST):
        # Get constraints
        print("Example {i}: {t}...".format(i=i,
                                           t=example[0][0:min(len(example[0]), 20)]))

        names = list(get_persons(example[0]))
        for name in example[1]:
            assert_in(name, names)


def test_gpe_in():
    """
    Test whether large list of GPE examples match.
    :return:
    """
    # Iterate through examples
    for i, example in enumerate(EXAMPLE_GPE_LIST):
        # Get constraints
        print("Example {i}: {t}...".format(i=i,
                                           t=example[0][0:min(len(example[0]), 20)]))

        gpes = list(get_geopolitical(example[0]))
        for gpe in example[1]:
            assert_in(gpe, gpes)
