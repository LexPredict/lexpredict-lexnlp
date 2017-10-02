#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Name unit tests for English.

This module implements unit tests for the name extraction functionality in English.

Todo:
    * Better testing for exact test in return sources
    * More pathological and difficult cases
"""

# Imports
from nose import with_setup
from nose.tools import assert_in, assert_set_equal
from lexnlp import disable_stanford, enable_stanford
from lexnlp.extract.en.entities.stanford_ner import get_persons, get_organizations, get_locations

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

EXAMPLE_STANFORD_ORG_LIST = [("""Hello, my name is John Doe.""",
                              []),
                             ("""This Amendment to Executive Employment Agreement, dated effective as of February 22, 
                            2011, is between Allis-Chalmers Energy Inc. (the “Company”) and Theodore F. Pound III 
                            (“Executive”).""",
                              ["Allis-Chalmers Energy Inc"]),
                             ("""The following agreement effective 1 January 2006 is hereby entered into between Art 
                             Hicks (hereinafter known as Executive) and Cybex International (together with its 
                             affiliated corporations hereinafter known as the “Company”) and having its principal 
                             offices at 10 Trotter Drive, Medway, MA. 02053.""",
                              ["Cybex International"]),
                             ("""""", [])
                             ]

EXAMPLE_ORG_LIST = [("""Hello, my name is John Doe.""",
                     []),
                    ("""THIS AGREEMENT is made as of this 1st day of June, 1999 (the "Effective Date"), between 
                    LASON SYSTEMS, INC, a Delaware corporation, the address of which is 1305 Stephenson Highway, 
                    Troy, Michigan, 48084 ("Corporation"), and Gary L. Monroe, whose address is 4808 Deer Park Court,
                    Rochester Hills, Michigan 48306 ("Employee").""", ["LASON SYSTEMS, INC"]),
                    ]

STANFORD_LOCATION_EXAMPLES = [("""Hello, my name is John Doe.""",
                               []),
                              ("""He is from the country of France.""",
                               ["France"]),
                              ("""LASON SYSTEMS, INC is a corporation based in Delaware.""",
                               ["Delaware"]),
                              ("""This Agreement shall be interpreted and applied under the laws of the State of
New York.""",
                               ["New York"]),
                              ("""Section 3.04. Governing Law. This Amendment has been executed and delivered in the 
                              State of Texas, and its validity, interpretation, performance and enforcement shall be 
                              governed by the laws of Texas, without giving effect to any principles of conflicts of 
                              law.""",
                               ["Texas"]),
                              ("""In accordance with the Contract Law of the People’s Republic of China, the 
                              Construction Law of the People’s Republic of China and relevant laws and administrative 
                              regulations, the two parties enter this Contract for the Construction""",
                               ["People's Republic of China"]),
                              ("""(b) The arbitrator(s) shall apply California law to the merits of any dispute or 
                              claim, without reference to conflicts of law rules. The arbitration""",
                               ["California"]),
                              ("""“Committed Currencies” means lawful currency of the United Kingdom of Great Britain 
                              and Northern Ireland, lawful currency of The Swiss Federation, lawful currency of Japan 
                              and Euros.""",
                               ["United Kingdom of Great Britain", "Northern Ireland", "Japan"])
                              ]

EXAMPLE_NAME_LIST = [("""Hello, my name is John Doe.""",
                      ["John Doe"]),
                     ("""THIS AGREEMENT is made as of this 1st day of June, 1999 (the "Effective Date"), between 
                     LASON SYSTEMS, INC, a Delaware corporation, the  address of which is 1305 Stephenson Highway, 
                     Troy, Michigan, 48084 ("Corporation"), and Gary L. Monroe, whose address is 4808 Deer Park Court,
                     Rochester Hills, Michigan 48306 ("Employee").""", ["Gary L. Monroe"]),
                     ("""Renée Moore will work as President, Corporate and Business Development, reporting to the CEO,
                     Encorium Group Inc. Renée Moore will work pursuant to all instructions given by the CEO or the 
                     Company’s board.""",
                      ["Renée Moore"]),
                     ("""(iii) in carrying out her duties hereunder, Renee engages in willful misconduct relating to the
                     business of the Company or any of its affiliates causing material harm to Encorium or its 
                     affiliates or their businesses, including, without limitation fraud, embezzlement and theft.""",
                      ["Renee"]),
                     ("""WHEREAS, SAS Software, Inc. (to which ANSYS, Inc., a Delaware corporation (the “Company”) is 
                     successor by operation of law) and SAS Acquisition Corp., a Delaware corporation (to which the 
                     Company is successor by operation of law) entered into an Employment Agreement with Peter J. 
                     Smith (the “Executive”) as of the 28th day of March 1994 (the “Agreement”)""",
                      ["Peter J. Smith"]),
                     ("""THIS SECOND AMENDMENT to Employment Agreement (“Second Amendment”) is entered into as of this
                     21st day of December, 2006 by and between Wilsons The Leather Experts Inc. (the “Company”), and 
                     Michael M. Searles (“Executive”).""",
                      ["Michael M. Searles"]),
                     ("""THIS AGREEMENT, is by and between Dover Motorsports, Inc. (the “Company”) and Denis McGlynn
                     (the “Executive”) and is effective as of this 16th day of June 2004 (the “Effective Date”).""",
                      ["Denis McGlynn"]),
                     ("""THIS FIRST AMENDMENT TO EMPLOYMENT AGREEMENT (“Amendment”) is entered into by and among 
                     Cardtronics, LP, a Delaware limited partnership (the “Company”), Cardtronics, Inc. (the “Parent
                     Company”) and Rick Updyke (the “Employee”) effective as of June 20, 2008.""",
                      ["Rick Updyke"])
                     ]


def setup_module():
    """
    Setup environment pre-tests
    :return:
    """
    enable_stanford()


def teardown_module():
    """
    Setup environment post-tests.
    :return:
    """
    disable_stanford()


@with_setup(setup_module, teardown_module)
def test_stanford_name_example_in():
    # Iterate through examples
    for i, example in enumerate(EXAMPLE_NAME_LIST):
        # Get constraints
        print("Example {i}: {t}...".format(i=i,
                                           t=example[0][0:min(len(example[0]), 20)]))

        names = get_persons(example[0])
        for name in example[1]:
            assert_in(name, names)


@with_setup(setup_module, teardown_module)
def test_stanford_org_example_in():
    # Iterate through examples
    for i, example in enumerate(EXAMPLE_STANFORD_ORG_LIST):
        # Get constraints
        print("Example {i}: {t}...".format(i=i,
                                           t=example[0][0:min(len(example[0]), 20)]))

        orgs = list(get_organizations(example[0]))
        for org in example[1]:
            assert_in(org, orgs)


@with_setup(setup_module, teardown_module)
def test_stanford_locations():
    """
    Test Stanford NER location extraction.
    :return:
    """
    i = 0
    for example, result in STANFORD_LOCATION_EXAMPLES:
        print("Example {i}: {t}...".format(i=i, t=example[0:min(len(example), 20)]))
        assert_set_equal(set(get_locations(example)), set(result))
        i += 1
