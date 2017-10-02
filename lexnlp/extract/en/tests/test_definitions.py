#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Definition unit tests for English.

This module implements unit tests for the definition extraction functionality in English.

Todo:
    * Better testing for exact test in return sources
    * More pathological and difficult cases
"""

# Test imports
from nose.tools import assert_set_equal

# Project imports
from lexnlp.extract.en.definitions import get_definitions

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

EXAMPLE_FIXED_DEFINITIONS = [("""“Advance” means a Revolving Credit Advance or a Competitive Bid Advance, as the 
context may require.""",
                              ["Advance"]),
                             ("""Visual Networks Operations, Inc., a Delaware corporation with offices at 2092 Gaither 
                             Road, Rockville, Maryland 20850("Licensor.") and is made retroactive to December 3, 2002 
                             ("Effective Date").""",
                              ["Licensor", "Effective Date"]),
                             ("""The word “vessel” includes every description of watercraft or other artificial 
                             contrivance used, or capable of being used, as a means of transportation on water.""",
                              ["vessel"]),
                             ("""the words “person” and “whoever” include corporations, companies, associations, firms,
                             partnerships, societies, and joint stock companies, as well as individuals;""",
                              ["person", "whoever"]),
                             ("""(1) The term “accountant” means accountant authorized under applicable law to practice 
                             public accounting, and includes professional accounting association, corporation, or 
                             partnership, if so authorized.""",
                              ["accountant"]),
                             ("""(20) The term “farmer” means (except when such term appears in the term 
                             “family farmer”) person that received more than 80 percent of such person’s gross income 
                             during the taxable year of such person immediately preceding the taxable year of such 
                             person  during which the case under this title concerning such person was commenced from 
                             a farming operation owned or operated by such person.""",
                              ["farmer", "family farmer"]),
                             ("""and any of the Contractor's proprietary information, including without limitation, 
                             financial information, projects, copies of leases, real estate appraisals, and other 
                             information regarding the Facility and the business affairs and operations of the 
                             Contractor which any of said parties obtain from the Contractor in the course of 
                             negotiations for the transactions contemplated hereby (the "Confidential Information");""",
                              ["Confidential Information"]),
                             ("""For the purposes of this Agreement, 
                             the terms "Physical Completion" or "Physically Completed" shall mean the date on which the 
                             building and improvements described and set forth in the Final Plans have been completed 
                             and the Facility shall have been approved for temporary or permanent occupancy by the 
                             local building inspector, and by the State Fire Marshall in the event his approval is 
                             required. Physical Completion shall be deemed to have been achieved notwithstanding that 
                             any of such officials or sagencies have issued a Punch-List listing items requiring 
                             completion or correction, so  long as such Punch-List not prevent or prohibit occupancy.
                             """,
                              ["Physical Completion", "Physically Completed"]),
                             ("""Payment of Contract Price. At the time of transfer of title, the balance of the 
                             Contract Price not paid via Contractor's requisitions under the construction financing 
                             for the Facility shall be paid by the Owner to the Contractor by wire transfer, certified 
                             check or other mutually acceptable means less any Punch-list Amount or retainage required
                             by Owner's lender. """,
                              []),
                             ("""The Parties agree that an hour of Services shall mean any hour during which one or more
                             employees of the Company are receiving Services.""",
                              []),
                             (""""PC MoneyGram Application Software" shall have the meaning set forth in the Contribution
                             Agreement.""",
                              ["PC MoneyGram Application Software"]),
                             (""""Losses" means any and all losses, Costs, obligations, liabilities, settlement payments,
                             awards, judgments, fines, penalties, damages, deficiencies or other charges.""",
                              ["Losses"]),
                             ("""For purposes of this definition, "control" shall mean the possession, directly or 
                             indirectly, of the power to direct or cause the direction of the management or policies 
                             of a person or entity, whether through the ownership of voting securities or partnership 
                             or other ownership interests, by contract, by law or otherwise.""",
                              ["control"]),
                             ("""Whenever used in this Agreement, the following terms will have the following specified 
                             meanings: "Affiliate" means, with respect to any person or entity, any other person or 
                             entity (including, without limitation, any officer, director, shareholder, partner, 
                             employee, agent or representative of such person or entity) that, directly or indirectly 
                             through one or more intermediaries, controls, is controlled by or is under common control 
                             with such first person or entity.""",
                              ["Affiliate"]),
                             ("""“Accounts” means all of each Borrower’s now owned and hereafter acquired, present and 
                             future, accounts, contract rights, chattel paper, documents, and instruments, including 
                             without limitation, all obligations to each Borrower for the payment of money, whether 
                             arising out of each Borrower’s sale of goods or rendition of services or otherwise.""",
                              ["Accounts"]),
                             ("""""", []),
                             ]


def test_definition_fixed():
    i = 0
    for example in EXAMPLE_FIXED_DEFINITIONS:
        # Get constraints
        print("Example {i}: {t}...".format(i=i,
                                           t=example[0][0:min(len(example[0]), 20)]))
        definitions = list(get_definitions(example[0]))
        print(definitions)
        assert_set_equal(set(definitions), set(example[1]))
        i += 1
