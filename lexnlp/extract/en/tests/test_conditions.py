#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Condition unit tests for English.

This module implements unit tests for the condition extraction functionality in English.

Todo:
    * Better testing for exact test in return sources
    * More pathological and difficult cases
"""

# Imports
from nose.tools import assert_in

from lexnlp.extract.en.conditions import get_conditions

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

EXAMPLE_FIXED_CONSTRAINTS = [("""If they buy, then you will sell.""",
                              ["if"]),
                             ("""The term of this lease shall be for a period of five years, commencing on the 1st day
                             of April, 1995, and terminating on the 31st day of March, 2000 with an option for an
                             additional five years at the same terms and conditions in this lease, provided that TENANT
                             shall have given the LANDLORD written notice of TENANT’s intention to do so six (6) months
                             prior to the expiration of this lease and that the Tenant is not in default of the
                             Lease.""",
                              ["provided that"]),
                             ("""The TENANT shall pay to the LANDLORD an annual rental (herein called
“minimum rent”) in the amount of One Hundred fifty eight thousand five hundred thirty & 50/100 DOLLARS
($158,530.50), subject to adjustment as hereinafter set forth, payable without deduction or set off in equal
monthly installments of Thirteen thousand two hundred ten & 88/100 DOLLARS ($13,210.88) per month in advance,
the first installment of which is due and payable April 1,1995 and all subsequent installments due
and payable on the 1st day of each calendar month hereafter until the total rent provided for herein is paid.""",
                              ["subject to", "until"]),
                             ("""(1)  Immediately  upon the occurrence of a Change in Control of the Company
or the Bank, the Employee shall be paid  $125,000.00.  Said sum shall be paid in one lump sum.""",
                              ["upon the occurrence"]),
                             ("""This  Agreement  shall  remain in effect for the period  commencing  on the
Effective Date and ending on the earlier of (i) the date thirty-six months after
the Effective Date, or (ii) the date on which the Employee terminates employment
with the Bank;  provided that the  Employee's  rights  hereunder  shall continue
following  the  termination  of this  employment  with the Bank under any of the
circumstances  described in Section 1(a)  hereof.""",
                              ["provided that"]),
                             ("""No amendments or additions to this  Agreement  shall be binding unless made
in  writing  and  signed  by all of the  parties,  except  as  herein  otherwise
specifically provided.""",
                              ["unless"]),
                             ]


def test_condition_fixed_example():
    i = 0
    for example in EXAMPLE_FIXED_CONSTRAINTS:
        # Get constraints
        print("Example {i}: {t}...".format(i=i,
                                           t=example[0][0:min(len(example[0]), 20)]))
        conditions = get_conditions(example[0])

        for condition in conditions:
            assert_in(condition[0], example[1])

        i += 1
