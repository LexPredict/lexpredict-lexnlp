#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Court/jurisdiction unit tests for English.

This module implements unit tests for the court/jurisdiction extraction functionality in English.

Todo:
    * Re-introduce known bad cases with better master data or more flexible approach
    * More pathological and difficult cases
"""

from nose.tools import assert_set_equal, assert_equals

from lexnlp.extract.en.courts import get_courts, CourtConfig

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

EXAMPLE_TEXT = ["""Exhibit 99.1
IN THE UNITED STATES DISTRICT COURT
FOR THE NORTHERN DISTRICT OF CALIFORNIA""",
                """As previously reported by
Pilgrim's Pride Corporation (the "Company") on a Current Report on Form 8-K (the "Prior Form 8-K")
filed with the Securities and Exchange Commission on December 22, 2008, the
Company entered into an Employment Agreement with Don Jackson (the "Original
Employment Agreement") pursuant to which Dr. Jackson was appointed as the
Company's President and Chief Executive Officer, subject to the approval of the
Bankruptcy Court for the Northern District of Texas, Fort Worth Division (the
"Bankruptcy Court").  On January 27, 2009, the Company entered into an
Amended and Restated Employment Agreement with Dr. Jackson (the "Amended
Employment Agreement").""",
                """“Bankruptcy Court” shall mean the United States Bankruptcy Court 
for the Southern District of New York or such other court having original jurisdiction 
over the Chapter 11 Case.""",
                """I will argue before E.D. Ark. next week."""

                ]

BAD_EXAMPLES = ["""13.  Governing Law;  Submissions to  Jurisdiction.  This Agreement shall be
deemed to be a contract made under the laws of the State of New York and for all
purposes  shall be  construed  in  accordance  with those laws.  The Company and
Employee  unconditionally consent to submit to the exclusive jurisdiction of the
New York State Supreme Court,  County of New York or the United States  District
Court for Southern  District of New York for any actions,  suits or  proceedings
arising  out of or relating  to this  letter and the  transactions  contemplated
hereby  (and agree not to  commence  any  action,  suit or  proceeding  relating
thereto  except in such courts),  and further agree that service of any process,
summons,  notice or document by  registered  mail to the address set forth above
shall be effective service of process for any action, suit or proceeding brought
against the Company or the Employee, as the case may be, in any such court.""",
                """THE  GUARANTOR HEREBY  IRREVOCABLY  SUBMITS  ITSELF TO THE EXCLUSIVE  JURISDICTION  OF BOTH THE
SUPREME  COURT OF THE STATE OF NEW YORK,  NEW YORK COUNTY AND THE UNITED  STATES
DISTRICT COURT FOR THE SOUTHERN  DISTRICT OF NEW YORK, AND ANY APPEAL THEREFROM,
FOR THE  PURPOSE  OF ANY SUIT,  ACTION  OR OTHER  PROCEEDING  ARISING  OUT OF OR
RELATING TO THIS GUARANTY,  AND HEREBY WAIVES,  AND AGREES NOT TO ASSERT, BY WAY
OF MOTION,  AS A DEFENSE OR OTHERWISE,  IN ANY SUIT,  ACTION OR PROCEEDING,  ANY
CLAIM THAT IT IS NOT PERSONALLY  SUBJECT TO THE  JURISDICTION OF THE ABOVE-NAMED
COURTS  FOR ANY  REASON  WHATSOEVER,  THAT SUCH SUIT,  ACTION OR  PROCEEDING  IS
BROUGHT IN AN INCONVENIENT FORUM OR THAT THIS GUARANTY MAY NOT BE ENFORCED IN OR
BY SUCH COURTS.""",

                ]

EXAMPLE_RESULTS = [["Northern District of California"],
                   ["Northern District of Texas"],
                   ["Southern District of New York"],
                   ["Eastern District of Arkansas"]
                   ]


def test_courts():
    """
    Test court extraction.
    :return:
    """

    # Read master data
    import pandas

    # Load court data
    court_df = pandas \
        .read_csv("https://raw.githubusercontent.com/LexPredict/lexpredict-legal-dictionary/1.0.2/en/legal/us_courts"
                  ".csv")

    # Create config objects
    court_config_list = []
    for _, row in court_df.iterrows():
        c = CourtConfig(row["Court ID"], row["Court Name"], row["Level"], row["Jurisdiction"], row["Court Type"],
                        row["Alias"].split(";") if not pandas.isnull(row["Alias"]) else [])
        court_config_list.append(c)

    # Iterate through examples
    for i, example in enumerate(EXAMPLE_TEXT):
        print("Example {0}: {1}".format(i, example[0:min(len(example), 20)]))
        courts = get_courts(example, court_config_list)
        court_names = [c.name for c in courts]
        assert_set_equal(set(court_names), set(EXAMPLE_RESULTS[i]))


def test_courts_rs():
    """
    Test court extraction with return sources.
    :return:
    """

    # Read master data
    import pandas

    # Load court data
    court_df = pandas \
        .read_csv("https://raw.githubusercontent.com/LexPredict/lexpredict-legal-dictionary/1.0.2/en/legal/us_courts"
                  ".csv")

    # Create config objects
    court_config_list = []
    for _, row in court_df.iterrows():
        c = CourtConfig(row["Court ID"], row["Court Name"], row["Level"], row["Jurisdiction"], row["Court Type"],
                        row["Alias"].split(";") if not pandas.isnull(row["Alias"]) else [])
        court_config_list.append(c)

    # Iterate through examples
    for i, example in enumerate(EXAMPLE_TEXT):
        print("Example {0}: {1}".format(i, example[0:min(len(example), 20)]))
        courts = [c[0] for c in get_courts(example, court_config_list, return_source=True)]
        court_names = [c.name for c in courts]
        assert_set_equal(set(court_names), set(EXAMPLE_RESULTS[i]))


def test_court_config_setup():
    """
    Test setup of CourtConfig object.
    :return:
    """
    # Test setup 1
    cc = CourtConfig(0, "Test Court", "Test Level", "Test Jurisdiction", "Test Type", ["Alias"])
    assert_equals(str(cc), "Test Court (id=0)")

    # Test setup 2
    cc = CourtConfig(0, "Test Court", "Test Level", "Test Jurisdiction", "Test Type")
    assert_equals("{0}".format(cc), "Test Court (id=0)")
