# !/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Date unit tests for English.

This module implements unit tests for the date extraction functionality in English.

Todo:
    * Implement document-level date detection to identify anomalous dates
    * Better testing for exact test in return sources
    * Resolve example bad dates
    * More pathological and difficult cases
"""

# Imports
import datetime
import random
import string

from nose.tools import assert_list_equal, assert_set_equal, assert_dict_equal, assert_equal

from lexnlp.extract.en.dates import get_dates, get_date_features, get_raw_dates, train_default_model

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

EXAMPLE_TEXT_1 = """Dear Jerry:
This amended and restated letter agreement sets forth the terms of your employment with Logitech Inc., a California 
corporation (the “Company”), as well as our understanding with respect to any termination of that employment 
relationship. Effective on the date set forth above, this letter agreement supersedes your offer letter dated January
28, 2008, in its entirety."""

# TODO: Improve classifier to handle
EXAMPLE_BAD_DATES = [
    ("""56 of March 22nd, 1983; Seismic Code by Executive Decree No.""",
     [datetime.date(1983, 3, 22)]),
]

EXAMPLE_FIXED_RAW_DATES = [("""No later than 2017-06-01.""", [datetime.date(2017, 6, 1)]),
                           ("""Dated as of June 1, 2017""",
                            [datetime.date(2017, 6, 1)]),
                           ("""Will be completed by June 2017""",
                            [datetime.date(2017, 6, 1)]),
                           ("""Will be completed by June""",
                            [datetime.date(2017, 6, 1)]),
                           ("""Will be completed by the 1st day of June, 2017""", [
                               datetime.date(2017, 6, 1)])]

EXAMPLE_FIXED_DATES = [("""No later than 2017-06-01.""", [datetime.date(2017, 6, 1)]),
                       ("""2. Amendment to Interest Rate. Beginning on February 1, 1998, and
        continuing until July 18, 2002, which is the fifth anniversary of the Loan
        conversion date, interest shall be fixed at an annual rate of 7.38%, which rate
        is equal to 200 basis points above the Bank's five-year "Treasury Constant
        Rate" in effect on January 23, 1998. In accordance with the Agreement, the
        interest rate shall be adjusted again on July 18, 2002.""",
                        [datetime.date(1998, 2, 1), datetime.date(2002, 7, 18), datetime.date(1998, 1, 23),
                         datetime.date(2002, 7, 18)]),
                       ("""THIS AGREEMENT, effective the 1st day of January, 2001, by and between Pharmaceutical Product
                       Development, Inc. and its subsidiaries and affiliates (collectively, “PPD”) and (“Employee”).""",
                        [datetime.date(2001, 1, 1)]),
                       (
                           """27.1 Notice of Default 1-71 27.2 Contractor's Default 1-72 27.3 Valuation at Date of
                           Termination 1-72 27.4 Payment After Termination 1-72 27.5 Effect on Liability for Delay
                           1-72 27.6 Employer's Default 1-73 27.7 Removal of Contractor's Equipment 1-73 27.8 Payment
                           on Termination for Employer's Default 1-73""",
                           []),
                       (
                           """18.1 Methods of Application 1-57 18.2 Issue of Certificate of payment 1-57 18.3
                           Corrections to Certificates of Payment 1-58 18.4 Payment 1-58 18.5 Delayed Payment 1-58
                           18.6 Remedies on Failure to Certify or Make Payment 1-58 18.7 Application for Final
                           Certificate of Payment 1-59 18.8 Issue of final Certificate of Payment 1-59 18.9 Final
                           Certificate of Payment conclusive 1-60 18.10 Advance Payment 1-60 18.11 Advance Payment
                           Guarantee 1-60 18.12 Terms of Payment 1-60 18.13 Retention 1-61""",
                           []),
                       (
                           """30.1 Customs, Import Duties and Taxes 1-74 30.2 Clearance Through Customs 1-75 30.3
                           Taxation 1-75 30.4 Customs and Taxes on Contractor's Equipment 1-75""",
                           []),
                       (
                           """16.1 Engineer's Right to Vary 1-53 16.2 Variation in Excess of 5% 1-54 16.3 Variation
                           Order Procedure 1-54 16.4 Disagreement on Adjustment of Contract Price 1-55 16.5 Variation
                           on Manufacture and Drawings 1-55 16.6 Contractor to Proceed 1-56 16.7 Records of Costs 1-56
                           16.8 Monthly Variations Statement 1-56""",
                           []),
                       ("""THIS  AGREEMENT  entered into this 19th day of March,  2007, by and between
The Patapsco Bank (the "Bank"),  and Michael J. Dee (the "Employee"),  effective
on the date above (the "Effective Date").""", [datetime.date(2007, 3, 19)]),
                       ("""Dated as of June 1, 2017""",
                        [datetime.date(2017, 6, 1)]),
                       ("""Dated as of June 10000000000000000000000000000000000, 2017""", []),
                       ("""Size 19 1/2" L x 7/8" H.""", []),
                       ("""Will be completed by June 2017""",
                        [datetime.date(2017, 6, 1)]),
                       ("""3. The Delivery of the Vessel shall be deferred and the revised Delivery Date shall be
                       30 July 2017. Parties shall, following execution of this Amendment No. 1, discuss and agree on 
                       the necessary changes to the Programme (i.e. Paragraph 4.1 of the Contract), so as to effect 
                       the revised Delivery Date. To the extent the Parties have yet to agree or have not agreed on 
                       necessary changes to the Programme, all references to the Programme in the Contract shall 
                       operate on the basis that (1) KD7 (Commencement of Commissioning Process) is revised to 31
                       October 2016 and (2) KD 11 (Delivery of the Vessel) is revised to 30 July 2017, and all other 
                       milestones and Key Dates are inoperative.""",
                        [datetime.date(2017, 7, 30), datetime.date(2016, 10, 31)]),
                       ("""11.1 Notice of Tests 1-41 11.2 Time for Tests 1-41 11.3 Delayed Tests 1-42 11.4 Facilities
                           for Tests on Completion 1-42 11.5 Notice of Test Results 1-42 11.6 Retesting 1-42 11.7
                           Disagreement as to Result of Test 1-43 11.8 Consequences of Failure to Pass Tests 1-43 on
                           Completion 11.9 Test Certificate 1-43 11.10 Test by Employer's Operators 1-44""",
                        []),
                       ("""Will be completed by June""",
                        [datetime.date(2017, 6, 1)]),
                       ("""Will be completed by the 1st day of June, 2017""",
                        [datetime.date(2017, 6, 1)]),
                       ("""Will be completed by the 1st day of June 2017""",
                        [datetime.date(2017, 6, 1)]),
                       ("""Will be completed by the 1st of June, 2017""",
                        [datetime.date(2017, 6, 1)]),
                       ("""Will be completed by the 1st of June 2017""",
                        [datetime.date(2017, 6, 1)]),
                       ("""section on 6.25""", []),
                       (
                           """All work shall be completed in accordance with WDD sketch dated 15 March 2005 and Hansen
                           Mechanical COR.""",
                           [datetime.date(2005, 3, 15)]),
                       (
                           """Cost Plus Incentive Construction Contract with JH Kelly LLC On August 8, 2007, Hoku
                           Materials, Inc. entered into a construction agreement, the Construction Agreement, with
                           JH Kelly LLC., or JH Kelly, for construction services for the construction of a polysilicon
                           production plant with an annual capacity of 2,000 metric tons.""",
                           [datetime.date(2007, 8, 8)]),
                       (
                           """SUBTOTAL 35,842,000 PROJECT REQUIREMENTS 1,281,000 CONSTRUCTION CONTINGENCY 1,075,000
                           TRAILER RELOCATION ALLOWANCE 50,000 SCHEDULE ADJUSTMENT 357,000 HOIST/ELEVATOR OPERATOR
                           104,000 GENERAL CONDITIONS 1,481,000 FEE 1,306,000 G. C. PAYMENT & PERFORMANCE BOND 204,000
                           - ----------------- ============================================================
                           ================== ================= TOTAL CONSTRUCTION COSTS 41,700,000 - -----------------
                           ============================================================ ==================
                           =================""",
                           []),
                       ("""4-7-98 Date Date""", [datetime.date(1998, 4, 7)]),
                       ("""4/7/98 Date Date""", [datetime.date(1998, 4, 7)]),
                       (
                           """This monthly maintenance and support arrangement will have an initial term of six (6)
                           months. The arrangement will then automatically renew for an additional twelve (12) months
                           at the above rates and conditions unless written notification to US/INTELICOM of Licensee's
                           intent to cancel the arrangement is received no later than September 1, 1998. Unless
                           Licensee elects to cancel this arrangement at the end of the first six months, the "initial
                           term" of the arrangement will be through September 30, 1999.""",
                           [datetime.date(1998, 9, 1), datetime.date(1999, 9, 30)]),
                       (
                           """CLASSIFICATION	  	STRAIGHT TIME TIME & A HALF    	 	DOUBLE TIME PIPEFITTERS LOCAL
                           #26 LV ZONE 5,6,7""",
                           []),
                       (
                           """Action	NBBB Milestone Dates - All AFC	Date required Owner	General Arrangement Frozen
                           [*] Jensen/Owner	Steel design Main Deck and Below	[*] Jensen/Owner	General Arrangement
                           [*] Jensen/Owner	Tonnage Openings	[*] Jensen/Owner	Electrical Single Line	[*] Owner
                           Interior finish schedule	[*] Owner	Room layouts Cabins	[*] Owner	Food Service Space
                           Layouts	[*] Owner	Public Space layouts	[*] Jensen/Owner	GW Piping Diagrams	[*]
                           Jensen/Owner	BW Piping Diagrams	[*] Jensen/Owner	PW Piping Diagrams	[*] Jensen/Owner
                           Fire Main Piping Diagrams	[*] Jensen/Owner	Steel design Modules 4 and 5	[*]
                           Jensen/Owner	Steel design Modules 6,7,8	[*] Jensen/Owner	Fire Zones	[*] Jensen/Owner
                           Heat load data (inc OFE)	[*] Owner	Owner Equip Information/Heat Load data	[*] Jensen/Owner
                           Main Wireway routing	[*] NBBBJensen	FGS Diagram	[*] NBBBJensen	PAGA Diagram	[*]
                           NBBBJensen	Telephone Diagram	[*]""",
                           []),
                       ("""9.6.6,9,8.2,9.9.3,9.10.1,9.103, 12.3""", []),
                       (
                           """NOW, THEREFORE, for good and valuable consideration, the receipt and sufficiency of which
                           are hereby acknowledged, the parties mutually agree as follows: 1. License Grant. NECTAR
                           hereby grants to Siboney an exclusive license and right in the United States, its territories
                           and possessions, to use, revise, modify and create derivative works of the "MathTrek 1,2,3",
                           "MathTrek 4,5,6" and "Math Trek 7,8,9" software program series (the "Licensed Software") for
                           use on Macintosh and Windows operating systems, and to repackage, manufacture, market,
                           distribute, sell, lease, license and sub-license such revised and/or modified Licensed
                           Software. Such revisions, modifications and derivative works are referred to herein as
                           "Modified Software". The foregoing licenses to Siboney are subject to NECTAR's right set
                           forth in Section 2 hereof, and to any licenses previously granted by NECTAR to end-users of
                           the Licensed Software. Siboney shall have no rights in the Licensed Software or Modified
                           Software other than as set forth in this Agreement. NECTAR shall, as reasonably requested by
                           Siboney, consult with Siboney concerning such revisions, modifications and the like, and all
                           revisions and the like will be subject to NECTAR's approval, which shall not be unreasonably
                           withheld. NECTAR shall receive one (1) copy of every commercial product created pursuant to
                           this license.""",
                           []),
                       (
                           """NECTAR hereby grants to Siboney an exclusive license and right in the United States, its
                           territories and possessions, to use, revise, modify and create derivative works of the
                           "MathTrek 1,2,3", "MathTrek 4,5,6" and "Math Trek 7,8,9" software program series (the
                           "Licensed Software") for use on Macintosh and Windows operating systems, and to repackage,
                           manufacture, market, distribute, sell, lease, license and sub-license such revised and/or
                           modified Licensed Software.""",
                           []),
                       ("""3.18.1, 6.1.1, 7.3.6, 8,2.1, 9.3.2, 9.8.4, 9.9.1,""", []),
                       ("""Total OCIP Credits 19,867,980""", []),
                       ("""3.11,42.8,7, 8.3.1, 9.3.1.1, 11.4.9""", []),
                       (
                           """Change Request Form: 122 Design Action Notification: DAN/ 0007 Increase to the Guaranteed
                           Maximum Price: HK$ 250,000/ USD 32,052 12. Coat Check-in and Storage Location: First Floor,
                           Meeting Rooms A separate coat check-in and storage area is added adjacent to the Main Meeting
                           Rooms at the First Floor GL 20/ V-T. Change Request Form: 123 Design Action Notification:
                           DAN/ 0014 Increase to the Guaranteed Maximum Price: HK$ 50,000/ USD 6,410 13. Hotel
                           Registration Counter Location: Hotel Main Registration Counter Provision of additional
                           cooling fans to the Main Registration counter to meet cooling requirements of I.T Equipment.
                           Change Request Form: 125 Design Action Notification: DAN/ 0046 Increase to the Guaranteed
                           Maximum Price: HK$ 76,000/ USD 9,744 14. VIP Manager’s Office / pantry Location: Ground
                           Floor, VIP Area The private dining room to the VIP Casino is deleted and is replaced with a
                           VIP Manager’s Office, dry pantry and connecting corridor. Change Request Form: 126 Design
                           Action Notification: DAN/ 0019 Increase to the Guaranteed Maximum Price: HK$ 67,000/ USD
                           8,590""",
                           []),
                       ("""5,397,150""", []),
                       (
                           """Plaintiff O2 Micro International Limited and Defendants Monolithic Power Systems, Inc.
                           (MPS), Michael Hsing, Advanced Semiconductor Manufacturing Company, Ltd. (ASMC), ASUSTeK
                           Computer, Inc., and Compal Electronics, Inc. (collectively, Defendants) dispute the meaning
                           of terms and phrases used in 02 Micro’s U.S. Patent No. 6,259,615 (the ‘615 patent), its
                           U.S. Patent No. 6,396,722 (the ‘722 patent) and its U.S. Patent No. 6,804,129 (the ‘129
                           patent) .1 02 Micro requests that the Court adopts the claim constructions previously
                           adopted by this Court and by the Eastern District of Texas court. Defendants ask the Court
                           to adopt their proposed construction of two disputed phrases. In addition, O2 Micro moves
                           for summary judgment based on collateral estoppel. Defendants oppose the motion and
                           cross-move for summary judgment. O2 Micro opposes their motion for summary judgment. The
                           matters were heard on October 27, 2006. Having considered the parties’ papers, the evidence
                           cited therein and oral argument, the Court construes the disputed terms and phrases as set
                           forth below. In addition, the Court denies O2 Micro’s motion for summary judgment and grants
                           in part Defendants’ motion for summary judgment and denies it in part. BACKGROUND I. Patents
                           at issue The ‘615, ‘722 and ‘129 patents are all entitled: “High-Efficiency Adaptive DC/AC
                           Converter.” They are related to the same technology: the ‘129 patent is a continuation of
                           the ‘722""",
                           [datetime.date(2006, 10, 27)]),
                       ("""6,396,722 (the ‘722 patent) and its U.S. Patent No.""", []),
                       (
                           """Japanese Restaurant Noodles Restaurant Italian Restaurant Change Request Form: 130 Design
                           Action Notification: DAN/ 008 Increase to the Guaranteed Maximum Price: HK$ 75,075/ USD
                           9,625 17. Refrigerated wine cabinets Location: First Floor, Italian Restaurant Refrigerated
                           wine coolers (4nr) are included at the Italian Restaurant. These are to be housed in millwork
                           at the back of the drinks bar.""",
                           []),
                       (
                           """DIVISION 10 DIVISION 10 - SPECIALTIES 10000 Allowance to Install Owner Supplied Huddled
                           Area Safety Items 3,000 10100 Markerboards 119,000 10160 Metal Toilet Compartments 45,000
                           10500 Metal Lockers w/10160 10520 Fire Extinguishers and Cabinets 6,000 10810 Toilet
                           Accessories w/10160 10950 Building Specialties - Corner Guards Allowance 41,000 DIVISION 11
                           DIVISION 11 - EQUIPMENT 11130 Projection Screens w/10100 11160 Loading Dock Equipment NIC by
                           Base Bldg. 11400 Food Service Equipment 838,000 11601 Laboratory Fume Hoods w/12345 11604
                           Laboratory Fittings w/12345 11605 Laboratory Equipment Install Allowance 78,000 DIVISION 12
                           DIVISION 12 - FURNISHINGS 12345 Laboratory Casework 2,860,000 12514 Vertical Blinds 12515
                           Roller Shades 110,000 12670 Entrance Mats 2,000 12710 Fixed Seating 70,000 DIVISION 13
                           DIVISION 13 - SPECIAL CONSTRUCTION 13038 Controlled Temp Rooms 145,000 DIVISION 14 DIVISION
                           14 - VERTICAL TRANSPORTATION 14100 Elevators 690,000 14200 Geared Elevators w/14100 14400
                           Handicap Lift 18,000 DIVISION 15 DIVISION 15 - MECHANICAL 15300 Fire Protection 698,000 15420
                           Plumbing 3,150,000 15600 HVAC 9,773,000 AHU Pre-Purchase 1,438,000 15900 Building Control
                           System 1,169,000 DIVISION 16 DIVISION 16 - ELECTRICAL 16100 Electrical 7,025,000 16500
                           Archetechural Lighting Fixtures w/16100 16700 Tele / Data 839,000 18000 Commissioning
                           w/trades ================= =============================================================
                           ================== =================""",
                           []),
                       (
                           """As of March 15, 2016 Premier Pacific Construction, Inc. had 5,169,000 shares of common
                           stock outstanding.""",
                           [datetime.date(2016, 3, 15)]),
                       (
                           """2.13 EQUITY. In addition to the Required Equity Funds, Borrower has used the following
                           sums for construction purposes at the following Projects and such sums shall not be
                           reimbursed from the proceeds of the Loan: Aversana $13,144,901.00 Savona 8,681,981.00
                           Grande Isle I & II 7,073,050.00""",
                           []),
                       (
                           """1. The comprehensive fixed, unilateral construction price for this project is RMB
                           ￥500/m² turkey (including the safety construction fee, and ￥20/m² of unforeseeable fee).
                           The Contract Price is tentatively set at RMB ￥36,810,000 (in words: Thirty Six Million and
                           Eight Hundred and Ten Thousand yuan).  Regardless of any reason, the price shall not be
                           adjusted. The construction area is subject to the Housing Authority’s mapping data at the
                           time of payment.""",
                           []),
                       (
                           """The Contract Price is tentatively set at RMB ￥36,810,000 (in words: Thirty Six Million
                           and Eight Hundred and Ten Thousand yuan).""",
                           []),
                       (
                           """The Contract Price is USD 70,016,819.- (Seventy Million, Sixteen Thousand, Eight Hundred
                           and Nineteen).""",
                           []),
                       (
                           """Contract Price: The contract price of the DRILLSHIP, including the drilling equipment
                           package and the subsea equipment package, is United States Dollars Five Hundred Fifty Seven
                           Million (USD 557,000,000.00) plus or minus the amount, if any, set forth in subclause 3,
                           below (the “CONTRACT PRICE”), inclusive of the PC SUM, net receivable by BUILDER, which is
                           exclusive of BUYER’S SUPPLIES.""",
                           []),
                       (
                           """59. Increase 5no. of doors’ width Location: First Floor, Service Lift Lobby The opening
                           width of 5 nr doors within the service lift lobby is increased to allow easier access for
                           housekeeping service cart. Change Request Form: 192 Design Action Notification: DAN/ 0053
                           Increase to the Guaranteed Maximum Price: Nil 60. Upgrade Lift Lobby finishes Location:
                           Multi-storey Car Park The lift and lift lobby interior finishes at the car park are upgraded
                           from a “back of house” to a “front of house” standard and air conditioning is introduced to
                           the lobbies. Change Request Form: 194 Design Action Notification: DAN/ 0060 Increase to the
                           Guaranteed Maximum Price: HK$ 800,000/ USD 102,565 61. Revised layout of Staff Entrance
                           Location: Podium External Entry The internal layout at the Staff Entry is revised to
                           incorporate a separate entry to the recruitment office with access/ egress control by
                           automatic turnstiles. Change Request Form: 196 Design Action Notification: DAN/ 0068 Increase
                           to the Guaranteed Maximum Price: Nil 62. Marquee Sign foundation Location: North West Corner
                           of Site The reinforced concrete foundation for the Wynn Marquee sign is added to the
                           Contractor’s scope of work. Change Request Form: 197 Design Action Notification: DAN/ 0061
                           Increase to the Guaranteed Maximum Price: HK$ 8,000,000/ USD 1,025,641""",
                           []),
                       (
                           """Current liabilities Current maturities of long-term debt $ 745 $ 1,130 Accounts payable
                           100,816 90,111 Billings in excess of costs and estimated earnings 87,149 57,412 Accrued
                           expenses and other current liabilities 81,311 82,924 Total current liabilities
                           270,021 231,577 Long-term debt 138,364 63,891 Other long-term liabilities 9,607 6,370
                           Deferred income taxes 31,540 31,540 Commitments and contingencies Stockholders' equity
                           Preferred stock, $0.01 par value, authorized 3,000,000 shares, none outstanding -- -- Common
                           stock, $0.01 par value, authorized 100,000,000 shares; issued and outstanding 41,107,224
                           shares in 2001 and 40,881,908 in 2000 411 409 Additional paid-in capital 61,421 56,381
                           Retained earnings 338,066 330,172 Accumulated other comprehensive loss (112) --
                           399,786 386,962 Unearned compensation (13,818) (9,198) 385,968 377,764 $ 835,500 $ 711,142
                           ========= ========= </TABLE>""",
                           []),
                       (
                           """Tenant Improvements/Vanilla (559,150) (356,250) (198,400) (32,000) (1,922,139) (1,928,150)
                           6,011 Leasing Commissions (26,348) (55,250) (45,435) (54,500) (301,065) (394,900) 93,835
                           Renovation and Replacements 0 0 0 0 (218,536) (200,000) (18,536) TOTAL CAPITAL (585,498)
                           (411,500) (243,835) (86,500) (2,441,740) 2,523,050 81,310""",
                           []),
                       (
                           """Power and data for additional ATMs Location: Podium Areas Power and data provisions are
                           included for additional ATMs at the following locations: Chinese Restaurant – 1nr Food Court
                           – 1nr Retail Promenade – 2nr Staff Dining – 2nr Change Request Form: 133 Design Action
                           Notification: DAN/ 0015 Increase to the Guaranteed Maximum Price: HK$ 30,000/ USD 3,831
                           19.""",
                           []),
                       (
                           """Revised MCA OCIP Deduction 26,236,418 Mutually Agreed Upon Credit Adjustments
                           (2,000,000	)""",
                           []),
                       (
                           """percent (66 2/3%) of the outstanding principal balance of the Loan held by Non-Defaulting
                           Lenders.""",
                           []),
                       (
                           """REQUIRED LENDERS. As of any date of determination prior to termination of the Commitments,
                           Lenders (excluding Defaulting Lenders) whose aggregate Loan Percentages constitute at least
                           sixty-six and two-thirds percent (66 2/3%) of the Commitments held by Non-Defaulting Lenders.
                           As of any date of determination occurring after the termination of the Commitments, Lenders
                           (excluding Defaulting Lenders) holding at least sixty-six and two-thirds percent (66 2/3%)
                           of the outstanding principal balance of the Loan held by Non-Defaulting Lenders.""",
                           []),
                       ("""19.1 Procedure 1-61 19.2 Assessment 1-62""", []),
                       (
                           """2.1.1, 3.3.3, 3.12.4, 3.12.8, 3.12.10, 4.1.2, 4.2.1, 4.2.2, 4.2.3, 4.2.6, 4.2.7, 4.2.10,
                           4,2.12, 4.2.13, 4.4, 5.2.1, 7.4, 9.4.2, 9.6.4, 9.6.6""",
                           []),
                       (
                           """All notices, consents, requests and other communications hereunder shall be in writing and
                           shall be deemed to have been duly given when (a) delivered by hand, (b) sent by telecopier
                           (with receipt confirmed), provided that a copy is sent in the manner provided in clause (c),
                           or (c) when received by the addressee, if sent by DHL, Federal Express, Airborne Express or
                           other generally recognized international express delivery service (receipt requested), in
                           each case to the appropriate addresses and telecopier numbers set forth below (or to such
                           other addresses and telecopier numbers as a party may designate as to itself by notice to the
                           other parties): (i) If to CCKK: SoftBank Corp. 3-42-3 Nihonbashi-Hamacho Chuo-ku Tokyo 103
                           Japan Telecopier No.""",
                           []),
                       ("""4.2.2, 4.2.9, 4.3,4, 9.4.2, 9.8.3, 9.9.2, 9.10.1, 13.5""", []),
                       ("""In the event the real estate taxes levied or assessed against the land
                       and building of which the premises are a part in future tax years are
                       greater than the real estate taxes for the base tax year, the TENANT,
                       shall pay within thirty (30) days after submission of the bill to TENANT for the increase in
                       real estate taxes, as additional rent a proportionate share of such
                       increases, which proportionate share shall be computed at 22.08% of the
                       increase in taxes, but shall exclude any fine, penalty, or interest
                       charge for late or non-payment of taxes by LANDLORD. The base tax year
                       shall be July 1, 1994 to June 30, 1995.""",
                        [datetime.date(1994, 7, 1), datetime.date(1995, 6, 30)]),
                       ("""THIS FIRST AMENDMENT TO EMPLOYMENT AGREEMENT (“Amendment”) is entered into by and among
Cardtronics, LP, a Delaware limited partnership (the “Company”), Cardtronics, Inc. (the “Parent
Company”) and Rick Updyke (the “Employee”) effective as of June 20, 2008.""",
                        [datetime.date(2008, 6, 20)]),
                       ("""""", [])]

