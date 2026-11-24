"""
LegalBridge: document classification.

Rule-based and deterministic, so it works without an AI provider and every
decision can be explained: each result lists the phrases that triggered it.

Steps:
1. Find who issued the document (letterhead/sender), ignoring the "To:" block,
   so a complaint addressed TO a police station is not mistaken for a police letter.
2. Decide whether it was issued by an institution or written by a member of the public.
3. Score every document type on weighted phrases, then adjust using issuer and origin.
4. Return 'unknown' when no type scores clearly, instead of forcing a category.
"""
from __future__ import annotations

import re

from .doc_types import DOC_TYPE_GROUPS, DOC_TYPE_LABELS, POLICE_GROUPS

MIN_SCORE = 4          # below this, the document is not confidently any type
AMBIGUITY_MARGIN = 1   # top two types closer than this (and both weak) -> unknown

# ── Issuers ─────────────────────────────────────────────────────────────────
ISSUER_PATTERNS = [
    ('police', r'uganda police(?: force)?|\bpolice (?:station|post|division|headquarters|hqs?)\b|'
               r'directorate of traffic|traffic (?:and road safety )?police|'
               r'\bdistrict police commander\b|\bcriminal investigations? (?:directorate|department)\b|'
               r'\bcentral police station\b|\bofficer in charge\b|\bo/c\b'),
    ('court', r"magistrate'?s? court|\bhigh court\b|\bchief magistrate\b|court of judicature"),
    ('local_authority', r'kampala capital city authority|\bkcca\b|'
                        r'\b(?:municipal|town|city|district|sub-?county|division) council\b|'
                        r'district local government|\btown clerk\b|\bcity clerk\b'),
    ('market_authority', r'market (?:management|master|manager|administration|committee|authority)|'
                         r'market vendors?.? association'),
    ('government_agency', r'\bministry of\b|uganda revenue authority'),
    ('landlord', r'\blandlord\b|\blessor\b|property manage(?:r|ment)'),
]

ADDRESSEE_START = re.compile(
    r'^\s*(?:to\b\s*[:,-]?|the\s+(?:officer\s+in\s+charge|o/c\b|district\s+police\s+commander|dpc\b|'
    r'town\s+clerk|market\s+master|landlord))',
    re.IGNORECASE,
)

# ── Origin signals ──────────────────────────────────────────────────────────
PUBLIC_SUBMISSION_PATTERNS = [
    r'\bi (?:wish|want|would like) to (?:report|complain|lodge)',
    r'\bi am writing to (?:report|complain|lodge|inform)',
    r'\blodge (?:a|my) complaint\b',
    r'\bmy complaint\b',
    r'\bi hereby (?:report|complain)',
    r'\bi,\s*[a-z]+(?:\s+[a-z]+)?,?\s+(?:of|a resident|resident)',
    r"\bcomplainant'?s? signature\b",
]
INSTITUTION_ISSUED_PATTERNS = [
    r'\byou are (?:hereby )?(?:required|summoned|directed|requested|instructed|notified|informed)',
    r'\bthis is to (?:inform|notify|acknowledge|certify|confirm)',
    r'\bwe (?:acknowledge|confirm) (?:receipt|that)',
    r'\byour complaint\b',
    r'\bfor:? inspector general\b',
    r'\bnotice is hereby given\b',
]

