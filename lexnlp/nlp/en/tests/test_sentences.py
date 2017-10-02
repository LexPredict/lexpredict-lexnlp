#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Imports
from nose.tools import nottest

from lexnlp.nlp.en.segments.sentences import get_sentences

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

#  Fake sample 1
SAMPLE_TEXT_1 = """Batman, Esq., J.D., M.B.A., is the author of 26 U.S.C. 501, i.e., the exemption section of the IRC.
Therefore, e.g., joke about INC. or LLC. entities.
Did you know that the I.R.S. loves to fine non-U.S. Acme Ltda. at c.a. 10:00A.M."""
SAMPLE_TEXT_1_RESULT = SAMPLE_TEXT_1.splitlines()

# Real sample 2
SAMPLE_TEXT_2 = """(A)  Definition of Normal Tenant Improvements. As used herein, "NORMAL TENANT
IMPROVEMENTS" shall mean any "below-ceiling" interior finishes and special
fixtures or equipment to be constructed for NAI within the Improvements as part
of the Construction Project, BUT WILL NOT INCLUDE (1) costs of structural
elements of the Construction Project, or (2) equipment that would be necessary
for the use of the Improvements by any lessee (e.g., HVAC equipment, elevators,
standard electrical wiring)."""
SAMPLE_TEXT_2_RESULT = ["""(A)  Definition of Normal Tenant Improvements.""",
                        """As used herein, "NORMAL TENANT
IMPROVEMENTS" shall mean any "below-ceiling" interior finishes and special
fixtures or equipment to be constructed for NAI within the Improvements as part
of the Construction Project, BUT WILL NOT INCLUDE (1) costs of structural
elements of the Construction Project, or (2) equipment that would be necessary
for the use of the Improvements by any lessee (e.g., HVAC equipment, elevators,
standard electrical wiring)."""]

# Real sample 3
SAMPLE_TEXT_3 = """NAI hereby unconditionally, unequivocally and irrevocably: (1) waives any
right to make any Issue 97-10 Election under any of the Operative Documents, and
(2) acknowledges and agrees that for purposes of calculating the Supplemental
Payment required by the Purchase Agreement, the Maximum Remarketing Obligation
will equal the Break Even Price under the Purchase Agreement."""
SAMPLE_TEXT_3_RESULT = [SAMPLE_TEXT_3]

# Real sample 4
SAMPLE_TEXT_4 = """All certificates, including Builder’s Certificate in form satisfactory for
recording with the U.S. Coast Guard, required to be furnished upon
delivery of the Vessel pursuant to this Contract and the Specifications.
If, through no fault on the part of Builder, the classification and/or
other certificates are not available at the time of delivery of the
Vessel, provisional certificates shall be accepted by Buyer, provided
that Builder shall furnish Buyer with the formal certificates as promptly
as possible after such formal certificates have been issued."""
SAMPLE_TEXT_4_RESULT = ["""All certificates, including Builder’s Certificate in form satisfactory for
recording with the U.S. Coast Guard, required to be furnished upon
delivery of the Vessel pursuant to this Contract and the Specifications.""",
                        """If, through no fault on the part of Builder, the classification and/or
other certificates are not available at the time of delivery of the
Vessel, provisional certificates shall be accepted by Buyer, provided
that Builder shall furnish Buyer with the formal certificates as promptly
as possible after such formal certificates have been issued."""]