EXAMPLE_FIXED_DATES_NONSTRICT = [("""The term of this lease shall
be for a period of five years, commencing
on the 1st day of April, 1995, and terminating on the 31st day of
March,
2000 with an option for an additional five years at the same terms and
conditions in this lease, provided that TENANT shall have given the
LANDLORD written notice of TENANT’s intention to do so six (6) months prior
to the expiration of this lease and that the Tenant is not in default
of the Lease.""",
                                  [datetime.date(1995, 4, 1),
                                   datetime.date(2000, 3, 31)]),
                                 ("""t may """, []),
                                 (""" Lockheed Martin Corporation """, []),
                                 (""" he Decided to make a break """, []),
                                 ]


def test_fixed_raw_dates():
    """
    Test raw date extraction from fixed examples.
    :return:
    """
    # Check all examples
    i = 0
    for example in EXAMPLE_FIXED_RAW_DATES:
        print("Example {i}: {t}...".format(
            i=i, t=example[0][0:min(20, len(example[0]))]))
        assert_set_equal(set(get_raw_dates(example[0])), set(example[1]))
        i += 1


def test_fixed_dates():
    """
    Test date extraction from fixed examples.
    :return:
    """
    # Check all examples
    i = 0
    for example in EXAMPLE_FIXED_DATES:
        print("Example {i}: {t}...".format(
            i=i, t=example[0][0:min(20, len(example[0]))]))
        dates = get_dates(example[0])
        assert_set_equal(set(dates), set(example[1]))
        i += 1


