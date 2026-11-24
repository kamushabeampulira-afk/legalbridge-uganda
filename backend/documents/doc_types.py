"""
Document type taxonomy shared by the Document model, the classifier and
legal retrieval. Each type maps to a group (for display/analytics) and to the
legal subjects searched in the verified knowledge base.

Codes that existed before this taxonomy (traffic_notice, police_charge,
court_summons, eviction_notice, allocation_slip, payment_receipt, rent_record,
market_notice, employment_letter, contract, other_official, unknown) are kept
so existing records stay valid.
"""

# code, label, group, legal subjects to search (most specific first)
DOC_TYPES = [
    # ── Traffic ──────────────────────────────────────────────────────────────
    ('traffic_notice', 'Traffic offence / violation notice', 'traffic', ['traffic', 'police']),
    ('traffic_penalty_ticket', 'Traffic ticket / express penalty notice', 'traffic', ['traffic']),
    ('traffic_summons', 'Traffic summons / notice to appear', 'traffic', ['traffic', 'criminal_procedure']),
    ('vehicle_inspection_notice', 'Vehicle inspection notice', 'traffic', ['traffic']),
    ('vehicle_impoundment_notice', 'Vehicle impoundment / seizure notice', 'traffic', ['traffic', 'police']),
    # ── Police-issued correspondence ─────────────────────────────────────────
    ('police_letter', 'Letter from the Uganda Police Force', 'police_correspondence', ['police']),
    ('police_summons', 'Police summons / request to report to a police station', 'police_correspondence',
     ['police', 'criminal_procedure']),
    ('police_notice', 'Police notice', 'police_correspondence', ['police']),
    ('police_info_request', 'Police request for information', 'police_correspondence', ['police']),
    ('police_complaint_ack', 'Police acknowledgement of a complaint or reported incident',
     'police_correspondence', ['police', 'criminal_procedure']),
    # ── Police complaints and case documents ─────────────────────────────────
    ('complaint_to_police', 'Complaint submitted to the police by a member of the public', 'police_case',
     ['police', 'criminal_procedure']),
    ('police_statement', 'Police statement / statement record', 'police_case', ['police', 'criminal_procedure']),
    ('police_case_document', 'Police case or investigation document', 'police_case',
     ['police', 'criminal_procedure']),
    ('police_bond', 'Police bond', 'police_case', ['police', 'criminal_procedure']),
    ('police_charge', 'Police charge sheet', 'police_case', ['criminal_procedure', 'police']),
    # ── Courts ───────────────────────────────────────────────────────────────
    ('court_summons', 'Court summons', 'court', ['criminal_procedure']),
    # ── Markets and trade ────────────────────────────────────────────────────
    ('allocation_slip', 'Market allocation letter / slip', 'market_trade', ['markets']),
    ('trading_licence', 'Trading licence / permit', 'market_trade', ['markets', 'local_gov']),
    ('payment_receipt', 'Payment receipt (e.g. market fees)', 'market_trade', ['markets']),
    ('market_notice', 'Market management notice', 'market_trade', ['markets']),
    ('trading_space_vacate_notice', 'Notice to vacate a trading space', 'market_trade', ['markets', 'local_gov']),
    # ── Property ─────────────────────────────────────────────────────────────
    ('eviction_notice', 'Eviction notice', 'property', ['land', 'markets']),
    ('landlord_correspondence', 'Landlord or market authority correspondence', 'property', ['land', 'markets']),
    # ── Local authorities ────────────────────────────────────────────────────
    ('local_authority_notice', 'Local authority notice', 'local_authority', ['local_gov']),
    # ── Agreements, payments, employment ─────────────────────────────────────
    ('contract', 'Agreement / contract', 'agreements_payments', ['general']),
    ('rent_record', 'Rent or payment record', 'agreements_payments', ['land', 'markets']),
    ('employment_letter', 'Employment letter', 'employment', ['employment']),
    # ── Fallbacks ────────────────────────────────────────────────────────────
    ('other_official', 'Other document affecting rights or obligations', 'other', ['general']),
    ('unknown', 'Unknown / unsupported document', 'other', []),
]

DOC_TYPE_CHOICES = [(code, label) for code, label, _group, _subjects in DOC_TYPES]
DOC_TYPE_LABELS = {code: label for code, label, _group, _subjects in DOC_TYPES}
DOC_TYPE_GROUPS = {code: group for code, _label, group, _subjects in DOC_TYPES}
DOC_TYPE_SUBJECTS = {code: subjects for code, _label, _group, subjects in DOC_TYPES}

POLICE_GROUPS = {'police_correspondence', 'police_case'}


def legal_subjects_for(doc_type):
    """Subjects to search for a document type. 'general' is always included."""
    subjects = list(DOC_TYPE_SUBJECTS.get(doc_type, []))
    if 'general' not in subjects:
        subjects.append('general')
    return subjects