# ── Type rules: doc_type -> (weighted patterns, words of which at least one must appear) ──
TYPE_RULES: dict[str, tuple[list[tuple[str, int]], list[str] | None]] = {
    # Traffic
    'traffic_notice': ([
        (r'traffic (?:offence|violation|infringement) notice', 5),
        (r'notice of (?:traffic )?(?:offence|violation)', 4),
        (r'traffic (?:offence|violation)', 3),
        (r'alleged (?:traffic )?offence', 2),
        (r'over ?speeding|\bspeeding\b|careless driving|dangerous driving|reckless|without (?:a )?helmet', 2),
        (r'traffic (?:officer|police)', 2),
        (r'road safety', 1),
        (r'number plate|registration (?:no|number)|\breg\.? no', 1),
        (r'\bvehicle\b', 1),
        (r'motor ?cycle|\bboda\b', 1),
        (r'driving (?:permit|licen[cs]e)', 1),
    ], None),
    'traffic_penalty_ticket': ([
        (r'express penalty|\beps\b', 5),
        (r'fixed penalty', 4),
        (r'traffic ticket', 4),
        (r'penalty (?:ticket|notice)', 3),
        (r'pay (?:the )?(?:fine|penalty) within', 2),
        (r'\bfine\b', 1),
        (r'\bpenalty\b', 1),
    ], ['traffic', 'vehicle', 'motor', 'driving', 'road', 'boda', 'eps', 'express penalty']),
    'traffic_summons': ([
        (r'notice to appear', 4),
        (r'traffic court', 4),
        (r'\bsummons\b|\bsummoned\b', 3),
        (r'appear before', 3),
        (r'\bcourt\b', 1),
        (r'\bhearing\b', 1),
    ], ['traffic', 'vehicle', 'motor', 'driving', 'road safety', 'boda']),
    'vehicle_inspection_notice': ([
        (r'vehicle inspection', 5),
        (r'inspection (?:notice|certificate|cent(?:re|er))', 3),
        (r'certificate of fitness|roadworth', 3),
        (r'mechanical (?:inspection|condition)', 3),
        (r'present (?:the|your) (?:vehicle|motor ?cycle)', 3),
    ], None),
    'vehicle_impoundment_notice': ([
        (r'\bimpound(?:ed|ment)?\b', 5),
        (r'release of (?:the |your )?(?:vehicle|motor ?cycle)', 4),
        (r'(?:vehicle|motor ?cycle) (?:has been |was )?detained|detained (?:vehicle|motor ?cycle)', 4),
        (r'\bseiz(?:ed|ure)\b', 3),
        (r'\btowed\b|tow(?:ing)? (?:fee|charge)', 3),
        (r'\byard\b', 1),
    ], ['vehicle', 'motor', 'boda', 'car', 'taxi']),
    # Police-issued correspondence
    'police_summons': ([
        (r'police summons', 6),
        (r'you are (?:hereby )?(?:summoned|required|requested|directed) to (?:report|appear)', 6),
        (r'report to (?:the )?[\w\s]{0,40}police (?:station|post)', 4),
        (r'\bsummons\b|\bsummoned\b', 2),
        (r'to report (?:at|to)\b', 2),
    ], None),
    'police_complaint_ack': ([
        (r'acknowledg(?:e|ement|ing) (?:the )?(?:receipt )?(?:of )?(?:your )?(?:complaint|report)', 6),
        (r'your (?:complaint|report) (?:has been|was) (?:received|registered|recorded)', 6),
        (r'(?:case|complaint) (?:has been )?registered (?:under|as)', 3),
        (r'reported (?:an |the )?incident', 2),
        (r'\bs\.?d\.? ?(?:ref|no)', 2),
        (r'\bcrb\b', 2),
    ], None),
    'police_info_request': ([
        (r'you are (?:hereby )?requested to (?:provide|furnish|submit|avail)', 6),
        (r'furnish (?:this office|us|the police) with', 5),
        (r'request(?:ing)? (?:for )?(?:information|documents|records)', 4),
        (r'provide the following', 3),
        (r'assist (?:the )?(?:police|investigation)', 2),
    ], None),
    'police_notice': ([
        (r'police notice', 5),
        (r'notice is hereby given', 3),
        (r'public notice', 3),
        (r'general public', 2),
    ], None),
    'police_letter': ([
        (r'uganda police', 2),
        (r'police (?:station|post|headquarters)', 1),
        (r'\bdear (?:sir|madam|mr|mrs|ms)\b', 1),
        (r'\bre\s*:', 1),
        (r'yours (?:faithfully|sincerely)', 1),
    ], None),
    # Police complaints and case documents
    'complaint_to_police': ([
        (r'\bi (?:wish|want|would like) to (?:report|complain|lodge)', 6),
        (r'\bi am writing to (?:report|complain|lodge)', 6),
        (r'lodge (?:a|my) complaint', 5),
        (r'\bmy complaint\b', 3),
        (r'\bcomplainant\b', 2),
        (r'officer in charge|\bo/c\b|district police commander', 1),
    ], None),
    'police_statement': ([
        (r'statement of (?:witness|complainant|suspect|accused)', 6),
        (r'witness statement', 6),
        (r'charge and caution|caution statement', 6),
        (r'statement (?:recorded|taken|made) (?:by|before|at)', 5),
        (r'police form', 2),
        (r'\bstatement\b', 1),
    ], None),
    'police_bond': ([
        (r'police bond', 8),
        (r'released on (?:police )?bond', 6),
        (r'bond (?:form|conditions)', 4),
        (r'\bsuret(?:y|ies)\b', 3),
        (r'report back (?:to the station|on)', 2),
    ], None),
    'police_case_document': ([
        (r'extract (?:from|of) (?:the )?(?:occurrence book|station diary|crime register)', 6),
        (r'investigating officer', 4),
        (r'case summary', 4),
        (r'\bcrb ?(?:no\.?|number)?\s*\d', 4),
        (r'occurrence book|station diary', 4),
        (r'case (?:file|ref(?:erence)?|no\.?|number)', 3),
        (r'\bs\.?d\.? ?(?:ref|no)', 3),
        (r'police file', 3),
        (r'\binvestigation', 2),
    ], None),
    'police_charge': ([
        (r'charge sheet', 8),
        (r'statement of offence', 4),
        (r'particulars of offence', 4),
        (r'charged with', 3),
        (r'\baccused\b', 2),
    ], None),
    # Courts
    'court_summons': ([
        (r'criminal case no|civil suit no|miscellaneous application', 4),
        (r'appear before (?:the )?(?:court|magistrate|judge)', 4),
        (r'\bsummons\b|\bsummoned\b', 3),
        (r'\bmagistrate', 3),
        (r'hearing date', 3),
        (r'\bcourt\b', 2),
    ], None),
    # Markets and trade
    'allocation_slip': ([
        (r'allocation (?:slip|letter|form)', 6),
        (r'hereby allocated', 4),
        (r'\ballocat(?:ed|ion)\b', 3),
        (r'\ballot(?:ted|ment)\b', 3),
        (r'stall (?:no|number)', 2),
        (r'trading space', 2),
        (r'\bstall\b|lock-?up|\bkiosk\b|table space', 1),
    ], None),
    'trading_licence': ([
        (r'trading licen[cs]e', 7),
        (r'business licen[cs]e', 6),
        (r'trading permit|vending permit|hawker\w*.{0,10}(?:licen[cs]e|permit)', 6),
        (r'licensed to', 3),
        (r'licen[cs]e (?:no|number|fee)', 2),
        (r'valid (?:until|up to|from)', 2),
        (r'\bpermit\b', 1),
    ], None),
    'payment_receipt': ([
        (r'official receipt', 4),
        (r'\breceipt\b', 3),
        (r'payment received|received (?:with thanks )?from', 3),
        (r'amount paid|\bpaid\b', 2),
        (r'market (?:fees|dues|levy)', 2),
        (r'\bcash\b|mobile money', 1),
    ], None),
    'market_notice': ([
        (r'notice to (?:all )?(?:market )?vendors', 5),
        (r'market (?:management|administration|master|manager|committee)', 3),
        (r'all (?:market )?vendors', 3),
        (r'market (?:dues|fees|rules|regulations)', 2),
        (r'\bnotice\b', 1),
    ], None),
    'trading_space_vacate_notice': ([
        (r'vacate (?:the |your )?(?:market )?(?:stall|trading space|lock-?up|kiosk|space|table)', 6),
        (r'clear (?:your|the) (?:stall|space|kiosk)', 4),
        (r'notice to vacate', 4),
        (r'\bvacate\b', 2),
        (r'relocat(?:e|ion)', 2),
    ], ['stall', 'trading space', 'lock-up', 'lockup', 'kiosk', 'market', 'table space', 'vending']),
    # Property
    'eviction_notice': ([
        (r'eviction notice|notice of eviction', 7),
        (r'notice to quit', 6),
        (r'vacate (?:the )?(?:premises|house|room|land|property|plot)', 5),
        (r'\bevict(?:ed|ion)?\b', 4),
        (r'\btenan(?:t|cy)\b', 2),
        (r'rent arrears', 2),
        (r'\blandlord\b', 1),
        (r'\bvacate\b', 1),
    ], None),
    'landlord_correspondence': ([
        (r'\bdear tenant\b', 5),
        (r'rent (?:increase|review|arrears|is due)', 3),
        (r'\blandlord\b', 3),
        (r'\blessor\b|\blessee\b', 3),
        (r'tenancy agreement', 2),
        (r'\bpremises\b', 1),
    ], None),
    # Local authorities
    'local_authority_notice': ([
        (r'kampala capital city authority|\bkcca\b', 3),
        (r'\b(?:municipal|town|city|division|district) council\b', 3),
        (r'town clerk|city clerk|chief administrative officer', 3),
        (r'by-?law|ordinance', 3),
        (r'local government', 2),
        (r'public notice', 2),
        (r'notice is hereby given', 2),
        (r'\benforcement\b', 1),
    ], None),
    # Agreements, payments, employment
    'contract': ([
        (r'this agreement|agreement (?:is )?(?:made|entered)', 5),
        (r'in witness whereof|witnessed by', 3),
        (r'\bagreement\b', 3),
        (r'\bcontract\b', 3),
        (r'\bparties\b', 2),
        (r'terms and conditions', 2),
    ], None),
    'rent_record': ([
        (r'rent (?:card|book|record|payment record)', 6),
        (r'payment (?:record|schedule|history)', 4),
        (r'rent paid|monthly rent', 3),
        (r'balance (?:due|brought forward|b/f)', 3),
        (r'instal?lment', 2),
    ], None),
    'employment_letter': ([
        (r'appointment letter|letter of appointment|employment (?:letter|contract)', 6),
        (r'termination|dismissal', 3),
        (r'\bemploy(?:ed|ment|er|ee)\b', 2),
        (r'\bsalary\b|\bwages?\b', 2),
    ], None),
}

