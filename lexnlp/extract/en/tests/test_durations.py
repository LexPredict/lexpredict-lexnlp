#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Duration unit tests for English.

This module implements unit tests for the duration extraction functionality in English.

Todo:
    * Better testing for exact test in return sources
    * More pathological and difficult cases

"""

# Imports
from nose.tools import assert_set_equal

from lexnlp.extract.en.durations import get_durations

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

EXAMPLE_DURATIONS = [
    ('no more than five-day period',
     [('day', 5.0, 5.0)],
     [('day', 5, 5, 'five-day')]),
    ('no more than twenty-four-day duration',
     [('day', 24.0, 24.0)],
     [('day', 24, 24, 'twenty-four-day')]),
    ('no more than five days thereafter',
     [('day', 5.0, 5.0)],
     [('day', 5, 5, 'five days')]),
    ('without at least thirty days of delay',
     [('day', 30.0, 30.0)],
     [('day', 30, 30, 'thirty days')]),
    ('at most 90 days shall',
     [('day', 90.0, 90.0)],
     [('day', 90.0, 90.0, '90 days')]),
    ('at most 90 business days shall',
     [('day', 90.0, 90.0)],
     [('day', 90.0, 90.0, '90 business days')]),
    ('at most 90 calendar days shall',
     [('day', 90.0, 90.0)],
     [('day', 90.0, 90.0, '90 calendar days')]),
    ('at most ninety days shall',
     [('day', 90.0, 90.0)],
     [('day', 90, 90, 'ninety days')]),
    ('at most ninety calendar days shall',
     [('day', 90.0, 90.0)],
     [('day', 90, 90, 'ninety calendar days')]),
    ('at most ninety actual days shall',
     [('day', 90.0, 90.0)],
     [('day', 90, 90, 'ninety actual days')]),
    ('at most ninety business days shall',
     [('day', 90.0, 90.0)],
     [('day', 90, 90, 'ninety business days')]),
    ('at most forty-five business days shall',
     [('day', 45.0, 45.0)],
     [('day', 45, 45, 'forty-five business days')]),
    ('within a period of one month after',
     [('month', 1.0, 30.0)],
     [('month', 1, 30, 'one month')]),
    ('before two months pass',
     [('month', 2.0, 60.0)],
     [('month', 2, 60, 'two months')]),
    ('no more than thirty (30) days',
     [('day', 30.0, 30.0)],
     [('day', 30.0, 30.0, '30) days')]),
    ('no more than twenty five days',
     [('day', 25.0, 25.0)],
     [('day', 25, 25, 'twenty five days')]),
    ('no more than two (2) quarters',
     [('quarter', 2.0, 182.5)],
     [('quarter', 2.0, 182.5, '2) quarters')]),
    ('BEFORE TWO MONTHS PASS',
     [('month', 2.0, 60.0)],
     [('month', 2, 60, 'two months')]),
    ('Before Two Months Pass',
     [('month', 2.0, 60.0)],
     [('month', 2, 60, 'two months')]),
    ('two anniversaries after',
     [('anniversary', 2.0, 730.0)],
     [('anniversary', 2, 730, 'two anniversaries')]),
    ('one anniversary after',
     [('anniversary', 1.0, 365.0)],
     [('anniversary', 1, 365, 'one anniversary')]),
    ('At Least One Month And No More Than Two Months',
     [('month', 1.0, 30.0), ('month', 2.0, 60.0)],
     [('month', 1, 30, 'one month'), ('month', 2, 60, 'two months')]),
    ('After The Passage Of At Least One Year There Can Be',
     [('year', 1.0, 365.0)],
     [('year', 1, 365, 'one year')]),
    ('from a period of two years to five years',
     [('year', 2, 730), ('year', 5, 1825)],
     [('year', 2, 730, 'two years'), ('year', 5, 1825, 'five years')]),
    ('After The Passage Of At Least 2.5 Years There Can Be',
     [('year', 2.5, 912.5)],
     [('year', 2.5, 912.5, '2.5 years')]),
    ('During A Hundred Days There Can Be',
     [('day', 100.0, 100.0)],
     [('day', 100, 100, 'hundred days')]),
    ('During A Hundred Days There Can Be',
     [('day', 100.0, 100.0)],
     [('day', 100, 100, 'hundred days')]),
    ('During A Dozen Days There Can Be',
     [('day', 12.0, 12.0)],
     [('day', 12, 12, 'dozen days')]),
    ("This  Agreement  shall  remain in effect for the period  commencing  on the"
     "Effective Date and ending on the earlier of (i) the date thirty-six months after"
     "the Effective Date, or (ii) the date on which the Employee terminates employment"
     "with the Bank;  provided that the  Employee's  rights  hereunder  shall continue"
     "following  the  termination  of this  employment  with the Bank under any of the"
     "circumstances  described in Section 1(a)  hereof.",
     [('month', 36.0, 1080.0)],
     [('month', 36, 1080, 'thirty-six months')]),
    (
        'Employee shall give PPD written notice of a Constructive Termination,'
        ' which notice shall provide a brief'
        ' description of the circumstances which Employee asserts gives rise '
        'to a right of Constructive Termination, and PPD'
        ' shall have ten (10) days from receipt of said notice within '
        'which to remedy said circumstances.',
        [('day', 10.0, 10.0)], [('day', 10.0, 10.0, '10) days')]),
    (
        '1.07 “Disability” means the inability of Employee to perform '
        'his assigned duties for PPD for a period of three\
         (3) months due to Employee’s physical or mental illness'
        ' as determined by a reputable medical doctor.',
        [('month', 3.0, 90.0)],
        [('month', 3.0, 90.0, '3) months')]),
    (
        'b. Calculation of Benefits. At least fifteen (15) days'
        ' prior to the Payment Date, PPD shall notify Employee of'
        ' the aggregate present value of all amounts and benefits '
        'to which Employee would be entitled under this Agreement'
        ' and any other plan, program or arrangement with PPD as '
        'of the Termination Date, together with the projected maximum'
        ' payments, determined as of such Date of Termination, that '
        'could be paid without Employee being subject to the Excise Tax.',
        [('day', 15.0, 15.0)],
        [('day', 15.0, 15.0, '15) days')]),
    ('6..23 Days', [], []),
    (',, MONTHS', [], []),
    ('After The Passage Of At Least One Year There Can Be',
     [('year', 1.0, 365.0)],
     [('year', 1, 365, 'one year')]),
    ('from a period of two years to five years',
     [('year', 2, 730), ('year', 5, 1825)],
     [('year', 2, 730, 'two years'),
      ('year', 5, 1825, 'five years')]),
    ('After The Passage Of At Least 2.5 Years There Can Be',
     [('year', 2.5, 912.5)],
     [('year', 2.5, 912.5, '2.5 years')]),
    ('During A Hundred Days There Can Be',
     [('day', 100.0, 100.0)],
     [('day', 100, 100, 'hundred days')]),
    ('During A Dozen Days There Can Be',
     [('day', 12.0, 12.0)],
     [('day', 12, 12, 'dozen days')]),
    (
        'The term of this license shall be for an initial'
        ' period of forty-eight (48) months ("initial term"), '
        'commencing on the date of execution of this Agreement. '
        'This license shall thereafter automatically renew on the '
        'anniversary of this execution date for additional terms '
        'of twelve (12) months ("subsequent terms"), unless Licensee'
        'sends written notification to US/INTELICOM of Licensee\'s '
        'intention not to renew. Such notification must be received by '
        'US/INTELICOM not less than ninety (90) days preceding the automatic annual renewal.',
        [('month', 48.0, 1440.0), ('month', 12.0, 360.0), ('day', 90.0, 90.0)],
        [('month', 48.0, 1440.0, '48) months'), ('month', 12.0, 360.0, '12) months'),
         ('day', 90.0, 90.0, '90) days')]),
]

EXAMPLE_TEXT_2 = """(f) Quarterly Report: For Initial Support Agreements and Renewals, Cisco shall submit (a) a report
to Licensor within forty-five (45) days after each Cisco fiscal quarter end, detailing each Customer invoiced for
support during such quarter, the Customer name, Support Agreement number, term of support, effective date of support
Software identification numbers, and the total list price; and (b) a payment equal to support fees owed to Licensor by
Cisco in accordance with this Section 5."""

EXAMPLE_TEXT_3 = """13.1 Final payment shall be made by the Owner to the Contractor when (1) the Contract has been
fully performed by the Contractor except for the Contractor's responsibility to correct defective or nonconforming Work,
as provided in Subparagraph 12.2.2 of the General Conditions, and to satisfy other requirements, if any, which
necessarily survive final payment; (2) a final Application for Payment and a final accounting for the Cost of the Work
and all supporting documentation have been submitted by the Contractor and reviewed by the Owner's accountants; and (3)
a final Certificate for Payment has then been issued by the Architect; such final payment shall be made by the Owner
not more than 30 days after the issuance of the Architect's final Certificate for Payment, or as follows: 13.2 The
amount of the final payment shall be calculated as follows: 13.2.1 Take the sum of the Cost of the Work substantiated
by the Contractor's final accounting and the Contractor's Fee; but not more than the Guaranteed Maximum Price, if
any."""

EXAMPLE_TEXT_4 = """B. At Owner’s written request after Contractor’s initial submission of the Recovery Schedule,
Contractor shall participate in a conference with Owner, and with any other Person, including Subcontractors and
Sub-subcontractors, whom Owner designates to participate, to review and evaluate the Recovery Schedule. Any revisions
necessary as a result of this review shall be resubmitted for review by Owner within three (3) Business Days after the
conference. The revised Recovery Schedule, once agreed upon by Owner in writing, shall then be the schedule which
Contractor shall use in planning, organizing, directing, coordinating, performing, and executing the Work (including
all activities of Subcontractors and Sub-subcontractors) to regain compliance with the Key Milestone Schedule, the
Guaranteed Substantial Completion Date and the Required Final Completion Date. The agreed upon Recovery Schedule,
including any changes to the Key Milestone Dates, shall be incorporated into the CPM Performance Measurement Baseline
Schedule by Change Order; provided that the Guaranteed Substantial Completion Date shall not be adjusted by such
incorporation of the Recovery Schedule."""

EXAMPLE_TEXT_5 = """2.7. MATURITY. The Loans to the Borrower for a Project shall mature and shall be repaid in full,
together with accrued interest thereon, on the earlier of (x) the date which is 30 days following the date a
Certificate of Occupancy is issued for such Project, or (y) the 15th monthly anniversary of the date of the Notes
issued by the Borrower to the Lenders for such Project, SUBJECT to the following: (A) 3-MONTH CONSTRUCTION EXTENSION
OPTION. The Borrower may elect to extend the maturity date of the Loans for a particular Project for a period expiring
on the three month anniversary of the date such Loans otherwise would have matured as provided above, by giving the
Administrative Agent written notice of such election, PROVIDED that no such election or extension of the maturity date
of any Loans for a Project shall be or become effective if at the time any Default under section 10.1(a) or Event of
Default shall have occurred and be continuing."""


def test_get_durations():
    """
    Test durations.
    :return:
    """
    for i, example in enumerate(EXAMPLE_DURATIONS):
        print("Example {i}: {t}...".format(i=i, t=example[0][:40]))
        durations = get_durations(example[0], return_sources=False)
        assert_set_equal(set(durations), set(example[1]))


def test_get_durations_source():
    """
    Test durations with source.
    :return:
    """
    for i, example in enumerate(EXAMPLE_DURATIONS):
        print("Example {i}: {t}...".format(i=i, t=example[0][:40]))
        durations = get_durations(example[0], return_sources=True)
        assert_set_equal(set(durations), set(example[2]))