def test_fixed_dates_nonstrict():
    """
    Test date extraction from fixed examples.
    :return:
    """
    # Check all examples
    i = 0
    for example in EXAMPLE_FIXED_DATES_NONSTRICT:
        print("Example {i}: {t}...".format(
            i=i, t=example[0][0:min(20, len(example[0]))]))
        assert_set_equal(set(get_dates(example[0], strict=False)), set(example[1]))
        i += 1


def test_date_may():
    """
    Test that " may " alone does not parse.
    :return:
    """
    # Ensure that no value is returned for either strict or non-strict mode
    nonstrict_result = get_dates("this may be a date", strict=False, return_source=True)
    strict_result = get_dates("this may be a date", strict=True, return_source=True)
    assert_equal(len(nonstrict_result), 0)
    assert_equal(len(strict_result), 0)


def test_fixed_dates_source():
    """
    Test date extraction from fixed examples with source.
    :return:
    """
    # Check all examples
    i = 0
    for example in EXAMPLE_FIXED_DATES:
        print("Example {i}: {t}...".format(
            i=i, t=example[0][0:min(20, len(example[0]))]))
        # TODO: Improve checking source strings.
        dates = [d[0] for d in get_dates(example[0], return_source=True)]
        assert_set_equal(set(dates), set(example[1]))
        i += 1


