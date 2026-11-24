"""
LegalBridge — USSD menu tree.
Text must stay within USSD character limits (~182 chars per screen).
Session state is tracked in memory (use Redis/DB for production).

Menus not yet translated into a local language fall back to English via
_render_menu(). Add a key with the language code to translate a menu.
"""

# Africa's Talking sends only digits, so the language menu uses option
# numbers. Keep this map in sync with the 'change_language' menu below.
LANGUAGE_OPTIONS = {
    '1': 'en',
    '2': 'lg',
    '3': 'nyn',  # Runyankore
    '4': 'ach',  # Acholi
    '5': 'lgg',  # Lugbara
}

LANGUAGE_OPTION_BY_CODE = {code: option for option, code in LANGUAGE_OPTIONS.items()}

# ---------------------------------------------------------------------------
# Menu definitions
# Each menu entry is: { 'text': display_text, 'next': next_menu_key | None }
# CON = continue session, END = end session
# ---------------------------------------------------------------------------

MENUS = {

    # ── Root ────────────────────────────────────────────────────────────────
    'main': {
        'en': (
            "CON Welcome to LegalBridge\n"
            "Justice Within Reach\n\n"
            "1. Boda Boda Rider\n"
            "2. Market Vendor\n"
            "3. Know Your Rights\n"
            "4. Find Legal Help\n"
            "5. Change Language"
        ),
        'lg': (
            "CON Mukaribuni ku LegalBridge\n"
            "Obwenkanya Bulungi\n\n"
            "1. Omuvuzi wa Boda Boda\n"
            "2. Omusuubuzi wa Akatale\n"
            "3. Manya Eddembe Lyo\n"
            "4. Noonya Obuyambi bw'Amateeka\n"
            "5. Kyusa Olulimi"
        ),
        'nyn': (
            "CON Mukaribuni ku LegalBridge\n"
            "Obwenkanya Bwaho\n\n"
            "1. Omuvuzi wa Boda Boda\n"
            "2. Omusuubuzi wa Akatale\n"
            "3. Manya Ekitiibwa Kyawe\n"
            "4. Noonya Obuyambi bw'Amateeka\n"
            "5. Hindura Orurimi"
        ),
        'ach': (
            "CON Welcome to LegalBridge\n\n"
            "1. Boda Boda Rider\n"
            "2. Market Vendor\n"
            "3. Know Your Rights\n"
            "4. Find Legal Help\n"
            "5. Ywal Leb"
        ),
        'lgg': (
            "CON LegalBridge Ati\n"
            "Obubaka obw'amateeka\n\n"
            "1. Omuvuzi wa Boda\n"
            "2. Omusuubuzi wa Akatale\n"
            "3. Manya eddembe lyawe\n"
            "4. Noonya obuyambi\n"
            "5. Hinduka Olulimi"
        ),
        'options': {
            '1': 'boda_main',
            '2': 'vendor_main',
            '3': 'rights_main',
            '4': 'legal_help',
            '5': 'change_language',
        }
    },

    # ── Boda Boda ────────────────────────────────────────────────────────────
    'boda_main': {
        'en': (
            "CON Boda Boda Rider\n\n"
            "1. Traffic violation notice\n"
            "2. I was stopped by police\n"
            "3. Understand a penalty\n"
            "4. Payment procedure\n"
            "0. Back"
        ),
        'lg': (
            "CON Omuvuzi wa Boda Boda\n\n"
            "1. Obubaka bw'okwetuka\n"
            "2. Poliisi yansinzya\n"
            "3. Tegeera omusango\n"
            "4. Enkola y'okusasula\n"
            "0. Odda Eggwanga"
        ),
        'options': {
            '1': 'boda_violation',
            '2': 'boda_stopped',
            '3': 'boda_penalty',
            '4': 'boda_payment',
            '0': 'main',
        }
    },

    'boda_violation': {
        'en': (
            "END Traffic Violation Notice\n\n"
            "A traffic violation notice is an official document "
            "stating you may have broken a road rule.\n\n"
            "What to do:\n"
            "1. Keep the notice safe\n"
            "2. Note the reference number\n"
            "3. Check the payment deadline\n"
            "4. Use LegalBridge app to upload "
            "and understand the full notice.\n\n"
            "For full analysis, download the "
            "LegalBridge app."
        ),
        'lg': (
            "END Obubaka bw'Okwetuka\n\n"
            "Obubaka bw'okwetuka bwe bubaka "
            "obutereevu obugamba nga owetuse "
            "amateeka ag'ekkubo.\n\n"
            "Ky'okola:\n"
            "1. Kubika obubaka obulungi\n"
            "2. Wandiika namba y'okulabirira\n"
            "3. Kengera olunaku lw'okusasula\n"
            "4. Kozesa app ya LegalBridge."
        ),
        'options': {}
    },

    'boda_stopped': {
        'en': (
            "END Stopped by Police/Officer\n\n"
            "Your rights when stopped:\n"
            "- Ask for the officer's name & badge number\n"
            "- Ask what specific rule was broken\n"
            "- Request a written notice\n"
            "- Do not pay unofficial 'on the spot' fees\n"
            "- Official fines have receipts\n\n"
            "For verified legal information, "
            "use the LegalBridge app.\n"
            "Legal aid: Uganda Law Society "
            "www.uls.or.ug"
        ),
        'lg': (
            "END Poliisi Yakusimba\n\n"
            "Eddembe lyo ng'okuggwa:\n"
            "- Saba erinnya n'obuwanguzi bwe\n"
            "- Buuza ekibiina ki ky'eteeka "
            "kye wayetuse\n"
            "- Saba obubaka obuwandiikiddwa\n"
            "- Tolipya ssente ez'enjawulo\n\n"
            "Kozesa app ya LegalBridge."
        ),
        'options': {}
    },

    'boda_penalty': {
        'en': (
            "END Understanding Penalties\n\n"
            "Traffic penalties in Uganda are set "
            "by law. Unofficial payments are not "
            "legally valid.\n\n"
            "- Always get an official receipt\n"
            "- Payments go through Uganda Revenue "
            "Authority or approved channels\n"
            "- Keep all receipts\n\n"
            "For specific penalty amounts, "
            "use the LegalBridge app which "
            "references verified Ugandan law."
        ),
        'lg': (
            "END Tegeera Emisango\n\n"
            "Emisango gy'ekkubo mu Uganda "
            "egemerwa amateeka.\n\n"
            "- Buuza resiti ya gwanga\n"
            "- Ssente ziweerereza mu URA\n"
            "- Kubika resiti zonna\n\n"
            "Kozesa app ya LegalBridge."
        ),
        'options': {}
    },

    'boda_payment': {
        'en': (
            "END Official Payment Procedure\n\n"
            "For traffic fines in Uganda:\n"
            "1. Receive official notice with "
            "reference number\n"
            "2. Pay at Uganda Revenue Authority "
            "or approved bank\n"
            "3. Keep your payment receipt\n"
            "4. Present receipt if requested\n\n"
            "IMPORTANT: Do not pay cash to "
            "individual officers without "
            "an official receipt.\n\n"
            "Use LegalBridge app for more."
        ),
        'lg': (
            "END Enkola y'Okusasula\n\n"
            "Emisango gy'ekkubo mu Uganda:\n"
            "1. Kubika obubaka n'namba\n"
            "2. Sasula ku URA oba banki\n"
            "3. Kubika resiti yo\n"
            "4. Leeta resiti ng'beddewa\n\n"
            "Kozesa app ya LegalBridge."
        ),
        'options': {}
    },

    # ── Market Vendor ────────────────────────────────────────────────────────
    'vendor_main': {
        'en': (
            "CON Market Vendor\n\n"
            "1. Eviction notice\n"
            "2. My allocation slip\n"
            "3. Payment receipt help\n"
            "4. Market vendor rights\n"
            "0. Back"
        ),
        'lg': (
            "CON Omusuubuzi wa Akatale\n\n"
            "1. Obubaka bw'okufulumizibwa\n"
            "2. Pepa ly'okuweebwayo\n"
            "3. Obuyambi bw'resiti\n"
            "4. Eddembe ly'omusuubuzi\n"
            "0. Odda Eggwanga"
        ),
        'options': {
            '1': 'vendor_eviction',
            '2': 'vendor_allocation',
            '3': 'vendor_receipt',
            '4': 'vendor_rights',
            '0': 'main',
        }
    },

    'vendor_eviction': {
        'en': (
            "END Eviction Notice\n\n"
            "If told to leave your stall:\n"
            "- Keep all your documents safe\n"
            "- Do not leave without written notice\n"
            "- Ask for the reason in writing\n"
            "- Ask for the official deadline\n"
            "- Check you have allocation slip "
            "and payment receipts\n\n"
            "LegalBridge cannot determine if "
            "an eviction is lawful from USSD.\n\n"
            "Use the LegalBridge app to upload "
            "your documents for full analysis.\n"
            "Legal aid: FIDA Uganda "
            "www.fidauganda.org"
        ),
        'lg': (
            "END Obubaka bw'Okufulumizibwa\n\n"
            "Ng'bagamba okufuluma:\n"
            "- Kubika empapula zonna\n"
            "- Tolekuka naye n'obubaka\n"
            "- Saba ensonga mu mpapula\n"
            "- Kubika pepa ly'okuweebwayo\n\n"
            "Kozesa app ya LegalBridge."
        ),
        'options': {}
    },

    'vendor_allocation': {
        'en': (
            "END Allocation Slip\n\n"
            "Your allocation slip is an important "
            "document. It shows you were assigned "
            "a stall by market authority.\n\n"
            "Keep it safe. It may show:\n"
            "- Stall number\n"
            "- Date of allocation\n"
            "- Authority that issued it\n"
            "- Any conditions attached\n\n"
            "Upload it on the LegalBridge app "
            "for a full explanation."
        ),
        'lg': (
            "END Pepa ly'Okuweebwayo\n\n"
            "Pepa lyo ly'okuweebwayo mpapula "
            "enkulu nnyo. Lilagira nga "
            "baakuwa essimu.\n\n"
            "Lisobola okulagira:\n"
            "- Namba y'essimbi\n"
            "- Olunaku lw'okuweebwayo\n\n"
            "Kozesa app ya LegalBridge."
        ),
        'options': {}
    },

    'vendor_receipt': {
        'en': (
            "END Payment Receipts\n\n"
            "Always keep payment receipts for:\n"
            "- Market fees\n"
            "- Stall rent\n"
            "- Any other official payments\n\n"
            "Receipts may help show that you "
            "have met your obligations.\n\n"
            "If you have lost receipts, ask "
            "market management for a statement "
            "of account.\n\n"
            "Upload receipts on LegalBridge "
            "app for analysis."
        ),
        'lg': (
            "END Obuyambi bw'Resiti\n\n"
            "Kubika resiti za:\n"
            "- Omusaasizi w'akatale\n"
            "- Omulimu gw'essimbi\n\n"
            "Resiti zikolera obujulizi.\n\n"
            "Kozesa app ya LegalBridge."
        ),
        'options': {}
    },

    'vendor_rights': {
        'en': (
            "END Vendor Rights (Markets Act)\n"
            "s.18: registration is free. s.21: "
            "committee allocates stalls.\n"
            "s.24: fees displayed. s.16(2): "
            "3 months' written notice.\n"
            "Source: Markets Act 2023"
        ),
        'lg': (
            "END Eddembe ly'Omusuubuzi\n"
            "s.18: okuweebwa kwa bwereere. s.21: "
            "ekitiibwa kigaba essimbi.\n"
            "s.24: omusaasizo gulagibwa. s.16(2): "
            "obubaka bwa myezi 3.\n"
            "Ensibuko: Markets Act 2023"
        ),
        'options': {}
    },

    # ── Know Your Rights ─────────────────────────────────────────────────────
    'rights_main': {
        'en': (
            "CON Know Your Rights\n\n"
            "1. Traffic laws\n"
            "2. Market vendor rights\n"
            "3. Employment information\n"
            "4. Other legal information\n"
            "0. Back"
        ),
        'lg': (
            "CON Manya Eddembe Lyo\n\n"
            "1. Amateeka g'ekkubo\n"
            "2. Eddembe ly'omusuubuzi\n"
            "3. Ebikwata ku mulimu\n"
            "4. Amateeka amalala\n"
            "0. Odda Eggwanga"
        ),
        'options': {
            '1': 'rights_traffic',
            '2': 'vendor_rights',
            '3': 'rights_employment',
            '4': 'rights_other',
            '0': 'main',
        }
    },

    'rights_traffic': {
        'en': (
            "END Boda Rights\n"
            "s.146: carry copy of licence & "
            "registration book; originals in "
            "72h/120h if asked.\n"
            "Reg 11: helmet must be worn & "
            "fastened.\n"
            "Sources: Act 6/2020; S.I.34/2023"
        ),
        'lg': (
            "END Eddembe ly'Omuvuzi\n"
            "s.146: twala kopi ya layisensi n'empapula "
            "z'ebidduka; ey'edda mu ssaawa 72/120.\n"
            "Reg 11: enkufiira esibibwe bulungi.\n"
            "Ensibuko: Act 6/2020; S.I.34/2023"
        ),
        'options': {}
    },

    'rights_employment': {
        'en': (
            "END Employment Information\n\n"
            "Uganda's Employment Act covers "
            "rights at work.\n\n"
            "General information:\n"
            "- Workers are entitled to written "
            "employment terms\n"
            "- Minimum wage provisions apply\n"
            "- Unfair dismissal has remedies\n\n"
            "Note: Many informal workers may "
            "not have formal contracts. Your "
            "rights may differ.\n\n"
            "For your specific situation, use "
            "LegalBridge app or visit a legal "
            "aid provider."
        ),
        'lg': (
            "END Ebikwata ku Mulimu\n\n"
            "Amateeka g'Emirimu Uganda "
            "gakulaakulanya eddembe "
            "ly'abakozi.\n\n"
            "Kozesa app ya LegalBridge."
        ),
        'options': {}
    },

    'rights_other': {
        'en': (
            "END Other Legal Information\n\n"
            "LegalBridge currently covers:\n"
            "- Traffic and road safety law\n"
            "- Market and vendor law\n"
            "- Employment information\n\n"
            "For other legal matters:\n"
            "- Uganda Law Society: uls.or.ug\n"
            "- FIDA Uganda: fidauganda.org\n"
            "- Legal Aid Service Providers "
            "in your district\n\n"
            "More topics coming soon on the "
            "LegalBridge app."
        ),
        'lg': (
            "END Amateeka Amalala\n\n"
            "LegalBridge kati ekuuma:\n"
            "- Amateeka g'ekkubo\n"
            "- Amateeka g'akatale\n\n"
            "Ebikwata ku bibeele ebirala:\n"
            "- Uganda Law Society: uls.or.ug\n\n"
            "Kozesa app ya LegalBridge."
        ),
        'options': {}
    },

    # ── Legal Help ───────────────────────────────────────────────────────────
    'legal_help': {
        'en': (
            "END Find Legal Help\n\n"
            "Legal Aid Organisations:\n\n"
            "Uganda Law Society\n"
            "Tel: +256 414 259 808\n"
            "www.uls.or.ug\n\n"
            "FIDA Uganda (Women & Family)\n"
            "Tel: +256 414 530 848\n"
            "www.fidauganda.org\n\n"
            "Uganda Christian Lawyers\n"
            "Fraternity: www.uclf.org\n\n"
            "For full directory, use the "
            "LegalBridge app."
        ),
        'lg': (
            "END Noonya Obuyambi bw'Amateeka\n\n"
            "Uganda Law Society\n"
            "Tel: +256 414 259 808\n\n"
            "FIDA Uganda\n"
            "Tel: +256 414 530 848\n\n"
            "Kozesa app ya LegalBridge "
            "okulabirira ebyenjawulo."
        ),
        'options': {}
    },

    # ── Language ─────────────────────────────────────────────────────────────
    'change_language': {
        'en': (
            "CON Choose Language\n\n"
            "1. English\n"
            "2. Luganda\n"
            "3. Runyankore\n"
            "4. Acholi\n"
            "5. Lugbara\n"
            "0. Back"
        ),
        'lg': (
            "CON Londa Olulimi\n\n"
            "1. Olungereza\n"
            "2. Oluganda\n"
            "3. Orunyankore\n"
            "4. Leb Acoli\n"
            "5. Lugbarati\n"
            "0. Back"
        ),
        'nyn': (
            "CON Londa Orurimi\n\n"
            "1. Olungereza\n"
            "2. Oluganda\n"
            "3. Orunyankore\n"
            "4. Leb Acoli\n"
            "5. Olugbara\n"
            "0. Back"
        ),
        'ach': (
            "CON Ywal Leb\n\n"
            "1. Leb Engereza\n"
            "2. Leb Luganda\n"
            "3. Leb Runyankore\n"
            "4. Leb Acoli\n"
            "5. Leb Lugbara\n"
            "0. Back"
        ),
        'lgg': (
            "CON Londa Olulimi\n\n"
            "1. Olungereza\n"
            "2. Oluganda\n"
            "3. Orunyankore\n"
            "4. Leb Acoli\n"
            "5. Lugbarati\n"
            "0. Back"
        ),
        'options': {
            '1': '__set_lang_en__',
            '2': '__set_lang_lg__',
            '3': '__set_lang_nyn__',
            '4': '__set_lang_ach__',
            '5': '__set_lang_lgg__',
        }
    },
}
