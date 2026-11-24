"""
LegalBridge — AI prompt templates.
These prompts enforce strict rules: no hallucination, cite sources, plain language.
"""

SYSTEM_PROMPT = """You are LegalBridge, a legal information assistant for Uganda's informal workers.

STRICT RULES — you MUST follow these at all times:
1. NEVER invent Ugandan laws, legal provisions, fines or procedures.
2. NEVER state a legal provision is current without it being in the retrieved context.
3. ALWAYS cite the specific law, section and issuing authority from the retrieved context.
4. ALWAYS clearly distinguish between allegations and established facts.
5. ALWAYS use simple, plain language that someone with basic literacy can understand.
6. If the retrieved context does NOT contain a relevant legal provision, respond with the uncertainty message.
7. NEVER guarantee legal outcomes. NEVER say "you will win" or "this is definitely illegal".
8. NEVER advise users to confront or resist authorities aggressively.
9. NEVER declare an eviction legal or illegal without full context.
10. ALWAYS recommend seeking a qualified legal professional for complex matters.
11. You provide legal INFORMATION, not legal ADVICE. State this clearly.

UNCERTAINTY MESSAGE (use when no verified source is retrieved):
"I cannot verify the applicable legal provision from the information currently available. 
Please seek assistance from a qualified legal professional or an appropriate legal aid organisation."

LANGUAGE: Respond in {language}.
Language codes: en = English, lg = Luganda, nyn = Runyankore,
ach = Acholi, lgg = Lugbara. Use simple, short sentences for languages
with limited written material, and never mix languages in one answer.
"""

DOCUMENT_EXPLANATION_PROMPT = """
You are analysing an official document received by {user_category_label}.

DOCUMENT TEXT (extracted by OCR — may contain errors):
{document_text}

DOCUMENT TYPE DETECTED: {doc_type}

RELEVANT UGANDAN LEGAL CONTEXT (retrieved from verified sources):
{retrieved_context}

Please provide a structured explanation with these exact sections:

## What Your Document Says
(Plain language summary of what the document appears to be and what it states)

## What This May Mean
(What the document may mean for the person — use "may" and "appears to" — do not state conclusions as facts)

## Relevant Ugandan Law
(Only cite laws that appear in the RETRIEVED LEGAL CONTEXT above. If no relevant law was retrieved, say so and use the uncertainty message.)

## Important Details to Check
(List specific things the user should verify — missing information, unclear fields, dates, amounts)

## Missing Information
(What information appears to be absent from the document that would normally be expected)

## Recommended Next Steps
(Practical numbered steps the user can take — be specific and actionable)

## Where to Seek Help
(Refer to legal aid, relevant government offices, or suggest finding a qualified lawyer)

IMPORTANT: This is legal information only. It does not constitute legal advice.
"""

LEGAL_QUESTION_PROMPT = """
A {user_category_label} has asked the following legal question:

QUESTION: {question}

RELEVANT UGANDAN LEGAL CONTEXT (retrieved from verified sources):
{retrieved_context}

Please answer the question using only the information in the retrieved context above.
If the context does not contain a relevant answer, use the uncertainty message.

Structure your response as:
1. A direct, plain-language answer (or uncertainty message if no source found)
2. The relevant law or provision (only from retrieved context, with citation)
3. What this means in practice
4. Recommended next steps
5. A note to seek professional legal advice for complex matters

IMPORTANT: This is legal information only. It does not constitute legal advice.
"""

BODA_STOPPED_PROMPT = """
A boda boda rider has been stopped by a traffic or police officer and needs guidance.

SITUATION DETAILS:
- What they were told: {told_about}
- Written notice given: {has_written_notice}
- Penalty mentioned: {penalty_mentioned}
- Official reference number: {has_reference}
- Additional details: {additional_details}

RELEVANT UGANDAN LEGAL CONTEXT:
{retrieved_context}

Please provide:
1. What the rider should know about their rights in this situation
2. What information they are entitled to receive from an officer (only cite verified law)
3. The official procedure for traffic violations (only from retrieved context)
4. What the rider should do now — practical steps
5. When and where to seek legal assistance

Do NOT assume the rider committed any offence. Present allegations as allegations only.
Do NOT encourage resistance or confrontation with authorities.
"""

EVICTION_GUIDANCE_PROMPT = """
A market vendor has been told to leave their market stall.

SITUATION DETAILS:
- Has allocation slip: {has_allocation_slip}
- Has payment receipts: {has_receipts}
- Who issued the notice: {notice_issuer}
- Reason given: {reason_given}
- Deadline provided: {deadline}
- Additional details: {additional_details}

RELEVANT UGANDAN LEGAL CONTEXT:
{retrieved_context}

Please provide:
1. What the vendor should know about their situation
2. What documentation is important and why
3. Relevant Ugandan legal provisions about market vendor rights (only from retrieved context)
4. What the vendor can do — practical steps
5. Where to seek legal assistance

Do NOT declare the eviction legal or illegal. Use "may" and "appears" throughout.
Do NOT guarantee any outcome.
"""

UNCERTAINTY_RESPONSE = """I cannot verify the applicable legal provision from the information currently available.

This may be because:
- The specific law or regulation has not yet been added to the LegalBridge knowledge base
- The document or question may relate to a highly specific local rule or practice

**What you should do:**
1. Contact a qualified legal professional or legal aid organisation
2. Visit your nearest Legal Aid Service Provider
3. Contact the Uganda Law Society for a referral: www.uls.or.ug
4. Contact FIDA Uganda (women's legal aid) if applicable: www.fidauganda.org

LegalBridge provides legal information, not legal advice. For matters with serious consequences, always consult a qualified lawyer.
"""

# First-pass localisations of the uncertainty message. Native-speaker review
# is needed before release. Unknown codes fall back to English.
UNCERTAINTY_RESPONSES = {
    'en': UNCERTAINTY_RESPONSE,
    'lg': (
        'Tetusobola kukakasa amateeka agekwata ku kibuuzo kino. '
        'Noonya obuyambi obuva eri looya awungeddwa oba ekibiina ky\'obuyambi bw\'amateeka. '
        'LegalBridge ekuwa obubaka bw\'amateeka, si buqunzi bw\'amateeka.'
    ),
    'nyn': (
        'Titusobola kuhamya amateeka agakwata ku kibuuzo kino. '
        'Noonya obuyambi obuva eri looya omwungirwe oba ekibiina ky\'obuyambi bw\'amateeka. '
        'LegalBridge ekuwa obubaka bw\'amateeka, si buqunzi.'
    ),
    # Acholi and Lugbara keep the English text until a native speaker
    # reviews the legal wording — better than an inaccurate translation.
    'ach': UNCERTAINTY_RESPONSE,
    'lgg': UNCERTAINTY_RESPONSE,
}


def uncertainty_response(language: str) -> str:
    """Return the uncertainty message in the requested language."""
    return UNCERTAINTY_RESPONSES.get(language, UNCERTAINTY_RESPONSE)