# Real sample 5
SAMPLE_TEXT_5 = """If, at any time before the actual delivery, either the construction of the Vessel
or any performance required as a prerequisite of delivery of the Vessel are delayed
due to Acts of God; acts of princes or rulers; orders by government authorities;
war or other hostilities or preparations therefor; blockade; revolution,
insurrections, mobilization, civil war, civil commotion or riots; vandalism;
sabotages; general or local strikes, lockouts or other labor disturbances (other
than strikes, lockouts, or disturbances limited to personnel of Builder or
Shipyard); labor shortage (other than labor shortage limited to personnel of
Builder or Shipyard); plague or other epidemics; quarantines; flood, typhoons,
hurricanes, storms or other weather conditions not included in normal planning;
earthquakes; tidal waves; landslides; fires, explosions; embargoes;; import
restrictions; prolonged failure, shortage or restriction of electric current,
oil or gas supplied to Builder’s premises or the Shipyard; destruction of, or
damage to, the Shipyard or premises of Builder, its subcontractors or suppliers,
or of or to the Vessel or any part thereof, by any causes herein; or any other
events, causes or accidents beyond the reasonable control of either party hereto
which, despite the exercise of reasonable efforts by the affected party, makes
continuance of construction or performance hereunder impossible, the Delivery
Date shall be postponed for a period of time which shall not exceed the total
accumulated time of all such delays."""
SAMPLE_TEXT_5_RESULT = [SAMPLE_TEXT_5]

# Real sample 6
SAMPLE_TEXT_6 = """This First Amendment (this "Amendment") to the Employment
Agreement (the "Agreement"), dated as of April 19, 2001, by and between 3dfx
Interactive, Inc., a California corporation (the "Company"), and Richard A.
Heddleson ("Executive"), is made and entered into this 14th day of October,
2002. Capitalized terms used but not defined herein shall have the meanings
ascribed to those terms in the Agreement."""
SAMPLE_TEXT_6_RESULT = ["""This First Amendment (this "Amendment") to the Employment
Agreement (the "Agreement"), dated as of April 19, 2001, by and between 3dfx
Interactive, Inc., a California corporation (the "Company"), and Richard A.
Heddleson ("Executive"), is made and entered into this 14th day of October,
2002.""",
                        """Capitalized terms used but not defined herein shall have the meanings
ascribed to those terms in the Agreement."""]

# Real sample 7
SAMPLE_TEXT_7 = """The Employee further agrees that if, at some later date, a court of competent jurisdiction
determines that these covenants do not meet the criteria set forth in Tex. Bus. & Com. Code § 15.50(2),
these agreements shall be reformed by the court, pursuant to Tex. Bus. & Com. Code § 15.51(c), by the
least extent necessary to make them enforceable. Employee acknowledges and recognizes that the enforcement of
any of the provisions in this Agreement by Company will not interfere with the Employee’s ability to pursue
a proper livelihood."""
SAMPLE_TEXT_7_RESULT = ["""The Employee further agrees that if, at some later date, a court of competent jurisdiction
determines that these covenants do not meet the criteria set forth in Tex. Bus. & Com. Code § 15.50(2),
these agreements shall be reformed by the court, pursuant to Tex. Bus. & Com. Code § 15.51(c), by the
least extent necessary to make them enforceable.""",
                        """Employee acknowledges and recognizes that the enforcement of
any of the provisions in this Agreement by Company will not interfere with the Employee’s ability to pursue
a proper livelihood."""]

# Real sample 8
SAMPLE_TEXT_8 = """This Executive Employment Agreement (hereinafter referred to as the “Agreement”) has been entered
into this 4th day of May, 2011, with effect from May 1, 2011, by and between Identive Group, Inc., a Delaware
corporation, having its principal executive offices at 1900-B Carnegie Ave., Santa Ana, CA 92705, United States of
America (hereinafter together with all the companies directly and indirectly controlled by it referred to as the
“Company”) and Melvin Denton-Thompson, an individual being resident in Paris, France (hereinafter referred to as the
“Executive”)."""
SAMPLE_TEXT_8_RESULT = [SAMPLE_TEXT_8]

# Real sample 9
SAMPLE_TEXT_9 = """(a) As compensation for the services to be rendered by Executive pursuant to this Agreement,
the Company hereby agrees to pay Executive a base monthly salary (“Base Monthly Salary”) at a rate equal to
Thirty-Five Thousand Dollars ($35,000.00) per month. The Base Monthly Salary shall be paid in substantially
equal bimonthly installments, in accordance with the normal payroll practices of the Company. While employed by
the Company, you will not receive any compensation for your service as a member of the Company’s Board or any
of its committees."""
SAMPLE_TEXT_9_RESULT = ["""(a) As compensation for the services to be rendered by Executive pursuant to this Agreement,
the Company hereby agrees to pay Executive a base monthly salary (“Base Monthly Salary”) at a rate equal to
Thirty-Five Thousand Dollars ($35,000.00) per month.""",
                        """The Base Monthly Salary shall be paid in substantially
equal bimonthly installments, in accordance with the normal payroll practices of the Company.""",
                        """While employed by
the Company, you will not receive any compensation for your service as a member of the Company’s Board or any
of its committees."""]