# Types that only the police issue: zeroed when the document was written by the public
POLICE_ISSUED_TYPES = {'police_summons', 'police_complaint_ack', 'police_info_request',
                       'police_notice', 'police_letter', 'police_bond', 'police_charge'}

_COMPILED = {
    doc_type: ([(re.compile(p, re.IGNORECASE), w) for p, w in patterns], required)
    for doc_type, (patterns, required) in TYPE_RULES.items()
}
_ISSUER_COMPILED = [(t, re.compile(p, re.IGNORECASE)) for t, p in ISSUER_PATTERNS]
_PUBLIC_COMPILED = [re.compile(p, re.IGNORECASE) for p in PUBLIC_SUBMISSION_PATTERNS]
_INSTITUTION_COMPILED = [re.compile(p, re.IGNORECASE) for p in INSTITUTION_ISSUED_PATTERNS]


def _lines(text: str) -> list[str]:
    return [ln.strip() for ln in (text or '').splitlines() if ln.strip()]


def _split_header(text: str) -> tuple[list[str], list[str]]:
    """
    Return (header_lines, addressee_lines). The header is the first lines of the
    document (letterhead/sender), excluding the 'To:' address block.
    """
    lines = _lines(text)[:12]
    header, addressee = [], []
    in_addressee = False
    for ln in lines:
        if ADDRESSEE_START.match(ln):
            in_addressee = True
            addressee.append(ln)
            continue
        if in_addressee:
            # The address block ends at a salutation, subject line or a blank-ish break
            if re.match(r'^(dear|re\b|ref\b|subject|sir|madam)', ln, re.IGNORECASE) or len(addressee) >= 4:
                in_addressee = False
            else:
                addressee.append(ln)
                continue
        header.append(ln)
    return header[:8], addressee