def test_random_dates():
    """
    Test date extraction with random dates.
    :return:
    """
    # Check random examples
    n = 10

    # Iterate through all date range
    for _ in range(n):
        # Setup date
        year = random.randint(1980, 2020)
        month = random.randint(1, 13)
        day = random.randint(1, 32)

        try:
            date = datetime.date(year, month, day)
        except ValueError:
            continue

        # Try three versions
        text = """on {0}-{1}-{2}""".format(year, month, day)
        assert_list_equal(get_dates(text), [date])

        text = "by " + date.strftime("%b %d, %Y")
        assert_list_equal(get_dates(text), [date])

        text = "before " + date.strftime("%B %d, %Y")
        assert_list_equal(get_dates(text), [date])


def test_date_feature_1():
    """
    Test date feature engineering.
    :return:
    """
    date_feature = get_date_features("2000-02-02", 0, 10, include_bigrams=False, characters=string.printable)
    assert_dict_equal(date_feature,
                      {'char_T': 0.0, 'char_L': 0.0, 'char_?': 0.0, 'char_`': 0.0, 'char_B': 0.0, 'char_]': 0.0,
                       'char_Z': 0.0,
                       'char_&': 0.0, 'char_-': 0.2, 'char_/': 0.0, 'char_8': 0.0, 'char_c': 0.0, 'char_A': 0.0,
                       'char__': 0.0,
                       'char_I': 0.0, 'char_9': 0.0, 'char_V': 0.0, 'char_7': 0.0, 'char_b': 0.0, 'char_g': 0.0,
                       'char_!': 0.0,
                       'char_Q': 0.0, 'char_*': 0.0, 'char_{': 0.0, 'char_G': 0.0, 'char_.': 0.0, 'char_U': 0.0,
                       'char_\r': 0.0,
                       'char_:': 0.0, 'char_,': 0.0, 'char_\\': 0.0, 'char_$': 0.0, 'char_C': 0.0, 'char_\x0b': 0.0,
                       'char_S': 0.0,
                       'char_r': 0.0, 'char_J': 0.0, 'char_i': 0.0, 'char_1': 0.0, 'char_^': 0.0, 'char_l': 0.0,
                       'char_v': 0.0,
                       'char_m': 0.0, 'char_o': 0.0, 'char_h': 0.0, 'char_@': 0.0, 'char_\t': 0.0, 'char_M': 0.0,
                       'char_x': 0.0,
                       'char_2': 0.3, 'char_5': 0.0, 'char_"': 0.0, 'char_0': 0.5, 'char_q': 0.0, 'char_K': 0.0,
                       'char_R': 0.0,
                       'char_n': 0.0, 'char_4': 0.0, 'char_H': 0.0, 'char_p': 0.0, 'char_+': 0.0, 'char_O': 0.0,
                       'char_D': 0.0,
                       'char_)': 0.0, 'char_Y': 0.0, 'char_E': 0.0, 'char_<': 0.0, "char_'": 0.0, 'char_f': 0.0,
                       'char_t': 0.0,
                       'char_e': 0.0, 'char_W': 0.0, 'char_;': 0.0, 'char_s': 0.0, 'char_3': 0.0, 'char_}': 0.0,
                       'char_%': 0.0,
                       'char_P': 0.0, 'char_z': 0.0, 'char_N': 0.0, 'char_w': 0.0, 'char_\n': 0.0, 'char_d': 0.0,
                       'char_#': 0.0,
                       'char_u': 0.0, 'char_~': 0.0, 'char_>': 0.0, 'char_=': 0.0, 'char_k': 0.0, 'char_F': 0.0,
                       'char_ ': 0.0,
                       'char_\x0c': 0.0, 'char_|': 0.0, 'char_y': 0.0, 'char_(': 0.0, 'char_X': 0.0, 'char_[': 0.0,
                       'char_a': 0.0,
                       'char_j': 0.0, 'char_6': 0.0})


