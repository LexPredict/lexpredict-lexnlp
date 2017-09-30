#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Imports
from lexnlp.nlp.en.segments.pages import get_pages

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

# Real world example
DOCUMENT_EXAMPLE_1 = """SECTION 1.1. LINE OF CREDIT.

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

"""
DOCUMENT_EXAMPLE_1_RESULT = [
    'SECTION 1.1. LINE OF CREDIT.\n\n(a) Line of Credit. Subject to the terms and conditions of this\nAgreement, '
    'Bank hereby agrees to make advances to Borrower from time to time up\nto and including May 1, 1998, not to '
    'exceed at any time the aggregate principal\namount of Twenty Million Dollars ($20,000,000.00) ("Line of Credit"), '
    'the\nproceeds of which shall be used for working capital purposes. Borrower\'s\nobligation to repay advances '
    'under the Line of Credit shall be evidenced by a\npromissory note substantially in the form of Exhibit A attached '
    'hereto ("Line of\nCredit Note"), all terms of which are incorporated herein by this reference.\n\n(b) Subfeature. '
    'Subject to the terms and conditions of this Agreement,\nBank hereby agrees to make advances to Smart(Europe) from '
    'time to time up to and\nincluding May 1, 1998, not to exceed at any time the aggregate principal amount\nof Ten '
    'Million Dollars ($10,000,000.00) ("Subfeature"), the proceeds of which\nshall be used for working capital '
    'purposes. Smart(Europe)\'s obligation to repay\nadvances under the Subfeature shall be evidenced by a promissory '
    'note\nsubstantially in the form of Exhibit B attached hereto ("Smart (Europe) Note"),\nall terms of which are '
    'incorporated herein by this reference. The outstanding\nprincipal balance of advances and the available undrawn '
    'balance of Letters of\nCredit issued under the Subfeature\n\n',
    '<PAGE>   2\nshall be reserved under the Line of Credit and shall not be available for\nadvances or Letters of '
    'Credit thereunder.\n\n(c) Letter of Credit Subfeature. As a subfeature under the Line of\nCredit and Subfeature, '
    'Bank agrees from time to time during the term thereof to\nissue sight commercial and standby letters of credit '
    'for the account of Borrower\nor Smart(Europe), respectively, to finance working capital and '
    'business\nrequirements (each, a "Letter of Credit" and collectively, "Letters of Credit");\nprovided however, '
    'that the form and substance of each Letter of Credit shall be\nsubject to approval by Bank, in its sole '
    'discretion; and provided further, that\nthe aggregate undrawn amount of all outstanding Letters of Credit shall '
    'not at\nany time exceed Four Million Dollars ($4,000,000.00). No Letter of Credit shall\nhave an expiration date '
    'subsequent to the maturity date of the Line of Credit.\nThe undrawn amount of all Letters of Credit for the '
    'account of Borrower shall be\nreserved under the Line of Credit and the undrawn amount of all Letters of\nCredit '
    'for the account of Smart(Europe) shall be reserved under the Subfeature\nand shall not be available for '
    'borrowings thereunder. Each Letter of Credit\nshall be subject to the additional terms and conditions of the '
    'Letter of Credit\nAgreement and related documents, if any, required by Bank in connection with the\nissuance '
    'thereof (each, a "Letter of Credit Agreement" and collectively, "Letter\nof Credit Agreements"). Each draft paid '
    'by Bank under a Letter of Credit shall\nbe deemed an advance under the Line of Credit or Subfeature, as '
    'applicable, and\nshall be repaid by Borrower or Smart(Europe), in accordance with the terms and\nconditions of '
    'this Agreement applicable to such advances; provided however, that\nif advances under the Line of Credit or '
    'Subfacility, as applicable, are not\navailable, for any reason, at the time any draft is paid by Bank, then '
    'Bank\nshall so notify Borrower or Smart(Europe), as applicable, and Borrower or\nSmart(Europe) shall immediately '
    'pay to Bank the full amount of such draft,\ntogether with interest thereon from the date such amount is paid by '
    'Bank to the\ndate such amount is fully repaid by Borrower or Smart(Europe), at the rate of\ninterest applicable to'
    ' advances under the Line of Credit. In such event Borrower\nagrees that Bank, in its sole discretion, may debit '
    'any demand deposit account\nmaintained by Borrower with Bank for the amount of any such draft.\n\n(d) Borrowing '
    'and Repayment. Borrower or Smart(Europe) may from time to\ntime during the terms of the Line of Credit and '
    'Subfeature, respectively borrow,\npartially or wholly repay its outstanding borrowings, and reborrow, subject '
    'to\nall of the limitations, terms and conditions contained herein or in the Line of\nCredit Note and Smart(Europe)'
    'Note, respectively; provided however, that the\ntotal outstanding borrowings under the Line of Credit an '
    'Subfeature shall not at\nany time exceed the respective\n\n\n'
]