def detect_issuer(text: str) -> dict:
    """Identify the issuing institution from the letterhead or a 'From:' line."""
    header, addressee = _split_header(text)
    from_lines = [ln for ln in _lines(text) if re.match(r'^\s*from\s*:', ln, re.IGNORECASE)]

    for region_name, region in (('letterhead', header), ('from_line', from_lines)):
        for ln in region:
            for issuer_type, pattern in _ISSUER_COMPILED:
                if pattern.search(ln):
                    return {'type': issuer_type, 'name': ln[:150], 'found_in': region_name}

    # Addressed TO an institution: useful context, but not the issuer
    addressed_to = None
    for ln in addressee:
        for issuer_type, pattern in _ISSUER_COMPILED:
            if pattern.search(ln):
                addressed_to = {'type': issuer_type, 'name': ln[:150]}
                break
        if addressed_to:
            break
    return {'type': 'unknown', 'name': '', 'found_in': '', 'addressed_to': addressed_to}


def detect_origin(text: str, issuer: dict) -> tuple[str, list[str]]:
    """'issued_by_institution', 'submitted_by_public' or 'unclear', with the evidence."""
    public = [m.group(0) for p in _PUBLIC_COMPILED for m in [p.search(text)] if m]
    institutional = [m.group(0) for p in _INSTITUTION_COMPILED for m in [p.search(text)] if m]
    if issuer.get('type') not in (None, 'unknown') and issuer.get('found_in') == 'letterhead':
        institutional.append(f'letterhead: {issuer["name"][:60]}')

    if public and len(public) >= len(institutional):
        return 'submitted_by_public', public
    if institutional and not public:
        return 'issued_by_institution', institutional
    if institutional and public:
        return 'issued_by_institution', institutional + [f'(also mentions: {public[0]})']
    return 'unclear', []