def test_date_feature_1_bigram():
    """
    Test date feature engineering with bigrams.
    :return:
    """
    date_feature = get_date_features(
        "2000-02-02", 0, 10, include_bigrams=True, characters=string.digits)
    assert_dict_equal(date_feature,
                      {'bigram_02': 0.6666666666666666, 'bigram_06': 0.0, 'bigram_05': 0.0, 'bigram_58': 0.0,
                       'bigram_41': 0.0, 'bigram_13': 0.0, 'bigram_95': 0.0, 'bigram_37': 0.0, 'bigram_25': 0.0,
                       'bigram_92': 0.0, 'bigram_20': 0.3333333333333333, 'bigram_71': 0.0, 'bigram_29': 0.0,
                       'bigram_52': 0.0, 'bigram_67': 0.0, 'bigram_96': 0.0, 'bigram_64': 0.0, 'char_5': 0.0,
                       'bigram_27': 0.0, 'bigram_72': 0.0, 'bigram_80': 0.0, 'bigram_86': 0.0, 'bigram_12': 0.0,
                       'bigram_23': 0.0, 'bigram_38': 0.0, 'bigram_78': 0.0, 'bigram_14': 0.0, 'bigram_32': 0.0,
                       'bigram_45': 0.0, 'bigram_03': 0.0, 'bigram_83': 0.0, 'bigram_54': 0.0, 'char_1': 0.0,
                       'bigram_28': 0.0, 'bigram_69': 0.0, 'bigram_35': 0.0, 'bigram_85': 0.0, 'bigram_68': 0.0,
                       'bigram_51': 0.0, 'bigram_26': 0.0, 'bigram_47': 0.0, 'bigram_46': 0.0, 'char_2': 0.375,
                       'bigram_43': 0.0, 'bigram_48': 0.0, 'bigram_90': 0.0, 'char_0': 0.625, 'bigram_50': 0.0,
                       'bigram_56': 0.0, 'bigram_62': 0.0, 'char_4': 0.0, 'bigram_34': 0.0, 'bigram_70': 0.0,
                       'bigram_73': 0.0, 'bigram_15': 0.0, 'bigram_07': 0.0, 'bigram_30': 0.0, 'bigram_63': 0.0,
                       'bigram_74': 0.0, 'bigram_36': 0.0, 'bigram_19': 0.0, 'bigram_42': 0.0, 'bigram_53': 0.0,
                       'bigram_89': 0.0, 'bigram_40': 0.0, 'bigram_87': 0.0, 'bigram_01': 0.0, 'bigram_60': 0.0,
                       'bigram_76': 0.0, 'bigram_18': 0.0, 'bigram_09': 0.0, 'bigram_16': 0.0, 'bigram_24': 0.0,
                       'char_3': 0.0, 'bigram_10': 0.0, 'bigram_17': 0.0, 'bigram_65': 0.0, 'bigram_31': 0.0,
                       'bigram_93': 0.0, 'bigram_59': 0.0, 'bigram_91': 0.0, 'bigram_61': 0.0, 'bigram_82': 0.0,
                       'char_8': 0.0, 'char_9': 0.0, 'bigram_39': 0.0, 'bigram_49': 0.0, 'bigram_81': 0.0,
                       'bigram_97': 0.0, 'bigram_75': 0.0, 'bigram_84': 0.0, 'bigram_08': 0.0, 'bigram_98': 0.0,
                       'bigram_79': 0.0, 'bigram_21': 0.0, 'bigram_04': 0.0, 'char_7': 0.0, 'bigram_57': 0.0,
                       'char_6': 0.0, 'bigram_94': 0.0})


def test_build_model():
    """
    Test build model by running default train.
    :return:
    """
    train_default_model(save=False)
