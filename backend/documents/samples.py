"""
Synthetic sample documents used by the classification diagnostic and tests.

All names, stations, reference numbers and amounts are fictional ("Sample
Police Station", "Example Town Council"). They exist only to check that the
classifier recognises each document type; they are never shown to users as
real documents or legal information.
"""

SAMPLE_DOCUMENTS = [
    ('traffic_notice', """UGANDA POLICE FORCE
DIRECTORATE OF TRAFFIC AND ROAD SAFETY
TRAFFIC OFFENCE NOTICE
Ref No: TON/0000/2026
Date: 03/02/2026
Name of rider: John Example
Motorcycle registration no: UXX 000X
Alleged offence: Riding without a helmet
Officer: No. 00000 PC Sample
"""),
    ('traffic_penalty_ticket', """EXPRESS PENALTY SCHEME (EPS)
Traffic ticket No. EPS/0000/2026
Vehicle reg. no: UXX 000X
Offence: Over speeding
Fine: UGX 000,000
Pay the fine within 28 days at any designated bank.
"""),
    ('traffic_summons', """SUMMONS TO APPEAR
In the Traffic Court at Sample Town
To: John Example, rider of motorcycle UXX 000X
You are summoned to appear before the court on 10/03/2026 at 9:00 am
to answer a charge of careless driving.
"""),
    ('vehicle_inspection_notice', """VEHICLE INSPECTION NOTICE
You are required to present your vehicle UXX 000X for mechanical inspection
at the Sample Inspection Centre on 12/03/2026.
Bring the certificate of fitness and registration documents.
"""),
    ('vehicle_impoundment_notice', """UGANDA POLICE FORCE
SAMPLE POLICE STATION
NOTICE OF IMPOUNDED MOTORCYCLE
Motorcycle UXX 000X has been impounded and is held at the station yard.
Release of the motorcycle requires the owner to report with the logbook.
"""),
    ('police_summons', """UGANDA POLICE FORCE
SAMPLE POLICE STATION
Ref: SPS/GEN/000/2026
Date: 04/02/2026
To: Mr. John Example
P.O. Box 000, Sample Town
RE: REQUEST TO REPORT
You are hereby required to report to Sample Police Station on 06/02/2026 at 10:00 am
to assist with inquiries. Bring your national identity card.
Officer in Charge
"""),
    ('police_complaint_ack', """UGANDA POLICE FORCE
SAMPLE POLICE STATION
Date: 05/02/2026
To: Ms. Jane Example
RE: ACKNOWLEDGEMENT OF COMPLAINT
This is to acknowledge receipt of your complaint dated 01/02/2026 regarding theft of goods.
Your complaint has been registered under SD Ref 00/00/02/2026.
Officer in Charge
"""),
    ('police_info_request', """UGANDA POLICE FORCE
SAMPLE POLICE STATION
Ref: SPS/CID/000/2026
To: The Manager, Example Market Vendors Association
RE: REQUEST FOR INFORMATION
You are hereby requested to provide the following records to assist the police investigation:
list of stall holders in block C for January 2026.
"""),
    ('complaint_to_police', """Jane Example
P.O. Box 000, Sample Town
01/02/2026
The Officer in Charge
Sample Police Station
Dear Sir,
RE: COMPLAINT ABOUT THEFT OF MY GOODS
I wish to report the theft of my goods from my stall at Example Market on the night of 30/01/2026.
I am the complainant and I request that this matter be investigated.
Yours faithfully,
Jane Example
"""),
    ('police_bond', """UGANDA POLICE FORCE
POLICE BOND
SAMPLE POLICE STATION
I, John Example, am released on police bond and undertake to report back to the station
on 15/02/2026. Surety: Peter Example.
CRB 000/2026
"""),
    ('police_statement', """UGANDA POLICE FORCE
STATEMENT OF WITNESS
Statement recorded by No. 00000 PC Sample at Sample Police Station
I, Mary Example, aged 30, a vendor at Example Market, state as follows ...
"""),
    ('police_case_document', """UGANDA POLICE FORCE
SAMPLE POLICE STATION
EXTRACT FROM THE STATION DIARY
SD Ref 00/00/02/2026
CRB 000/2026
Investigating officer: D/Sgt Sample
Case summary: report of a lost national identity card.
"""),
    ('allocation_slip', """EXAMPLE MARKET MANAGEMENT COMMITTEE
MARKET STALL ALLOCATION SLIP
This is to certify that Jane Example has been allocated stall number B-00
at Example Market with effect from 01/01/2026.
"""),
    ('trading_licence', """EXAMPLE TOWN COUNCIL
TRADING LICENCE
Licence No: TL/000/2026
Jane Example is licensed to trade in general merchandise at Example Market.
Valid until 31/12/2026.
"""),
    ('payment_receipt', """EXAMPLE MARKET
OFFICIAL RECEIPT
Receipt No. 000000
Received from: Jane Example
Amount paid: UGX 00,000 being market dues for February 2026.
"""),
    ('trading_space_vacate_notice', """EXAMPLE MARKET MANAGEMENT COMMITTEE
NOTICE TO VACATE
To: Jane Example, Stall B-00
You are hereby required to vacate the market stall within 14 days to allow for renovation.
"""),
    ('eviction_notice', """NOTICE TO QUIT
To: John Example, tenant of Room 0, Example Plot
Take notice that you are required to vacate the premises within 30 days
due to rent arrears. Signed: The Landlord
"""),
    ('local_authority_notice', """EXAMPLE TOWN COUNCIL
PUBLIC NOTICE
Notice is hereby given to all traders that enforcement of the trading by-law
on street vending will begin on 01/03/2026.
Town Clerk
"""),
    ('unknown', """Shopping list: sugar, bread, tea leaves, soap.
Remember to call mum on Sunday."""),
]
