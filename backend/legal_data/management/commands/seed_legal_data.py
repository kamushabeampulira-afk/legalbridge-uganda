"""
Management command: python manage.py seed_legal_data

Seeds verified EXTRACTS from published Ugandan laws for the rider and vendor
flows. The full official PDFs are kept in legal_sources/official/ and each
record links to its official publisher.

The extracts are written in plain language and say so explicitly; they are not
verbatim quotes of the Acts. Section numbers and propositions were checked
against the official Acts/Statutory Instruments listed in legal_sources/README.md.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from legal_data.models import LegalSource, LegalProvision


VERIFIED_SOURCES = [
    {
        'title': 'Traffic and Road Safety Act, 1998 (Cap 361), as amended by Act 6 of 2020',
        'short_title': 'Traffic & Road Safety Act',
        'instrument_number': 'Cap 361; Act 6 of 2020',
        'category': 'act',
        'subject': 'traffic',
        'issuing_authority': 'Parliament of Uganda',
        'publication_date': '1998-01-01',
        'source_url': (
            'https://works.go.ug/wp-content/uploads/2026/04/'
            'Traffic-Road-Safety-Amendment-Act-2020-FINAL.pdf'
        ),
        'version_or_amendment': 'Amended by the Traffic and Road Safety Act (Amendment) Act, 2020',
        'legal_status': 'amended',
        'summary': (
            'Governs road use, driving licences, vehicle registration, offences and penalties '
            'in Uganda. The 2020 amendment changed licence production rules, penalties and '
            'introduced a demerit points system.'
        ),
        'full_text': (
            'VERIFIED PLAIN-LANGUAGE EXTRACTS — not a verbatim copy of the Act.\n\n'
            's.35(1): A person may only drive a vehicle for which they hold a valid licence '
            'for that group or class of vehicle.\n\n'
            's.70(1)(g) and s.94(1)(g): The Act provides for licences for commercial '
            'motorcycles and motorised tricycles, including Class M.\n\n'
            's.105(1): Using a vehicle without a licence is an offence. Act 6 of 2020 '
            'amended the penalty to a fine not exceeding one hundred currency points or '
            'imprisonment not exceeding one year, or both.\n\n'
            's.122A: Inserted by Act 6 of 2020. The Minister may prescribe a demerit '
            'points system; offences are categorised by severity and points are recorded '
            'against the licence held by that person.\n\n'
            's.146(1): A driver must carry a copy of a valid driving licence at all times '
            'and produce the original within 72 hours when a uniformed police officer '
            'requires it.\n\n'
            's.146(2): A driver must be in possession of a copy of the registration book '
            'and produce the original within 120 hours when required by a uniformed '
            'police officer.\n\n'
            's.146(3): A person crossing the Uganda border must carry their driving '
            'licence, a copy of the registration book with the prescribed certificate, '
            'and a valid insurance certificate.\n\n'
            'See the official PDF linked on this record for the exact statutory wording.'
        ),
        'verification_notes': (
            'Checked against the Ministry of Works and Transport copy of Act 6 of 2020. '
            'Legacy seed sections 118 and 130 were removed: s.118 was repealed by the '
            '2020 amendment and s.130 concerns taking a vehicle without the owner’s '
            'consent, not fixed penalty notices.'
        ),
        'provisions': [
            {
                'section_number': '35(1)',
                'section_title': 'Licence for the class of vehicle',
                'text': (
                    'Verified plain-language extract (not a verbatim quote): a person may '
                    'only drive a vehicle if they hold a valid licence for that group or '
                    'class of vehicle.'
                ),
                'plain_language_summary': (
                    'Your licence must cover the kind of vehicle you are riding. Check the '
                    'class printed on your licence before carrying passengers for payment.'
                ),
                'tags': ['licence', 'class', 'boda boda', 'motorcycle'],
            },
            {
                'section_number': '70(1)(g), 94(1)(g)',
                'section_title': 'Licences for commercial motorcycles and tricycles',
                'text': (
                    'Verified plain-language extract (not a verbatim quote): the Act '
                    'provides for licences for commercial motorcycles and motorised '
                    'tricycles, including Class M.'
                ),
                'plain_language_summary': (
                    'Commercial boda boda work needs the licence class that covers a '
                    'motorcycle used to carry passengers for payment.'
                ),
                'tags': ['Class M', 'commercial motorcycle', 'boda boda', 'licence'],
            },
            {
                'section_number': '105(1)',
                'section_title': 'Using a vehicle without a licence',
                'text': (
                    'Verified plain-language extract (not a verbatim quote): using a '
                    'vehicle without a licence is an offence. Act 6 of 2020 substituted a '
                    'fine not exceeding one hundred currency points or imprisonment not '
                    'exceeding one year, or both.'
                ),
                'plain_language_summary': (
                    'Riding without a valid licence is an offence. The current maximum '
                    'penalty is a fine of up to 100 currency points, up to one year in '
                    'prison, or both.'
                ),
                'tags': ['licence', 'offence', 'penalty', 'boda boda'],
            },
            {
                'section_number': '122A',
                'section_title': 'Demerit points',
                'text': (
                    'Verified plain-language extract (not a verbatim quote): section '
                    '122A, inserted by Act 6 of 2020, allows the Minister to prescribe a '
                    'demerit point system. Regulations categorise offences by severity '
                    'and record points against a licence held by that person.'
                ),
                'plain_language_summary': (
                    'Convictions for some traffic offences can put points on your '
                    'licence record. Take every written notice seriously.'
                ),
                'tags': ['demerit points', 'conviction', 'licence'],
            },
            {
                'section_number': '146(1)-(2)',
                'section_title': 'Production of licence and registration book',
                'text': (
                    'Verified plain-language extract (not a verbatim quote): a driver '
                    'must carry a copy of a valid driving licence at all times and '
                    'produce the original within 72 hours when a uniformed police '
                    'officer requires it. The same applies to a copy of the registration '
                    'book, with the original within 120 hours.'
                ),
                'plain_language_summary': (
                    'You must carry copies. If an officer asks, show the original licence '
                    'within 72 hours and the original registration book within 120 hours.'
                ),
                'tags': ['documents', 'licence', 'registration book', 'police', 'boda boda'],
            },
            {
                'section_number': '146(3)',
                'section_title': 'Documents for travel across the Uganda border',
                'text': (
                    'Verified plain-language extract (not a verbatim quote): a person '
                    'crossing the Uganda border must carry their driving licence, a copy '
                    'of the registration book with the prescribed certificate, and a '
                    'valid insurance certificate.'
                ),
                'plain_language_summary': (
                    'For cross-border travel you need your licence, a certified copy of '
                    'the registration book and a valid insurance certificate.'
                ),
                'tags': ['border', 'insurance', 'documents', 'motorcycle'],
            },
        ],
    },
    {
        'title': (
            'Traffic and Road Safety (Motorcycles and Motorised Tricycles) '
            '(Amendment) Regulations, 2023 (S.I. 34 of 2023)'
        ),
        'short_title': 'Motorcycles (Amendment) Regulations 2023',
        'instrument_number': 'S.I. No. 34 of 2023',
        'category': 'regulation',
        'subject': 'traffic',
        'issuing_authority': 'Ministry of Works and Transport',
        'publication_date': '2023-03-31',
        'source_url': (
            'https://works.go.ug/wp-content/uploads/2026/04/'
            'Traffic-and-Road-Safety-Motorcycles-and-Motorised-Tricycles-'
            'Amendment-Regulations-2023.pdf'
        ),
        'version_or_amendment': 'Amends S.I. No. 30 of 2016',
        'legal_status': 'in_force',
        'summary': (
            'Amends the 2016 motorcycle and tricycle regulations, including helmet '
            'requirements and provisions on public transport providers.'
        ),
        'full_text': (
            'VERIFIED PLAIN-LANGUAGE EXTRACTS — not a verbatim copy of the Regulations.\n\n'
            'Regulation 11(4), (5) and (5a), as amended: helmets must be worn and '
            'properly fastened, and must comply with Uganda National Bureau of Standards '
            'requirements.\n\n'
            'Regulations 11A and 11B, inserted by S.I. 34 of 2023: provisions on public '
            'transport providers and a public transport providers entity.\n\n'
            'See the official PDF linked on this record for the exact wording.'
        ),
        'verification_notes': (
            'Checked against the Ministry of Works and Transport copy of S.I. 34 of 2023.'
        ),
        'provisions': [
            {
                'section_number': '11(4), 11(5), 11(5a)',
                'section_title': 'Helmets: worn, fastened and to UNBS standard',
                'text': (
                    'Verified plain-language extract (not a verbatim quote): regulation '
                    '11 of S.I. 30 of 2016, as amended by S.I. 34 of 2023, requires '
                    'helmets to be worn and properly fastened and to comply with Uganda '
                    'National Bureau of Standards requirements.'
                ),
                'plain_language_summary': (
                    'The helmet must be on your head and strapped on, not just carried, '
                    'and it must meet the UNBS standard.'
                ),
                'tags': ['helmet', 'UNBS', 'boda boda', 'safety'],
            },
            {
                'section_number': '11A-11B',
                'section_title': 'Public transport providers',
                'text': (
                    'Verified plain-language extract (not a verbatim quote): S.I. 34 of '
                    '2023 inserts provisions dealing with public transport providers and '
                    'a public transport providers entity.'
                ),
                'plain_language_summary': (
                    'The 2023 regulations add rules for organised public transport '
                    'providers. Check with your local authority which rules apply to you.'
                ),
                'tags': ['public transport providers', 'boda boda', 'entity'],
            },
        ],
    },
    {
        'title': 'Markets Act, 2023 (Uganda)',
        'short_title': 'Markets Act 2023',
        'instrument_number': 'Act 7 of 2023',
        'category': 'act',
        'subject': 'markets',
        'issuing_authority': 'Parliament of Uganda',
        'publication_date': '2023-05-22',
        'source_url': 'https://www.bills.parliament.ug/attachments/Markets%20Act,%202023.pdf',
        'version_or_amendment': 'Repealed the Markets Act, Cap 94',
        'legal_status': 'in_force',
        'summary': (
            'The current law on public and private markets: vendor registration, '
            'allocation of stalls, market fees, notices, disputes and offences.'
        ),
        'full_text': (
            'VERIFIED PLAIN-LANGUAGE EXTRACTS — not a verbatim copy of the Act.\n\n'
            's.16(2): at least three months’ written notice is required before the '
            'layout or design of a public market is altered.\n\n'
            's.18(4), (5), (8): vendor registration is free of charge, a vendor is '
            'given a registration number, and the register is displayed.\n\n'
            's.19(3), (5)(c): elected heads of market departments have functions '
            'including settlement of disputes.\n\n'
            's.21: an allocation committee allocates spaces, shops, pitches and '
            'stalls; existing registered vendors have priority; a vendor may not hold '
            'more than one stall; unauthorised subletting requires the vendor to '
            'vacate.\n\n'
            's.22: a stall may be treated as abandoned after three months unoccupied '
            'or three months in default of market fees.\n\n'
            's.24(1), (2): market fees are set by the administrative authority and '
            'must be displayed.\n\n'
            's.26(2)-(5): goods may be seized and sold after 14 days, any surplus is '
            'reimbursed, and the allocation may be reallocated.\n\n'
            's.32: selling outside the designated space or in pathways and drains is '
            'prohibited.\n\n'
            'See the official PDF linked on this record for the exact statutory wording.'
        ),
        'verification_notes': (
            'Checked against the Parliament of Uganda PDF and published full text. The '
            'old Markets Act, Cap 94 (1942) was repealed and is not used. Legacy seed '
            'sections 15, 25, 26 and 30 were removed because they did not match this Act.'
        ),
        'provisions': [
            {
                'section_number': '16(2)',
                'section_title': 'Written notice before layout changes',
                'text': (
                    'Verified plain-language extract (not a verbatim quote): at least '
                    'three months’ written notice is required before the layout or '
                    'design of a public market is altered.'
                ),
                'plain_language_summary': (
                    'If the market will be reorganised or rebuilt, vendors must be told '
                    'in writing at least three months before.'
                ),
                'tags': ['notice', 'layout', 'redevelopment', 'vendor'],
            },
            {
                'section_number': '18(4), 18(5), 18(8)',
                'section_title': 'Free vendor registration',
                'text': (
                    'Verified plain-language extract (not a verbatim quote): a vendor '
                    'is registered free of charge, is given a registration number, and '
                    'the register is displayed.'
                ),
                'plain_language_summary': (
                    'Registration should not cost you money. You should get a number '
                    'and be able to see your name on the displayed register.'
                ),
                'tags': ['registration', 'free', 'vendor', 'register'],
            },
            {
                'section_number': '19(3), 19(5)(c)',
                'section_title': 'Elected department heads settle disputes',
                'text': (
                    'Verified plain-language extract (not a verbatim quote): the Act '
                    'provides for elected heads of market departments and gives them '
                    'functions including settlement of disputes.'
                ),
                'plain_language_summary': (
                    'Market disputes should first be handled by the elected department '
                    'heads.'
                ),
                'tags': ['dispute', 'committee', 'vendor'],
            },
            {
                'section_number': '21',
                'section_title': 'Allocation of stalls',
                'text': (
                    'Verified plain-language extract (not a verbatim quote): an '
                    'allocation committee allocates spaces, shops, pitches and stalls. '
                    'Existing registered vendors have priority. A vendor may not hold '
                    'more than one stall and subletting without authorisation requires '
                    'the vendor to vacate.'
                ),
                'plain_language_summary': (
                    'A committee decides who gets a stall, existing registered vendors '
                    'are considered first, you can hold only one stall, and you need '
                    'permission to sublet.'
                ),
                'tags': ['allocation', 'stall', 'vendor', 'subletting'],
            },
            {
                'section_number': '22',
                'section_title': 'Abandonment of a stall',
                'text': (
                    'Verified plain-language extract (not a verbatim quote): a stall '
                    'may be treated as abandoned if it is unoccupied for three months '
                    'or the vendor is in default of market fees for three months.'
                ),
                'plain_language_summary': (
                    'Keep your stall in use and keep up with fees. Three months empty '
                    'or three months in default can lead to the stall being treated as '
                    'abandoned.'
                ),
                'tags': ['abandonment', 'fees', 'stall', 'eviction'],
            },
            {
                'section_number': '24(1), 24(2)',
                'section_title': 'Market fees are displayed',
                'text': (
                    'Verified plain-language extract (not a verbatim quote): market '
                    'fees are set by the administrative authority and must be displayed.'
                ),
                'plain_language_summary': (
                    'You should be able to see the official fee list and should get a '
                    'receipt for every payment.'
                ),
                'tags': ['fees', 'receipt', 'vendor'],
            },
            {
                'section_number': '26(2)-(5)',
                'section_title': 'Seizure and sale of goods',
                'text': (
                    'Verified plain-language extract (not a verbatim quote): goods may '
                    'be seized and sold after 14 days, any surplus must be reimbursed '
                    'to the vendor, and the allocation may be reallocated.'
                ),
                'plain_language_summary': (
                    'If goods are seized, the law sets a process. Ask for a written '
                    'inventory and what happens to any money left after costs.'
                ),
                'tags': ['seizure', 'goods', 'surplus', 'vendor'],
            },
            {
                'section_number': '32',
                'section_title': 'Designated trading areas',
                'text': (
                    'Verified plain-language extract (not a verbatim quote): selling '
                    'outside the designated space and in pathways or drains is '
                    'prohibited.'
                ),
                'plain_language_summary': (
                    'Trade from the space allocated to you and do not block walkways '
                    'or drains.'
                ),
                'tags': ['trading space', 'pathways', 'drains', 'vendor'],
            },
        ],
    },
    {
        'title': 'Local Governments (Kampala City) (Street Traders) Byelaws, S.I. 243-23',
        'short_title': 'Kampala Street Traders Byelaws',
        'instrument_number': 'S.I. No. 243-23',
        'category': 'bylaw',
        'subject': 'local_gov',
        'issuing_authority': 'Kampala Capital City Authority',
        'publication_date': '2023-01-01',
        'source_url': 'https://kcca.go.ug/uploads/acts/Kampala%20Street%20Traders%20By-laws.pdf',
        'version_or_amendment': 'Made under section 39 of the Local Governments Act',
        'legal_status': 'in_force',
        'summary': (
            'KCCA rules for certain named street trading activities in Kampala, '
            'including permits and their conditions.'
        ),
        'full_text': (
            'VERIFIED PLAIN-LANGUAGE EXTRACTS — not a verbatim copy of the Byelaws.\n\n'
            'Byelaw 3: prohibits street trading without a permit.\n\n'
            'Byelaw 6: a permit may not be let or hired out and must be produced on '
            'demand.\n\n'
            'Byelaw 8: provides for cancellation of a permit.\n\n'
            'Scope: these Byelaws cover specific street trader activities listed by '
            'KCCA. They are not a general rule for every market stall. See the official '
            'PDF for the exact activities and wording.'
        ),
        'verification_notes': (
            'Checked against the KCCA PDF. Included for Kampala street traders only; '
            'do not apply it to other districts or to market stalls generally.'
        ),
        'provisions': [
            {
                'section_number': '3',
                'section_title': 'Permit required for street trading',
                'text': (
                    'Verified plain-language extract (not a verbatim quote): street '
                    'trading without a permit is prohibited under these Kampala Byelaws.'
                ),
                'plain_language_summary': (
                    'In Kampala, the street trading activities covered by these '
                    'Byelaws need a permit.'
                ),
                'tags': ['permit', 'street trader', 'Kampala'],
            },
            {
                'section_number': '6, 8',
                'section_title': 'Permit conditions and cancellation',
                'text': (
                    'Verified plain-language extract (not a verbatim quote): a permit '
                    'may not be let or hired out, must be produced on demand, and may '
                    'be cancelled under the Byelaws.'
                ),
                'plain_language_summary': (
                    'You must carry your permit and show it when asked, and you cannot '
                    'lend it to someone else.'
                ),
                'tags': ['permit', 'cancellation', 'Kampala'],
            },
        ],
    },
]


SAMPLE_REFERRALS = [
    {
        'name': 'Uganda Law Society',
        'acronym': 'ULS',
        'description': (
            'The professional body for lawyers in Uganda. '
            'Provides referrals to qualified legal professionals and information on legal services.'
        ),
        'service_type': 'general_legal_aid',
        'district': 'Kampala',
        'physical_address': 'ULS House, Plot 10 Hannington Road, Kampala',
        'phone_number': '+256 414 259 808',
        'website': 'https://www.uls.or.ug',
        'is_free': False,
        'eligibility': 'Open to all. Referrals to member advocates.',
        'consultation_info': 'Contact ULS for referral to a qualified advocate in your area.',
    },
    {
        'name': 'FIDA Uganda',
        'acronym': 'FIDA',
        'description': (
            'Federation of Women Lawyers in Uganda. '
            'Provides free legal aid for women and families, including market vendor issues.'
        ),
        'service_type': 'women_family',
        'district': 'Kampala',
        'physical_address': 'Plot 13 Nkrumah Road, Kampala',
        'phone_number': '+256 414 530 848',
        'website': 'https://www.fidauganda.org',
        'is_free': True,
        'eligibility': 'Primarily women and families. Low-income individuals prioritised.',
        'consultation_info': 'Walk-in and phone consultations available. No appointment required for initial advice.',
    },
    {
        'name': 'Legal Aid Service Providers Network',
        'acronym': 'LASPNET',
        'description': (
            'A network of legal aid providers across Uganda. '
            'Can help locate the nearest legal aid service in your district.'
        ),
        'service_type': 'general_legal_aid',
        'district': 'National',
        'physical_address': 'Kampala (network across Uganda)',
        'phone_number': '',
        'website': 'https://www.laspnet.org',
        'is_free': True,
        'eligibility': 'Low-income individuals. Eligibility criteria vary by member organisation.',
        'consultation_info': 'Contact LASPNET to find the nearest legal aid provider in your district.',
    },
]


class Command(BaseCommand):
    help = (
        'Seeds verified plain-language extracts from published Ugandan laws, '
        'plus legal aid referrals, for development/demo use.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--index',
            action='store_true',
            help='Also index sources into ChromaDB after seeding.',
        )
        parser.add_argument(
            '--if-empty',
            action='store_true',
            help='Seed only when no legal sources exist (safe for every boot on ephemeral hosting).',
        )

    def handle(self, *args, **options):
        if options['if_empty'] and LegalSource.objects.exists():
            self.stdout.write('Legal sources already present — skipping seed.')
            return

        self.stdout.write(self.style.WARNING(
            '\nVerified extracts: these are plain-language summaries of published '
            'Ugandan law, not verbatim Acts. Check the linked official PDF before '
            'relying on a section.\n'
        ))

        verified_at = timezone.now()

        for source_data in VERIFIED_SOURCES:
            data = {k: v for k, v in source_data.items() if k != 'provisions'}
            provisions_data = source_data['provisions']
            data.setdefault('status', 'approved')
            data.setdefault('is_sample', False)
            data['last_verified_at'] = verified_at

            source, created = LegalSource.objects.update_or_create(
                title=data['title'],
                defaults=data,
            )

            action = 'Created' if created else 'Updated'
            self.stdout.write(f'  {action}: {source.title}')

            for prov_data in provisions_data:
                LegalProvision.objects.update_or_create(
                    source=source,
                    section_number=prov_data['section_number'],
                    defaults=prov_data,
                )

            if options['index']:
                from legal_data.vector_store import index_legal_source
                ids = index_legal_source(source)
                if ids:
                    source.is_indexed = True
                    source.indexed_at = timezone.now()
                    source.chroma_doc_ids = ids
                    source.save()
                    self.stdout.write(f'    → Indexed {len(ids)} chunks into ChromaDB')

        from referrals.models import LegalAidOrganisation
        for ref_data in SAMPLE_REFERRALS:
            org, created = LegalAidOrganisation.objects.update_or_create(
                name=ref_data['name'],
                defaults={
                    **ref_data,
                    'is_verified': True,
                    'is_active': True,
                    'last_verified_at': timezone.now(),
                }
            )
            action = 'Created' if created else 'Updated'
            self.stdout.write(f'  {action} referral: {org.name}')

        self.stdout.write(self.style.SUCCESS(
            '\n✓ Verified extracts and referrals seeded. '
            'Run with --index to also load into ChromaDB for RAG retrieval.\n'
        ))