def _score_types(text: str) -> dict[str, tuple[int, list[str]]]:
    lowered = text.lower()
    scores = {}
    for doc_type, (patterns, required) in _COMPILED.items():
        if required and not any(word in lowered for word in required):
            scores[doc_type] = (0, [])
            continue
        total, signals = 0, []
        for pattern, weight in patterns:
            m = pattern.search(text)
            if m:
                total += weight
                signals.append(m.group(0).strip())
        scores[doc_type] = (total, signals)
    return scores


def classify_document(text: str) -> dict:
    """Classify a document from its extracted text. See module docstring."""
    text = text or ''
    if not text.strip():
        return _result('unknown', 0, [], [], {'type': 'unknown', 'name': '', 'found_in': ''},
                       'unclear', [], note='No readable text was extracted from the document.')

    issuer = detect_issuer(text)
    origin, origin_signals = detect_origin(text, issuer)
    raw = _score_types(text)
    scores = {t: s for t, (s, _sig) in raw.items()}

    # Issuer and origin adjustments
    for doc_type in scores:
        group = DOC_TYPE_GROUPS.get(doc_type)
        if scores[doc_type] == 0:
            continue
        if origin == 'submitted_by_public' and doc_type in POLICE_ISSUED_TYPES:
            scores[doc_type] = 0
        elif doc_type == 'complaint_to_police' and origin != 'submitted_by_public':
            scores[doc_type] = 0
        elif group in POLICE_GROUPS and issuer['type'] == 'police' and doc_type != 'police_letter':
            scores[doc_type] += 3
        elif group == 'traffic' and issuer['type'] == 'police':
            scores[doc_type] += 1
        elif doc_type == 'court_summons' and issuer['type'] == 'court':
            scores[doc_type] += 3
        elif doc_type == 'local_authority_notice' and issuer['type'] == 'local_authority':
            scores[doc_type] += 3
        elif group == 'market_trade' and issuer['type'] in ('market_authority', 'local_authority'):
            scores[doc_type] += 1

    # A police-issued document that matched no specific police type is a police letter
    if issuer['type'] == 'police' and origin != 'submitted_by_public':
        specific = [t for t in POLICE_ISSUED_TYPES | {'police_statement', 'police_case_document'}
                    if t != 'police_letter' and scores.get(t, 0) >= MIN_SCORE]
        traffic_specific = [t for t in scores if DOC_TYPE_GROUPS.get(t) == 'traffic' and scores[t] >= MIN_SCORE]
        if not specific and not traffic_specific:
            scores['police_letter'] = max(scores.get('police_letter', 0), MIN_SCORE)

    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    (best, best_score), (second, second_score) = ranked[0], ranked[1]
    alternatives = [{'doc_type': t, 'label': DOC_TYPE_LABELS[t], 'score': s}
                    for t, s in ranked[1:3] if s > 0]

    if best_score < MIN_SCORE:
        if issuer['type'] != 'unknown':
            return _result('other_official', best_score, [], alternatives, issuer, origin, origin_signals,
                           note='Issued by an identifiable institution, but the document type is not one '
                                'LegalBridge recognises.')
        return _result('unknown', best_score, [], alternatives, issuer, origin, origin_signals,
                       note='The document did not clearly match any supported document type.')

    if best_score - second_score < AMBIGUITY_MARGIN and best_score < 8:
        return _result('unknown', best_score, raw[best][1], alternatives, issuer, origin, origin_signals,
                       note=f'The document could be a {DOC_TYPE_LABELS[best].lower()} or a '
                            f'{DOC_TYPE_LABELS[second].lower()}; it was not classified to avoid guessing.')

    return _result(best, best_score, raw[best][1], alternatives, issuer, origin, origin_signals,
                   margin=best_score - second_score)


def _result(doc_type, score, signals, alternatives, issuer, origin, origin_signals, margin=0, note=''):
    if doc_type in ('unknown',) or score < MIN_SCORE:
        confidence = 'none' if doc_type == 'unknown' else 'low'
    elif score >= 8 and margin >= 3:
        confidence = 'high'
    elif score >= 5:
        confidence = 'medium'
    else:
        confidence = 'low'
    return {
        'doc_type': doc_type,
        'label': DOC_TYPE_LABELS.get(doc_type, doc_type),
        'group': DOC_TYPE_GROUPS.get(doc_type, 'other'),
        'confidence': confidence,
        'score': score,
        'signals': signals[:8],
        'alternatives': alternatives,
        'issuer': issuer,
        'origin': origin,
        'origin_signals': origin_signals[:5],
        'note': note,
    }


def classify_document_type(text: str) -> str:
    """Backwards-compatible helper: returns only the doc_type code."""
    return classify_document(text)['doc_type']
