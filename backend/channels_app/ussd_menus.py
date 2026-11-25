"""
LegalBridge — USSD menu tree.
Text must stay within USSD character limits (~182 chars per screen).
Session state is tracked in memory (use Redis/DB for production).

Every screen has all five languages. Runyankore (nyn) and Acholi (ach) were
written by hand and Lugbara (lgg) was machine-translated with Sunbird AI; all
three are drafts for native-speaker review. When you change an English screen,
update the other languages too: tests/test_ussd.py checks that each translation
keeps the same CON/END, option numbers, numbers and web addresses.
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
            "CON Tukwakiire ahari LegalBridge\n"
            "Obwinganwa Haihi Naiwe\n"
            "\n"
            "1. Omuvugi wa Boda Boda\n"
            "2. Omucuruzi w'omu Katare\n"
            "3. Manya Obugabe Bwawe\n"
            "4. Sherura Obuhwezi bw'Ebiragiro\n"
            "5. Hindura Orurimi"
        ),
        'ach': (
            "CON Wajoli i LegalBridge\n"
            "Ngol Matir Cok Boti\n"
            "\n"
            "1. Laryem Boda Boda\n"
            "2. Lacat i Cuk\n"
            "3. Nge Twero Meri\n"
            "4. Yeny Kony me Cik\n"
            "5. Lok Leb"
        ),
        'lgg': (
            "CON Mi a'i mi LegalBridge vu\n"
            "E'yo liza 'bani ecozu esuzu ra\n"
            "\n"
            "1. Boda Boda 'ba onzupi ri\n"
            "2. Ba afa ozipi cu'a ri\n"
            "3. Mi ma driwala ni 'diyi nizu\n"
            "4. Mi esu azakoma azita palari\n"
            "5. Mi oja ti ni"
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
        'nyn': (
            "CON Omuvugi wa Boda Boda\n"
            "\n"
            "1. Ebaruha y'omusango gw'omu muhanda\n"
            "2. Omupolisi yaanyemeza\n"
            "3. Yetegyereze omutango\n"
            "4. Omuringo gw'okusasura\n"
            "0. Garuka"
        ),
        'ach': (
            "CON Laryem Boda Boda\n"
            "\n"
            "1. Karatac me bal me yo\n"
            "2. Lapulici ojuko an\n"
            "3. Niang i kom cul\n"
            "4. Yo me culo\n"
            "0. Dok Cen"
        ),
        'lgg': (
            "CON Boda Boda 'ba onzupi ri\n"
            "\n"
            "1. E'yo 'bani ecezu e'yo azita onyozuri ma dria\n"
            "2. Polisi eyi atri ma ra\n"
            "3. E'yo penati vuri va\n"
            "4. Otita ofeza niri\n"
            "0. Vutia"
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
        'nyn': (
            "END Ebaruha y'Omusango gw'Omu Muhanda\n"
            "\n"
            "Ebaruha y'omusango gw'omu muhanda n'ekihandiiko kya gavumenti "
            "ekirikugamba ngu nobaasa kuba wahenda ekiragiro ky'omu muhanda.\n"
            "\n"
            "Eky'okukora:\n"
            "1. Biika gye ebaruha\n"
            "2. Handiika enamba y'okureeberaho\n"
            "3. Reeba ekiro ky'okumaririraho kusasura\n"
            "4. Kozesa app ya LegalBridge kuhereza n'okwetegyereza ebaruha yoona.\n"
            "\n"
            "Okucondooza kwona, teeka app ya LegalBridge aha simu yaawe."
        ),
        'ach': (
            "END Karatac me Bal me Yo\n"
            "\n"
            "Karatac me bal me yo obedo karatac me gamente ma waco ni itwero bedo "
            "ni iturro cik mo me yo.\n"
            "\n"
            "Ngo ma myero itim:\n"
            "1. Gwok karatac maber\n"
            "2. Coo namba me ngiyo\n"
            "3. Ngi nino me agiki me culo\n"
            "4. Tii ki app me LegalBridge me cwalo ki niang i karatac ducu.\n"
            "\n"
            "Pi ngiyo ducu, ket app me LegalBridge i cim meri."
        ),
        'lgg': (
            "END E'yo azita onyozani nzila dria ri ma e'yo ecezu\n"
            "\n"
            "E'yo 'bani ecezu e'yo azita onyoza nzila dria ri ma dria ri eri "
            "kokobi azi ngapi ra ni e'dapi kini mi eco nga azita nzila dria ri "
            "nyaku ra.\n"
            "\n"
            "Afa 'yezu:\n"
            "1. Le mi ma 'ba e'yo 'bani 'ba o'duko fezu ri muke\n"
            "2. Mi ma ne namba e'yo 'bani 'ba alenia ri\n"
            "3. Mi ma andri o'du 'bani afa ofezu ri\n"
            "4. Mi ayu app LegalBridge ni e'yo 'da ma driari fezu azini vazu ra\n"
            "\n"
            "E'yo eti ondaza dria 'yezu, mi ma e'du app LegalBridge niri ra"
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
            "Kozesa app ya LegalBridge.\n"
            "Obuyambi bw'amateeka: Uganda Law Society "
            "www.uls.or.ug"
        ),
        'nyn': (
            "END Omupolisi Yaakwemeza\n"
            "\n"
            "Obugabe bwawe ku bakwemeza:\n"
            "- Shaba eiziina ry'omupolisi n'enamba ye\n"
            "- Buuza ekiragiro ekyahenzirwe\n"
            "- Shaba ebaruha ehandiikirwe\n"
            "- Otasasura sente zitari za gavumenti aho n'aho\n"
            "- Emitango ya gavumenti eine risiiti\n"
            "\n"
            "Amakuru g'ebiragiro agahamiziibwe, kozesa app ya LegalBridge.\n"
            "Obuhwezi bw'ebiragiro: Uganda Law Society www.uls.or.ug"
        ),
        'ach': (
            "END Lapulici Ojuki\n"
            "\n"
            "Twero meri ka kijuki:\n"
            "- Peny nying lapulici ki namba ne\n"
            "- Peny cik ma kiturro\n"
            "- Kwa karatac ma kicoyo\n"
            "- Pe icul cente ma pe me gamente i kabedo meno\n"
            "- Cul me gamente tye ki risit\n"
            "\n"
            "Pi ngec me cik ma kimoko, tii ki app me LegalBridge.\n"
            "Kony me cik: Uganda Law Society www.uls.or.ug"
        ),
        'lgg': (
            "END Ba e'yo 'du Polisi/azita ma drilea\n"
            "\n"
            "Drilemgbo mivileri 'bani mi atriria:\n"
            "- Le mi ma zi 'ba azi ngapi ri ma ru azini namba badge niri\n"
            "- Zi azita 'bani onyo ri a'dini\n"
            "- Le mi ma si waraga e'yo 'da ma dria\n"
            "- Mi ma ofe aje 'yeta azita palani ku 'diyi ku\n"
            "- E'yo ofeza 'diyi ma dria kokobi ci\n"
            "\n"
            "O'duko azita ma dria 'bani esu kililiruri, le mi ayu app LegalBridge "
            "niri'i\n"
            "Azakoma azita palani: Uganda Law Society www.uls.or.ug"
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
        'nyn': (
            "END Okwetegyereza Emitango\n"
            "\n"
            "Emitango y'omu muhanda omu Uganda eteerwaho ebiragiro. Sente "
            "ezisasurwa zitari za gavumenti tiziikirizibwa omu biragiro.\n"
            "\n"
            "- Buriijo tunga risiiti ya gavumenti\n"
            "- Sente zisasurirwa omu Uganda Revenue Authority nari omu miringo "
            "ehamiziibwe\n"
            "- Biika risiiti zoona\n"
            "\n"
            "Kumanya obwingi bw'omutango, kozesa app ya LegalBridge erikukozesa "
            "ebiragiro bya Uganda ebihamiziibwe."
        ),
        'ach': (
            "END Niang i Kom Cul\n"
            "\n"
            "Cul me yo i Uganda cik aye oketo. Cul ma pe me gamente pe tye atir i "
            "cik.\n"
            "\n"
            "- Kare ducu nong risit me gamente\n"
            "- Cul cito ki i Uganda Revenue Authority onyo yo ma kiye\n"
            "- Gwok risit ducu\n"
            "\n"
            "Me ngeyo wel me cul, tii ki app me LegalBridge ma tiyo ki cik pa "
            "Uganda ma kimoko."
        ),
        'lgg': (
            "END E'yo 'bani e'yo onzi 'yezu 'diyi vazu\n"
            "\n"
            "E'yo 'bani 'ba eyi ma dria e'yo onzi 'yezu 'diyi Ugandaa 'diyi azita "
            "si. Afa ofeza azi ngapi ku 'diyi ovuni azita palaa ku.\n"
            "\n"
            "- Mi ma esu sawa driasi risiti azita pala ri\n"
            "- Robia feza ni mu Uganda Revenue Authority kani geri 'bani a'i ra "
            "'diyi ma alea\n"
            "- Le mi ma mba kokobi dria 'diyi\n"
            "\n"
            "E'yo 'bani ega kini yi ma eselea ci 'diyi ma dria, mi ayu app "
            "LegalBridge ni azita Ugandaa 'diyi ma ale andrizu."
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
        'nyn': (
            "END Omuringo gw'Okusasura ogwa Gavumenti\n"
            "\n"
            "Ahabw'emitango y'omu muhanda omu Uganda:\n"
            "1. Tunga ebaruha ya gavumenti erimu enamba y'okureeberaho\n"
            "2. Sasura ahari Uganda Revenue Authority nari banka ehamiziibwe\n"
            "3. Biika risiiti yaawe y'okusasura\n"
            "4. Yoreka risiiti baakugishaba\n"
            "\n"
            "KIKURU: Otaha omupolisi sente omu ngaro otaine risiiti ya gavumenti.\n"
            "\n"
            "Kozesa app ya LegalBridge kumanya ebindi."
        ),
        'ach': (
            "END Yo me Culo me Gamente\n"
            "\n"
            "Pi cul me yo i Uganda:\n"
            "1. Nong karatac me gamente ma tye ki namba me ngiyo\n"
            "2. Cul i Uganda Revenue Authority onyo bange ma kiye\n"
            "3. Gwok risit me culo meri\n"
            "4. Nyut risit ka kipenyo\n"
            "\n"
            "PIRE TEK: Pe imi lapulici cente i cing labongo risit me gamente.\n"
            "\n"
            "Tii ki app me LegalBridge pi ngec mukene."
        ),
        'lgg': (
            "END E'yo 'bani robia ofezu azita palari\n"
            "\n"
            "E'yo ongmbo afa acizu 'diyi ma dria Ugandaa:\n"
            "1. Mi isu o'duko azita palani namba be\n"
            "2. Mi ma ofe amuti Uganda Revenue Authority niri vu kani ero robia "
            "ta mbazuri ma alia\n"
            "3. Mi ma mba mi vile receipt ofa niri\n"
            "4. Mi ma fe kokobi afa ozizuri ka 'ba le ria\n"
            "\n"
            "OKPORU: Le mi ma fe sende 'ba azi alu alu ni ku kokoru kokobi ofeza "
            "niri ka ovu yo ria.\n"
            "\n"
            "Le mi ayu app LegalBridge niri ma azi ngazu drile."
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
        'nyn': (
            "CON Omucuruzi w'omu Katare\n"
            "\n"
            "1. Ebaruha y'okubingwa\n"
            "2. Orupapura rwangye rw'ekifo\n"
            "3. Obuhwezi aha risiiti\n"
            "4. Obugabe bw'omucuruzi w'omu katare\n"
            "0. Garuka"
        ),
        'ach': (
            "CON Lacat i Cuk\n"
            "\n"
            "1. Karatac me ryemo\n"
            "2. Karatac na me kabedo\n"
            "3. Kony i kom risit\n"
            "4. Twero pa lacat i cuk\n"
            "0. Dok Cen"
        ),
        'lgg': (
            "CON Ba afa ozipi cu'a ri\n"
            "\n"
            "1. E'yo 'bani 'ba ofuzu joa ri\n"
            "2. Ma vile kokobi 'bani ma o'bizuri\n"
            "3. Receipt of payment ni azakoma fe\n"
            "4. Drilemgbo 'ba afa ozipi cu'a 'diyi ni\n"
            "0. Vutia"
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
            "Kozesa app ya LegalBridge.\n"
            "Obuyambi bw'amateeka: FIDA Uganda "
            "www.fidauganda.org"
        ),
        'nyn': (
            "END Ebaruha y'Okubingwa\n"
            "\n"
            "Baakugambira kuruga omu kifo kyawe:\n"
            "- Biika gye ebihandiiko byawe byona\n"
            "- Otaruga otahairwe ebaruha ehandiikirwe\n"
            "- Shaba enshonga ehandiikirwe\n"
            "- Shaba ekiro ky'okumaririraho kya gavumenti\n"
            "- Reeba ngu oine orupapura rw'ekifo na risiiti z'okusasura\n"
            "\n"
            "LegalBridge tekubaasa kumanya kurabira aha USSD yaaba okubingwa "
            "kuhikire omu biragiro.\n"
            "\n"
            "Kozesa app ya LegalBridge kuhereza ebihandiiko byawe bicondoozibwe "
            "gye.\n"
            "Obuhwezi bw'ebiragiro: FIDA Uganda www.fidauganda.org"
        ),
        'ach': (
            "END Karatac me Ryemo\n"
            "\n"
            "Ka kiwaco ni ia ki i kabedo ni:\n"
            "- Gwok karatac ni ducu maber\n"
            "- Pe ia labongo karatac me ngec ma kicoyo\n"
            "- Kwa tyen lok ma kicoyo\n"
            "- Kwa nino me agiki me gamente\n"
            "- Ngi ka itye ki karatac me kabedo ki risit me culo\n"
            "\n"
            "LegalBridge pe twero ngeyo ki i USSD ka ryemo obedo atir i cik.\n"
            "\n"
            "Tii ki app me LegalBridge me cwalo karatac ni wek kingi iye ducu.\n"
            "Kony me cik: FIDA Uganda www.fidauganda.org"
        ),
        'lgg': (
            "END E'yo 'bani 'ba ofuzu joa ri\n"
            "\n"
            "Ba ka mi dri 'yo kini mi ku pari mini afa ozizu ri ma aliarisi:\n"
            "- Mi ma mba kokobi mi vile 'diyi ma ta kililiru\n"
            "- Mi ma ku 'ba azi kokoru e'yo siza si\n"
            "- Le mi ma zi e'yo 'da ma dria geri siza si\n"
            "- Le mi ma zi o'du 'bani lezu e'yo nde 'yezu ri\n"
            "- Le mi ma andri kini mi vu kokobi 'bani robia fezu azini kokobi "
            "'bani ofeza ofezu ri ci\n"
            "\n"
            "LegalBridge econi ni kani 'ba azini eco 'ba ofu joa azita pala ku "
            "yari USSD si ku\n"
            "\n"
            "Mi ayu app LegalBridge ni mi vile kokobi 'diyi ma ti ojizu e'yo eti "
            "ondaza dria ri ma alia.\n"
            "Azakoma azita palani: FIDA Uganda www.fidauganda.org"
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
        'nyn': (
            "END Orupapura rw'Ekifo\n"
            "\n"
            "Orupapura rwawe rw'ekifo n'ekihandiiko ekikuru. Nirworeka ngu "
            "abakuru b'akatare bakuhaire ekifo.\n"
            "\n"
            "Rubiike gye. Nirubaasa kworeka:\n"
            "- Enamba y'ekifo\n"
            "- Ekiro ky'okuhabwa ekifo\n"
            "- Abakuru abaruhaire\n"
            "- Ebiragiro byona ebirikukwataho\n"
            "\n"
            "Ruhereze aha app ya LegalBridge otunge ensobanuro yoona."
        ),
        'ach': (
            "END Karatac me Kabedo\n"
            "\n"
            "Karatac me kabedo meri obedo karatac ma pire tek. Nyuto ni lutela "
            "cuk gumiyi kabedo.\n"
            "\n"
            "Gwoke maber. Romo nyuto:\n"
            "- Namba me kabedo\n"
            "- Nino me miyo kabedo\n"
            "- Lutela ma gumiyo\n"
            "- Cik mo keken ma kimato iye\n"
            "\n"
            "Cwale i app me LegalBridge wek inong tyen lok ducu."
        ),
        'lgg': (
            "END E'yo 'bani afa fezu 'diyi ma dria\n"
            "\n"
            "Mi vile allocation slip eri kokobi azi orodriruni'i. Eri e'da kini "
            "'ba fe mi dri pari cuu ma alia ni amuti cuu ma dricepiri vu.\n"
            "\n"
            "Mi ma mba eri kililiru. Eco nga e'da:\n"
            "- Stall namba\n"
            "- O'du 'bani afa fezu ri\n"
            "- Driceza fepi eri dri ri\n"
            "- E'yo azi 'bani o'bale drinia 'diyi\n"
            "\n"
            "Mi o'ba eri app LegalBridge niri ma dria e'yo 'diyi ma ti zizu "
            "kililiru."
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
        'nyn': (
            "END Risiiti z'Okusasura\n"
            "\n"
            "Buriijo biika risiiti z'okusasura:\n"
            "- Emisoro y'akatare\n"
            "- Obukodyo bw'ekifo\n"
            "- Ebindi byona ebisasurwa gavumenti\n"
            "\n"
            "Risiiti nizibaasa kworeka ngu okozire ebi oshemereire kukora.\n"
            "\n"
            "Waaba waaburwa risiiti, shaba abakuru b'akatare bakuhe orupapura "
            "orworeka ebi wasasuire.\n"
            "\n"
            "Hereza risiiti aha app ya LegalBridge zicondoozibwe."
        ),
        'ach': (
            "END Risit me Culo\n"
            "\n"
            "Kare ducu gwok risit me culo pi:\n"
            "- Cul me cuk\n"
            "- Cul me kabedo\n"
            "- Cul mukene me gamente\n"
            "\n"
            "Risit romo konyo nyuto ni itimo gin ma myero itim.\n"
            "\n"
            "Ka irwenyo risit, kwa lutela cuk gumiyi karatac ma nyuto cul ma "
            "iculo.\n"
            "\n"
            "Cwal risit i app me LegalBridge wek kingi iye."
        ),
        'lgg': (
            "END E'yo 'bani ofeza ma dria ri\n"
            "\n"
            "Mi ma mba sawa driasi kokobi ofeza ni 'diyi:\n"
            "- Aje cuu ni 'diyi\n"
            "- Stall rent\n"
            "- Afa azi 'bani ofe azita pala ni\n"
            "\n"
            "Receipt eco fe e'da kini mi 'ye e'yo mini lele 'diyi ra\n"
            "\n"
            "Eka waraga afa oziza ma dria 'diyi avi ra ria, le mi ma zi 'ba cuu "
            "ma dricepiri ni e'yo siza robia ma dria ri.\n"
            "\n"
            "Mi ma o'ba kokobi afa oziza ni 'diyi app LegalBridge niri ma alia "
            "e'yo eti ondazu"
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
        'nyn': (
            "END Obugabe bw'Omucuruzi (Markets Act)\n"
            "s.18: okwehandiikisa ni kw'obusha. s.21: akakiiko nikagaba ebifo.\n"
            "s.24: emisoro eteerwe ahabweru. s.16(2): ebaruha ehandiikirwe "
            "y'emyezi 3.\n"
            "Ahu byarugire: Markets Act 2023"
        ),
        'ach': (
            "END Twero pa Lacat (Markets Act)\n"
            "s.18: coyo nying obedo me nono. s.21: komiti aye poko kabedo.\n"
            "s.24: cul myero kinyut. s.16(2): karatac me ngec ma kicoyo me dwe 3.\n"
            "Kama oa iye: Markets Act 2023"
        ),
        'lgg': (
            "END Drilemgbo 'ba afa ozipi 'diyi ni (Markets Act)\n"
            "s.18: Ba 'ba ru osiza ni pirini s.21: Komiti ni pari o'bi yi ma dria "
            "'diyi awa\n"
            "s.24: Aje 'bani e'da 'diyi s.16(2): E'yo siza mba 3 ni\n"
            "Angu e'yo esuzu: Markets Act 2023"
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
        'nyn': (
            "CON Manya Obugabe Bwawe\n"
            "\n"
            "1. Ebiragiro by'omu muhanda\n"
            "2. Obugabe bw'omucuruzi w'omu katare\n"
            "3. Amakuru g'emirimo\n"
            "4. Amakuru agandi g'ebiragiro\n"
            "0. Garuka"
        ),
        'ach': (
            "CON Nge Twero Meri\n"
            "\n"
            "1. Cik me yo\n"
            "2. Twero pa lacat i cuk\n"
            "3. Ngec i kom tic\n"
            "4. Ngec mukene me cik\n"
            "0. Dok Cen"
        ),
        'lgg': (
            "CON Mi ma driwala ni 'diyi nizu\n"
            "\n"
            "1. Azita nzila dria 'diyi\n"
            "2. Drilemgbo 'ba afa ozipi cu'a 'diyi ni\n"
            "3. O'duko azi esuzu 'diyi\n"
            "4. O'duko azita ni azi 'diyi\n"
            "0. Vutia"
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
        'nyn': (
            "END Obugabe bw'Omuvugi wa Boda\n"
            "s.146: twara kopi ya laisensi n'ekitabo ky'okuhandiikisa; ebyamazima "
            "omu saaha 72/120 baabishaba.\n"
            "Reg 11: enkofiira eine kujwarwa kandi ekomirwe gye.\n"
            "Ahu byarugire: Act 6/2020; S.I.34/2023"
        ),
        'ach': (
            "END Twero pa Laryem Boda\n"
            "s.146: bed ki kopi me laicen ki buk me coyo nying; ma gi ada i cawa "
            "72/120 ka kipenyo.\n"
            "Reg 11: elemet myero kiruk ki kitwey maber.\n"
            "Kama oa iye: Act 6/2020; S.I.34/2023"
        ),
        'lgg': (
            "END Drilemgbo boda eyini\n"
            "s.146: Mi ma 'du kopi kokobi driwala fezu azini buku ru sizu ri; "
            "okori yi sawa 72/120 ma alia 'ba ka zi ria.\n"
            "Reg 11: Le 'ba ma su helmeti azini 'ba ma ombe eri ra\n"
            "Angu e'yo esuzu: Act 6/2020; S.I.34/2023"
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
        'nyn': (
            "END Amakuru g'Emirimo\n"
            "\n"
            "Employment Act ya Uganda neeteeraho obugabe aha mulimo.\n"
            "\n"
            "Amakuru amwe:\n"
            "- Abakozi baine obugabe bw'okuhabwa endagaano y'omulimo ehandiikirwe\n"
            "- Ebiragiro by'omushaara ogwa hansi nibikora\n"
            "- Kubingwa aha mulimo kutari kwa buringaniza kwine obuhwezi\n"
            "\n"
            "Manya: Abakozi baingi abatari omu mirimo y'endagaano nibabaasa kuba "
            "batine ndagaano. Obugabe bwawe nibubaasa kuba butandikaine.\n"
            "\n"
            "Ahabw'enshonga yaawe, kozesa app ya LegalBridge nari oze ahari "
            "abarikuha obuhwezi bw'ebiragiro."
        ),
        'ach': (
            "END Ngec i Kom Tic\n"
            "\n"
            "Employment Act pa Uganda mako twero i tic.\n"
            "\n"
            "Ngec mogo:\n"
            "- Lutic tye ki twero me nongo cik me tic ma kicoyo\n"
            "- Cik me lim matidi loyo tiyo\n"
            "- Ka kiryemo i tic labongo tyen lok atir, tye yo me kony\n"
            "\n"
            "Ngec: Lutic mapol ma pe i tic me cik romo bedo labongo cik me tic. "
            "Twero meri romo bedo mapat.\n"
            "\n"
            "Pi peko meri, tii ki app me LegalBridge onyo icit bot lumiyo kony me "
            "cik."
        ),
        'lgg': (
            "END O'duko azi niri\n"
            "\n"
            "Uganda vile Employment Act ri e'yo driwala azi ngazu 'diyi ma dria\n"
            "\n"
            "O'duko dria 'diyi:\n"
            "- Ba azi ngapi 'diyi ma drilemgbo ci e'yo siza azini 'ba yi dri azi "
            "fezu ri ma dria\n"
            "- E'yo 'bani ofeza ma omgbo esizu ri ni azi nga\n"
            "- E'yo 'bani 'ba ofuzu azita pala ku ri ma aza kozu\n"
            "\n"
            "E'yo 'bani ega ri: Azi'ba karakara azi ngapi azita palaa ku 'diyi "
            "eco ovu kontrakiti azita palaa 'diyi be ku. Mi ma drilemgbo yi eco "
            "ovu ndundu ra.\n"
            "\n"
            "Mi vile e'yo 'diyi ma alia, mi ayu app LegalBridge niri kani mu pari "
            "azakoma fezu e'yo azita ni 'diyi ma alia ri ma alia"
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
            "- Uganda Law Society: uls.or.ug\n"
            "- FIDA Uganda: fidauganda.org\n\n"
            "Kozesa app ya LegalBridge."
        ),
        'nyn': (
            "END Amakuru Agandi g'Ebiragiro\n"
            "\n"
            "Hati LegalBridge neeyoreka:\n"
            "- Ebiragiro by'omu muhanda n'okwerinda akabi\n"
            "- Ebiragiro by'akatare n'abacuruzi\n"
            "- Amakuru g'emirimo\n"
            "\n"
            "Ahabw'enshonga ezindi z'ebiragiro:\n"
            "- Uganda Law Society: uls.or.ug\n"
            "- FIDA Uganda: fidauganda.org\n"
            "- Abarikuha obuhwezi bw'ebiragiro omu disiturikiti yaawe\n"
            "\n"
            "Ebindi nibiija juba aha app ya LegalBridge."
        ),
        'ach': (
            "END Ngec Mukene me Cik\n"
            "\n"
            "Kombedi LegalBridge mako:\n"
            "- Cik me yo ki gwoko kuc i yo\n"
            "- Cik me cuk ki lucat\n"
            "- Ngec i kom tic\n"
            "\n"
            "Pi lok mukene me cik:\n"
            "- Uganda Law Society: uls.or.ug\n"
            "- FIDA Uganda: fidauganda.org\n"
            "- Lumiyo kony me cik i distrik meri\n"
            "\n"
            "Lok mukene bino cok i app me LegalBridge."
        ),
        'lgg': (
            "END O'duko azita ni azi 'diyi\n"
            "\n"
            "LegalBridge ni sawa 'disi e'yo 'diyi ma dria:\n"
            "- Azita nzila dria azini nzila ma agei tema ni\n"
            "- Azita cuu azini 'ba afa ozipi 'diyi ma dria\n"
            "- O'duko azi esuzu 'diyi\n"
            "\n"
            "E'yo azita ni azi 'diyi ma alia:\n"
            "- Uganda Law Society: uls.or.ug\n"
            "- FIDA Uganda: fidauganda.org\n"
            "- Ba azakoma fele e'yo azita ni 'diyi ma alia distrikiti mivileri ma "
            "alea 'diyi\n"
            "\n"
            "E'yo azi eyi emu drioru app LegalBridge niri ma alea"
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
            "Tel: +256 414 259 808\n"
            "www.uls.or.ug\n\n"
            "FIDA Uganda\n"
            "Tel: +256 414 530 848\n"
            "www.fidauganda.org\n\n"
            "Uganda Christian Lawyers\n"
            "Fraternity: www.uclf.org\n\n"
            "Kozesa app ya LegalBridge "
            "okulabirira ebyenjawulo."
        ),
        'nyn': (
            "END Sherura Obuhwezi bw'Ebiragiro\n"
            "\n"
            "Ebitongole by'obuhwezi bw'ebiragiro:\n"
            "\n"
            "Uganda Law Society\n"
            "Tel: +256 414 259 808\n"
            "www.uls.or.ug\n"
            "\n"
            "FIDA Uganda (Abakazi n'Amaka)\n"
            "Tel: +256 414 530 848\n"
            "www.fidauganda.org\n"
            "\n"
            "Uganda Christian Lawyers\n"
            "Fraternity: www.uclf.org\n"
            "\n"
            "Kureeba orukarara rwona, kozesa app ya LegalBridge."
        ),
        'ach': (
            "END Yeny Kony me Cik\n"
            "\n"
            "Dul ma miyo kony me cik:\n"
            "\n"
            "Uganda Law Society\n"
            "Tel: +256 414 259 808\n"
            "www.uls.or.ug\n"
            "\n"
            "FIDA Uganda (Mon ki Paco)\n"
            "Tel: +256 414 530 848\n"
            "www.fidauganda.org\n"
            "\n"
            "Uganda Christian Lawyers\n"
            "Fraternity: www.uclf.org\n"
            "\n"
            "Pi nying ducu, tii ki app me LegalBridge."
        ),
        'lgg': (
            "END Mi esu azakoma azita palari\n"
            "\n"
            "Amuti azakoma fele e'yo azita ni 'diyi ma alia 'diyi:\n"
            "\n"
            "Uganda Law Society\n"
            "Tel: +256 414 259 808\n"
            "www.uls.or.ug\n"
            "\n"
            "FIDA Uganda (Oku azini Familia)\n"
            "Tel: +256 414 530 848\n"
            "www.fidauganda.org\n"
            "\n"
            "Uganda Christian Lawyers\n"
            "Fraternity: www.uclf.org\n"
            "\n"
            "Kata buku dria ma alea, le mi ayu app LegalBridge niri'i"
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
            "CON Toorana Orurimi\n"
            "\n"
            "1. Orungyereza\n"
            "2. Oruganda\n"
            "3. Orunyankore\n"
            "4. Acholi\n"
            "5. Lugbara\n"
            "0. Garuka"
        ),
        'ach': (
            "CON Yer Leb\n"
            "\n"
            "1. Leb Munu\n"
            "2. Leb Luganda\n"
            "3. Leb Runyankore\n"
            "4. Leb Acoli\n"
            "5. Leb Lugbara\n"
            "0. Dok Cen"
        ),
        'lgg': (
            "CON Mi pe ti\n"
            "\n"
            "1. English\n"
            "2. Luganda\n"
            "3. Runyankore\n"
            "4. Acholi\n"
            "5. Lugbarati\n"
            "0. Vutia"
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
