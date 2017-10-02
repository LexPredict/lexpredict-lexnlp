#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Constraints unit tests for English.

This module implements unit tests for the constraint extraction functionality in English.

Todo:
    * Better testing for exact test in return sources
    * More pathological and difficult cases
"""

# Imports
from nose.tools import assert_set_equal

from lexnlp.extract.en.constraints import get_constraints

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

EXAMPLE_FIXED_CONSTRAINTS = [("""Neither the making of any Advance hereunder or the use of the
proceeds thereof will violate or be inconsistent with the provisions of
Regulation G, Regulation T, Regulation U or Regulation X.  Following the
application of the proceeds of the Loans, less than 25% of the value (as
determined by any reasonable method) of the assets of the Borrower and its
Subsidiaries which are subject to any limitation on sale, pledge, or other
restriction hereunder taken as a whole have been, and will continue to be,
represented by Margin Stock.""",
                              ["less than"]),
                             ("""11.2. Ratable Payments.  If any Lender, whether by setoff or otherwise,
has payment made to it upon its Loans (other than payments received pursuant to
Section 3.1, 3.2 or 3.4) in a greater proportion than its pro-rata share of
such Loans, such Lender agrees, promptly upon demand, to purchase a portion of
the Loans held by the other Lenders so that after such purchase each Lender
will hold its ratable proportion of Loans.""",
                              ["greater", "after"]),
                             ("""6.22. Nuveen & Co. Net Capital.  The Borrower shall cause Nuveen & Co. at
all times after the date hereof to maintain a ratio of Net Capital to Aggregate
Debit Items (as such terms are defined pursuant to SEC Rule 15c3-1 under the
Exchange Act) of not less than 5.5%.""",
                              ["less than", "after"]),
                             (""""Rate Hedging Obligations" of a Person means any and all obligations of
such Person, whether absolute or contingent and howsoever and whensoever
created, arising, evidenced or acquired (including all renewals, extensions and
modifications thereof and substitutions therefor), under (a) any and all
agreements, devices or arrangements designed to protect at least one of the
parties thereto from the fluctuations of interest rates, exchange rates or
forward rates applicable to such party's assets, liabilities or exchange
transactions, including, but not limited to, dollar-denominated or
cross-currency interest rate exchange agreements, forward currency exchange
agreements, interest rate cap or collar protection agreements, forward rate
currency or interest rate options, puts and warrants, and (b) any and all
cancellations, buybacks, reversals, terminations or assignments of any of the
foregoing.""",
                              ["at least"]),
                             ("""The
Applicable Margin shall be adjusted, if necessary, quarterly as of the tenth
day after the earlier of the date of delivery or the required delivery date for
the certificate provided for above; provided, that if such certificate,
together with the financial statements to which such certificate relates, are
not delivered by the tenth day after the required delivery date, then the""",
                              ["after"]),
                             ("""Applicable Margin shall be equal to .24% for the relevant quarter.  Until
adjusted as described above after September 30, 1997, the Applicable Margin
shall be equal to .21%; provided that if the Borrower shall deliver a
certificate demonstrating a Leverage Ratio at Level I for the June 30, 1997
Fiscal Quarter, then the Applicable Margin shall be .18% from the date of
delivery of such certificate until adjusted as described above after September
30, 1997.""",
                              ["equal to",
                               "after"]),
                             ("""No payment by TENANT
or receipt of LANDLORD of a lesser amount than a monthly installment of
rent herein stipulated shall be deemed to be other than on account of
such stipulated rent, nor shall any endorsement or statement on any check
or any letter accompanying any check or payment as rent be deemed an
accord and satisfaction, and LANDLORD may accept such check for payment
without prejudice to LANDLORD’s right to recover the balance of such
rent or pursue any other remedy provided for in this lease.""",
                              ["lesser"]),
                             ("""The minimum rent shall be adjusted at the end of each year during the
term hereof by a 3% increase over the rent then being paid. There also
shall be no additional pass-throughs of increases in operating expenses
except as specifically referenced herein.""",
                              ["minimum"]),
                             ("""In the event the real estate taxes levied or assessed against the land
and building of which the premises are a part in future tax years are greater than the real estate taxes for the
base tax year, the TENANT, shall pay within thirty (30) days after submission of the bill to TENANT for the increase in
real estate taxes, as additional rent a proportionate share of such
increases, which proportionate share shall be computed at 22.08% of the
increase in taxes, but shall exclude any fine, penalty, or interest
charge for late or non-payment of taxes by LANDLORD. The base tax year
shall be July 1, 1994 to June 30, 1995.""",
                              ["greater than", "within", "after"]),
                             ("""b. Calculation of Benefits. At least fifteen (15) days prior to the Payment Date, PPD
                             shall notify Employee of the aggregate present value of all amounts and benefits to which
                             Employee would be entitled under this Agreement and any other plan, program or arrangement
                             with PPD as of the Termination Date, together with the projected maximum payments,
                             determined as of such Date of Termination, that could be paid without Employee being
                             subject to the Excise Tax.""",
                              ["at least", "prior to", "maximum"]),
                             ("""If (i) the aggregate value of all amounts and benefits to which Employee would be
                             entitled under this Agreement and any other plan, program or arrangement with PPD exceeds
                             the amount which can be paid to Employee without Employee incurring an Excise Tax and (ii)
                             Employee would receive a greater net after-tax amount (taking into account all applicable
                             taxes payable by Employee, including an Excise Tax) by applying the limitation contained
                             in this Section 2.05(c), then the amounts otherwise payable to Employee under this Section
                             2 shall be reduced to an amount equal to the Payment Cap. If Employee receives reduced
                             payments and benefits hereunder, Employee shall have the right to designate which of the
                             payments and benefits otherwise provided for in this Agreement that Employee will receive
                             in connection with the application of the Payment Cap.""",
                              ["exceeds", "greater", "equal to"]),
                             ("""(i) federal income taxes at the highest applicable marginal rate of federal income
                             taxation for the calendar year in which the first amounts are to be paid hereunder, and""",
                              ["highest"]),
                             ("""prior to fifteen days""",
                              ["prior to"])
                             ]


def test_constraint_fixed_example():
    i = 0
    for example in EXAMPLE_FIXED_CONSTRAINTS:
        print("Example {i}: {t}...".format(
            i=i, t=example[0][0:min(20, len(example[0]))]))
        constraints = get_constraints(example[0])
        constraint_types = [c[0] for c in constraints]
        print(constraints)
        assert_set_equal(set(constraint_types),
                         set(example[1]))
        i += 1