# Real sample 10
SAMPLE_TEXT_10 = """For purposes of §409A, the amounts deferred as annual or discretionary contributions and benefits 
attributable thereto, shall be considered an nonelective account balance plan as defined in Treas. Reg. 
§1.409A -1(c)(2)(i)(B), or as otherwise provided by the Code."""
SAMPLE_TEXT_10_RESULT = [SAMPLE_TEXT_10]

# Real sample 11
SAMPLE_TEXT_11 = """Encorium Germany GmbH, with registered office in Cologne, represented by Dr. Kai E. Lindevall,
Chief Executive Officer, Encorium Group, Inc. (hereinafter Company” or “Employer”) and Dr. Renee E. Moore, born May 2,
1969, with an address at XYZ (hereinafter “Renée Moore”) hereby enter into the following Employment
Contract (hereinafter “Contract”):"""
SAMPLE_TEXT_11_RESULT = [SAMPLE_TEXT_11]


@nottest
def run_sentence_test(text, result):
    """
    Base test method to run against text with given results.
    """
    # Get list from text
    sentence_list = get_sentences(text)

    # Check length first
    assert len(sentence_list) == len(result)

    # Check each sentence matches
    for sentence in sentence_list:
        assert sentence in result


def test_sentence_segmenter_empty():
    """
    Test basic sentence segmentation.
    """
    _ = get_sentences("")


def test_sentence_segmenter_1():
    """
    Test basic sentence segmentation.
    """
    run_sentence_test(SAMPLE_TEXT_1, SAMPLE_TEXT_1_RESULT)


def test_sentence_segmenter_2():
    """
    Test basic sentence segmentation.
    """
    run_sentence_test(SAMPLE_TEXT_2, SAMPLE_TEXT_2_RESULT)


def test_sentence_segmenter_3():
    """
    Test basic sentence segmentation.
    """
    run_sentence_test(SAMPLE_TEXT_3, SAMPLE_TEXT_3_RESULT)


def test_sentence_segmenter_4():
    """
    Test basic sentence segmentation.
    """
    run_sentence_test(SAMPLE_TEXT_4, SAMPLE_TEXT_4_RESULT)


def test_sentence_segmenter_5():
    """
    Test basic sentence segmentation.
    """
    run_sentence_test(SAMPLE_TEXT_5, SAMPLE_TEXT_5_RESULT)


def test_sentence_segmenter_6():
    """
    Test basic sentence segmentation.
    """
    run_sentence_test(SAMPLE_TEXT_6, SAMPLE_TEXT_6_RESULT)


def test_sentence_segmenter_7():
    """
    Test basic sentence segmentation.
    """
    run_sentence_test(SAMPLE_TEXT_7, SAMPLE_TEXT_7_RESULT)


def test_sentence_segmenter_8():
    """
    Test basic sentence segmentation.
    """
    run_sentence_test(SAMPLE_TEXT_8, SAMPLE_TEXT_8_RESULT)


def test_sentence_segmenter_9():
    """
    Test basic sentence segmentation.
    """
    run_sentence_test(SAMPLE_TEXT_9, SAMPLE_TEXT_9_RESULT)


def test_sentence_segmenter_10():
    """
    Test basic sentence segmentation.
    """
    run_sentence_test(SAMPLE_TEXT_10, SAMPLE_TEXT_10_RESULT)


def test_sentence_segmenter_11():
    """
    Test basic sentence segmentation.
    """
    run_sentence_test(SAMPLE_TEXT_11, SAMPLE_TEXT_11_RESULT)