DOCUMENT_EXAMPLE_2 = """This Agreement is dated as of June 28, 2001 by and between ROBERTS
PROPERTIES RESIDENTIAL, L.P., a Georgia limited partnership ("Borrower"), having
its address at 8010 Roswell Road, Suite 120, Atlanta, Georgia 30350, Attention:
Chief Financial Officer, and BANK OF NORTH GEORGIA, ("Bank") having an address
at 8025 Westside Parkway, Alpharetta, Georgia 30004;

In consideration of the Loan described below and the mutual covenants
and agreements contained herein, and intending to be legally bound hereby, Bank
and Borrower agree as follows:

1. Definitions and Reference Terms. In addition to any other terms
defined herein, the following terms shall have the meanings set forth with
respect thereto:

(a) Agent to Request Disbursements: Charles S. Roberts or
Charles R. Elliott


(b) Architect: Lyman Davidson Dooley, Inc.

(c) Budget: The budget attached hereto as Exhibit A setting
forth in detail all direct and indirect costs for the construction of the
Improvements.

(d) Completion Date: February 28, 2002.


(e) Construction Commitment: The agreement between Borrower
and Bank dated June 21, 2001, and attached hereto as Exhibit B, the terms of
which are incorporated herein.

(f) Contractor: Roberts Properties Construction, Inc.


(g) Guarantor: Not applicable.


(h) Guaranty: Not applicable.

(i) Hazardous Materials: All materials defined as hazardous
wastes or substances under any local, state or federal environmental laws, rules
or regulations, and petroleum, petroleum products, oil and asbestos.

(j) Improvements: The buildings and other improvements
constructed or to be constructed on the Land, generally including the following:
37,864 square foot office building fronting on Northridge Parkway, Atlanta,
Fulton County, Georgia, with associated site work.

(k) Inspecting Agent: USA Inspection Services, LLC



<PAGE>





(l) Land: The land located at Land Lots 25 and 26 in the 17th
District, Fulton County, Georgia as more particularly described in the Mortgage
and any additional property which may become subject to the Mortgage.

(m) Loan: The loan in the principal amount of up to
$5,280,000.00 for the financing and construction of the Premises in accordance
with this Agreement.

(n) Loan Documents: This Agreement and the Construction
Commitment (and all items and documents required therein), the Note, the
Mortgage, and all other instruments, documents and agreements required by Bank
which evidence, secure or otherwise relate to the Loan including, without
limitation, any guaranties, financing statements, assignments of lessor's
interest in leases, rents and profits, and assignments of construction
documents, together with any amendments, renewals, and extensions thereof, all
of which are incorporated herein by reference and made a part hereof. References
herein to the Loan Documents shall include all such documents, instruments and
other agreements collectively, except that any such reference shall mean the
appropriate individual document, instrument or agreement if the context shall so
require.

(o) Mortgage: The first lien mortgage, deed of trust, or deed
to secure debt and security agreement securing the Note and the performance of
Borrower's obligations with respect to the Loan, and all amendments, renewals
and extensions thereof.

(p) Note: The promissory note or notes and other instruments,
documents or agreements evidencing Borrower's indebtedness for the Loan, and all
amendments, renewals and extensions thereof.

(q) Obligors: The Borrower and all other makers, co-makers,
endorsers, guarantors and others obligated, primarily or secondarily, for the
payment of the indebtedness evidenced by the Note or performance of Borrower's
obligations under the Loan Documents (including, without limitation, all general
partners of Borrower if Borrower, is a partnership), collectively.

(r) Plans: The plans and specifications entitled "Roberts
Properties, Inc. Corporate Headquarters, Fulton County" prepared by Lyman
Davidson Dooley, Inc. last revised January 31, 2001 and all amendments thereto
approved by Bank.

(s) Premises. The Land and the Improvements,

2. Loan. Subject to the terms and conditions of this Agreement and the
Loan Documents, Bank agrees to lend to Borrower (in periodic disbursements) up
to the principal sum set forth in Section 1 (m) hereof. The Loan shall bear
interest at the rate or rates set forth in the Note and shall be evidenced
thereby and secured by the Mortgage and other Loan Documents.


2
<PAGE>


3. Representations and Warranties of Borrower. As an inducement to Bank
to enter into this Agreement and to make the Loan, Borrower represents and
warrants to Bank as follows:

(a) Borrower Organization. Borrower is duly organized and
existing in good standing under the laws of the state of its organization and is
duly qualified in the state where the Land is located to own, construct and
operate the Improvements. Borrower has the authority and the legal right to
carry on the business now being conducted by it and to engage in the
transactions contemplated by the Loan Documents.

(b) Binding Documents. The Loan Documents are legal, valid and
binding in accordance with their terms and have been duly authorized, executed
and delivered.

(c) Legal and Environmental Compliance. The Plans for the
Improvements and the anticipated use of the Premises and all easements and
rights appurtenant thereto comply with all applicable restrictive covenants,
zoning ordinances, building laws and codes, and other laws, regulations and
governmental requirements, including but not limited to those regarding
environmental matters and access and facilities for persons with disabilities.
All permits and approvals necessary to continue work on the Premises, including-
without limitation all building and site work permits, have been obtained by
Borrower.

During Borrower's ownership of the Premises and to the best of
Borrower's knowledge prior thereto, the Premises have not been used in violation
of any federal laws, rules or ordinances for environmental protection,
regulations of the Environmental Protection Agency and any applicable local or
state law, rule, regulation or rule of common law and any judicial
interpretation thereof relating primarily to the environment or Hazardous
Materials. Borrower will not use or permit any other party to use any Hazardous
Materials on the Premises except such materials as are incidental to Borrower's
normal course of business, maintenance and repairs and which are handled in
compliance with all applicable environmental laws.

(d) Utilities Availability. All utility services necessary for
the construction and full utilization of the Premises for their intended
purposes are presently available at the boundaries of the Land through public or
unencumbered private easements or rights of way and are available for connection
to the Improvements at ordinary costs.

(e) Access to the Premises. Access necessary for the
construction and full utilization of the Premises for their intended purposes is
presently available to the Premises over private easement areas and/or streets
or roads which have been dedicated to public use and accepted therefor by
appropriate governmental authorities and any permits necessary for connecting
the driveways on the Premises to such streets or roads will be obtained if
necessary.

(f) Financial Statements. Each financial statement delivered
to Bank in connection with the Loan is true and correct in all material
respects, has been prepared in accordance with generally accepted accounting
principles consistently applied, and fairly

3

<PAGE>

represents the financial condition of its subject, and no material, adverse
change has occurred in the financial condition of its subject since the date
thereof.
"""
DOCUMENT_EXAMPLE_2_RESULT = [
    'This Agreement is dated as of June 28, 2001 by and between ROBERTS\nPROPERTIES RESIDENTIAL, L.P., a Georgia '
    'limited partnership ("Borrower"), having\nits address at 8010 Roswell Road, Suite 120, Atlanta, Georgia 30350, '
    'Attention:\nChief Financial Officer, and BANK OF NORTH GEORGIA, ("Bank") having an address\nat 8025 Westside '
    'Parkway, Alpharetta, Georgia 30004;\n\nIn consideration of the Loan described below and the mutual '
    'covenants\nand agreements contained herein, and intending to be legally bound hereby, Bank\nand Borrower agree '
    'as follows:\n\n1. Definitions and Reference Terms. In addition to any other terms\ndefined herein, the following '
    'terms shall have the meanings set forth with\nrespect thereto:\n\n(a) Agent to Request Disbursements: Charles S. '
    'Roberts or\nCharles R. Elliott\n\n\n(b) Architect: Lyman Davidson Dooley, Inc.\n\n(c) Budget: The budget attached '
    'hereto as Exhibit A setting\nforth in detail all direct and indirect costs for the construction of '
    'the\nImprovements.\n\n(d) Completion Date: February 28, 2002.\n\n\n(e) Construction Commitment: The agreement '
    'between Borrower\nand Bank dated June 21, 2001, and attached hereto as Exhibit B, the terms of\nwhich are '
    'incorporated herein.\n\n(f) Contractor: Roberts Properties Construction, Inc.\n\n\n(g) Guarantor: Not '
    'applicable.\n\n\n(h) Guaranty: Not applicable.\n\n(i) Hazardous Materials: All materials defined as '
    'hazardous\nwastes or substances under any local, state or federal environmental laws, rules\nor regulations, '
    'and petroleum, petroleum products, oil and asbestos.\n\n(j) Improvements: The buildings and other '
    'improvements\nconstructed or to be constructed on the Land, generally including the following:\n37,864 square '
    'foot office building fronting on Northridge Parkway, Atlanta,\nFulton County, Georgia, with associated site '
    'work.\n\n(k) Inspecting Agent: USA Inspection Services, LLC\n\n\n',
    '<PAGE>\n\n\n\n\n\n(l) Land: The land located at Land Lots 25 and 26 in the 17th\nDistrict, Fulton County, '
    'Georgia as more particularly described in the Mortgage\nand any additional property which may become subject to '
    'the Mortgage.\n\n(m) Loan: The loan in the principal amount of up to\n$5,280,000.00 for the financing and '
    'construction of the Premises in accordance\nwith this Agreement.\n\n(n) Loan Documents: This Agreement and the '
    'Construction\nCommitment (and all items and documents required therein), the Note, the\nMortgage, and all other '
    'instruments, documents and agreements required by Bank\nwhich evidence, secure or otherwise relate to the Loan '
    'including, without\nlimitation, any guaranties, financing statements, assignments of lessor\'s\ninterest in '
    'leases, rents and profits, and assignments of construction\ndocuments, together with any amendments, renewals, '
    'and extensions thereof, all\nof which are incorporated herein by reference and made a part hereof. '
    'References\nherein to the Loan Documents shall include all such documents, instruments and\nother agreements '
    'collectively, except that any such reference shall mean the\nappropriate individual document, instrument or '
    'agreement if the context shall so\nrequire.\n\n(o) Mortgage: The first lien mortgage, deed of trust, or deed\nto '
    'secure debt and security agreement securing the Note and the performance of\nBorrower\'s obligations with respect '
    'to the Loan, and all amendments, renewals\nand extensions thereof.\n\n(p) Note: The promissory note or notes '
    'and other instruments,\ndocuments or agreements evidencing Borrower\'s indebtedness for the Loan, and '
    'all\namendments, renewals and extensions thereof.\n\n(q) Obligors: The Borrower and all other makers, '
    'co-makers,\nendorsers, guarantors and others obligated, primarily or secondarily, for the\npayment of the '
    'indebtedness evidenced by the Note or performance of Borrower\'s\nobligations under the Loan Documents '
    '(including, without limitation, all general\npartners of Borrower if Borrower, is a partnership), '
    'collectively.\n\n(r) Plans: The plans and specifications entitled "Roberts\nProperties, Inc. Corporate '
    'Headquarters, Fulton County" prepared by Lyman\nDavidson Dooley, Inc. last revised January 31, 2001 and all '
    'amendments thereto\napproved by Bank.\n\n(s) Premises. The Land and the Improvements,\n\n2. Loan. Subject to '
    'the terms and conditions of this Agreement and the\nLoan Documents, Bank agrees to lend to Borrower (in periodic '
    'disbursements) up\nto the principal sum set forth in Section 1 (m) hereof. The Loan shall bear\ninterest at the '
    'rate or rates set forth in the Note and shall be evidenced\nthereby and secured by the Mortgage and other Loan '
    'Documents.\n\n\n2',
    "<PAGE>\n\n\n3. Representations and Warranties of Borrower. As an inducement to Bank\nto enter into this Agreement "
    "and to make the Loan, Borrower represents and\nwarrants to Bank as follows:\n\n(a) Borrower Organization. "
    "Borrower is duly organized and\nexisting in good standing under the laws of the state of its organization and "
    "is\nduly qualified in the state where the Land is located to own, construct and\noperate the Improvements. "
    "Borrower has the authority and the legal right to\ncarry on the business now being conducted by it and to engage "
    "in the\ntransactions contemplated by the Loan Documents.\n\n(b) Binding Documents. The Loan Documents are legal, "
    "valid and\nbinding in accordance with their terms and have been duly authorized, executed\nand delivered.\n\n(c) "
    "Legal and Environmental Compliance. The Plans for the\nImprovements and the anticipated use of the Premises and "
    "all easements and\nrights appurtenant thereto comply with all applicable restrictive covenants,\nzoning "
    "ordinances, building laws and codes, and other laws, regulations and\ngovernmental requirements, including but "
    "not limited to those regarding\nenvironmental matters and access and facilities for persons with disabilities."
    "\nAll permits and approvals necessary to continue work on the Premises, including-\nwithout limitation all "
    "building and site work permits, have been obtained by\nBorrower.\n\nDuring Borrower's ownership of the Premises "
    "and to the best of\nBorrower's knowledge prior thereto, the Premises have not been used in violation\nof any "
    "federal laws, rules or ordinances for environmental protection,\nregulations of the Environmental Protection "
    "Agency and any applicable local or\nstate law, rule, regulation or rule of common law and any "
    "judicial\ninterpretation thereof relating primarily to the environment or Hazardous\nMaterials. Borrower will "
    "not use or permit any other party to use any Hazardous\nMaterials on the Premises except such materials as are "
    "incidental to Borrower's\nnormal course of business, maintenance and repairs and which are handled in\ncompliance "
    "with all applicable environmental laws.\n\n(d) Utilities Availability. All utility services necessary for\nthe "
    "construction and full utilization of the Premises for their intended\npurposes are presently available at the "
    "boundaries of the Land through public or\nunencumbered private easements or rights of way and are available for "
    "connection\nto the Improvements at ordinary costs.\n\n(e) Access to the Premises. Access necessary for "
    "the\nconstruction and full utilization of the Premises for their intended purposes is\npresently available to "
    "the Premises over private easement areas and/or streets\nor roads which have been dedicated to public use and "
    "accepted therefor by\nappropriate governmental authorities and any permits necessary for connecting\nthe "
    "driveways on the Premises to such streets or roads will be obtained if\nnecessary.\n\n(f) Financial Statements. "
    "Each financial statement delivered\nto Bank in connection with the Loan is true and correct in all "
    "material\nrespects, has been prepared in accordance with generally accepted accounting\nprinciples consistently "
    "applied, and fairly\n\n3\n",
    "<PAGE>represents the financial condition of its subject, and no material, adverse change has occurred in the "
    "financial condition of its subject since the date thereof."
]


def test_page_example_1():
    def remove_whitespace(r):
        return r.replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")

    # Get list of pages
    page_list = list(get_pages(DOCUMENT_EXAMPLE_1))
    assert len(page_list) == len(DOCUMENT_EXAMPLE_1_RESULT)
    clean_result = [remove_whitespace(p) for p in DOCUMENT_EXAMPLE_1_RESULT]
    for page in page_list:
        assert remove_whitespace(page) in clean_result


def test_page_example_2():
    def remove_whitespace(r):
        return r.replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")

    # Get list of pages
    page_list = list(get_pages(DOCUMENT_EXAMPLE_2))
    assert len(page_list) == len(DOCUMENT_EXAMPLE_2_RESULT)
    clean_result = [remove_whitespace(p) for p in DOCUMENT_EXAMPLE_2_RESULT]
    for page in page_list:
        assert remove_whitespace(page) in clean_result
