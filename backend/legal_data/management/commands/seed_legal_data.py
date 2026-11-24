"""
Management command: python manage.py seed_legal_data
Seeds the database with SAMPLE legal source records for development/demo.
These are labelled as SAMPLE DATA and reference real Ugandan laws by name,
but the full text is placeholder text — do NOT use in production.
In production, add verified full-text documents through the admin panel.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from legal_data.models import LegalSource, LegalProvision
from legal_data.vector_store import index_legal_source


SAMPLE_SOURCES = [
    {
        'title': 'Traffic and Road Safety Act, Cap 361 (Uganda)',
        'short_title': 'Traffic & Road Safety Act',
        'category': 'act',
        'subject': 'traffic',
        'issuing_authority': 'Parliament of Uganda',
        'publication_date': '1998-01-01',
        'source_url': 'https://ulii.org/ug/legislation/act/1998/15',
        'summary': (
            'The Traffic and Road Safety Act governs the use of public roads in Uganda, '
            'including licensing of drivers and vehicles, traffic offences, penalties, '
            'and enforcement procedures.'
        ),
        'full_text': (
            '[SAMPLE DATA — Replace with verified full text from ULII]\n\n'
            'Traffic and Road Safety Act, Cap 361\n\n'
            'Section 1 — Interpretation\n'
            'In this Act, unless the context otherwise requires: '
            '"driver" means a person who drives or is in charge of a vehicle; '
            '"motor vehicle" means any mechanically propelled vehicle; '
            '"motorcycle" includes any two-wheeled motor vehicle.\n\n'
            'Section 118 — Driving without a licence\n'
            'A person who drives a motor vehicle on a road without holding a valid '
            'driving permit commits an offence and is liable on conviction to a fine '
            'not exceeding two currency points or imprisonment for a term not exceeding '
            'six months or both.\n\n'
            'Section 120 — Penalty for riding a motorcycle without a helmet\n'
            'A person who rides a motorcycle or is a passenger on a motorcycle without '
            'wearing a protective helmet commits an offence.\n\n'
            'Section 125 — Powers of police officers\n'
            'A police officer in uniform may stop any vehicle on a road and may require '
            'the driver to produce their driving permit, certificate of insurance, '
            'and certificate of fitness.\n\n'
            'Section 130 — Penalty notices\n'
            'Where a police officer has reason to believe that a person has committed '
            'a traffic offence, the officer may issue a fixed penalty notice. '
            'The notice shall specify the alleged offence, the amount of the penalty, '
            'and the period within which payment must be made.\n\n'
            '[NOTE: This is sample text for development. Add verified full text from '
            'Uganda Legal Information Institute (ULII) at ulii.org before production.]'
        ),
        'provisions': [
            {
                'section_number': '118',
                'section_title': 'Driving without a licence',
                'text': (
                    'A person who drives a motor vehicle on a road without holding a valid '
                    'driving permit commits an offence and is liable on conviction to a fine '
                    'not exceeding two currency points or imprisonment for a term not exceeding '
                    'six months or both. [SAMPLE — verify at ULII]'
                ),
                'plain_language_summary': (
                    'Driving without a valid licence is an offence under Ugandan law. '
                    'The penalty may include a fine or imprisonment. '
                    'Always carry your driving permit when operating a vehicle.'
                ),
                'tags': ['licence', 'driving permit', 'offence', 'motorcycle', 'boda boda'],
            },
            {
                'section_number': '125',
                'section_title': 'Powers of police officers to stop vehicles',
                'text': (
                    'A police officer in uniform may stop any vehicle on a road and may require '
                    'the driver to produce their driving permit, certificate of insurance, '
                    'and certificate of fitness. [SAMPLE — verify at ULII]'
                ),
                'plain_language_summary': (
                    'A uniformed police officer has the legal authority to stop your vehicle '
                    'and ask to see your driving permit, insurance certificate, and roadworthiness '
                    'certificate. You are legally required to produce these documents when asked.'
                ),
                'tags': ['police', 'stop', 'vehicle check', 'documents', 'boda boda'],
            },
            {
                'section_number': '130',
                'section_title': 'Fixed penalty notices',
                'text': (
                    'Where a police officer has reason to believe that a person has committed '
                    'a traffic offence, the officer may issue a fixed penalty notice specifying '
                    'the alleged offence, the penalty amount, and the payment deadline. '
                    '[SAMPLE — verify at ULII]'
                ),
                'plain_language_summary': (
                    'If an officer believes you have committed a traffic offence, they can give '
                    'you an official penalty notice. This notice should state what the offence is, '
                    'how much the penalty is, and when you must pay. '
                    'An allegation in a notice does not automatically mean you are guilty.'
                ),
                'tags': ['penalty notice', 'fine', 'traffic offence', 'payment'],
            },
        ],
    },
    {
        'title': 'Markets Act, 2023 (Uganda)',
        'short_title': 'Markets Act 2023',
        'category': 'act',
        'subject': 'markets',
        'issuing_authority': 'Parliament of Uganda',
        'publication_date': '2023-01-01',
        'source_url': 'https://ulii.org/ug/legislation',
        'summary': (
            'The Markets Act 2023 governs the establishment, management and operation '
            'of markets in Uganda, including the rights of market vendors, '
            'allocation of market spaces, and dispute resolution procedures.'
        ),
        'full_text': (
            '[SAMPLE DATA — Replace with verified full text from ULII or official gazette]\n\n'
            'Markets Act, 2023\n\n'
            'Section 1 — Interpretation\n'
            '"market" means any place established by a local government authority or '
            'private operator for the purpose of buying and selling goods; '
            '"vendor" means a person allocated a market stall or space for the purpose '
            'of trading; '
            '"allocation" means the assignment of a market stall or space to a vendor '
            'by the market authority.\n\n'
            'Section 15 — Allocation of market stalls\n'
            'The market authority shall issue an allocation document to each vendor '
            'assigned a market stall. The allocation document shall specify the stall '
            'number, the period of allocation, and any conditions attached.\n\n'
            'Section 20 — Payment of market fees\n'
            'Every vendor shall pay the prescribed market fees as set by the relevant '
            'local government authority. The authority shall issue an official receipt '
            'upon payment of any fees.\n\n'
            'Section 25 — Termination of allocation\n'
            'An allocation may be terminated by the market authority where: '
            '(a) the vendor fails to pay fees for a prescribed period; '
            '(b) the vendor breaches conditions of the allocation; '
            '(c) the market is relocated or redeveloped. '
            'The market authority shall give reasonable written notice before '
            'terminating an allocation.\n\n'
            'Section 26 — Right of vendors to written notice\n'
            'A vendor whose allocation is proposed to be terminated has the right to '
            'receive written notice specifying the reason for termination and the '
            'deadline by which they must vacate. The vendor shall have the opportunity '
            'to respond before the termination takes effect.\n\n'
            'Section 30 — Dispute resolution\n'
            'Disputes between vendors and market authorities may be referred to the '
            'relevant local government dispute resolution mechanism or to the courts.\n\n'
            '[NOTE: This is sample text for development. Add verified full text before '
            'production deployment. Verify current status of this Act.]'
        ),
        'provisions': [
            {
                'section_number': '15',
                'section_title': 'Allocation of market stalls',
                'text': (
                    'The market authority shall issue an allocation document to each vendor. '
                    'The allocation document shall specify the stall number, the period of '
                    'allocation, and any conditions attached. [SAMPLE — verify]'
                ),
                'plain_language_summary': (
                    'When you are given a market stall, the market authority should give you '
                    'an official allocation document. This document should show your stall number, '
                    'how long the allocation lasts, and any rules you must follow. '
                    'Keep this document safe — it is evidence that you were assigned the stall.'
                ),
                'tags': ['allocation', 'market stall', 'vendor', 'document', 'assignment'],
            },
            {
                'section_number': '25',
                'section_title': 'Termination of allocation — when and how',
                'text': (
                    'An allocation may be terminated where the vendor fails to pay fees, '
                    'breaches conditions, or the market is relocated. The market authority '
                    'shall give reasonable written notice before terminating. [SAMPLE — verify]'
                ),
                'plain_language_summary': (
                    'The market authority may end your allocation if you have not paid fees, '
                    'if you have broken the rules of your allocation, or if the market is being '
                    'moved or rebuilt. However, they must give you reasonable written notice first. '
                    'You should not be removed without prior written notice.'
                ),
                'tags': ['eviction', 'termination', 'allocation', 'notice', 'written notice', 'vendor rights'],
            },
            {
                'section_number': '26',
                'section_title': 'Right to written notice before termination',
                'text': (
                    'A vendor whose allocation is proposed to be terminated has the right to '
                    'receive written notice specifying the reason and deadline, and the '
                    'opportunity to respond. [SAMPLE — verify]'
                ),
                'plain_language_summary': (
                    'If the market authority wants to end your allocation, you have the right '
                    'to receive a written notice that explains the reason and gives you a '
                    'deadline. You also have the right to respond before the decision is final. '
                    'An eviction without written notice may not follow the proper procedure.'
                ),
                'tags': ['written notice', 'eviction', 'vendor rights', 'right to respond', 'procedure'],
            },
            {
                'section_number': '30',
                'section_title': 'Dispute resolution',
                'text': (
                    'Disputes between vendors and market authorities may be referred to the '
                    'local government dispute resolution mechanism or to the courts. [SAMPLE — verify]'
                ),
                'plain_language_summary': (
                    'If you have a dispute with the market authority, you can take it to the '
                    'local government dispute resolution process or to court. '
                    'Consider seeking help from a legal aid organisation before going to court.'
                ),
                'tags': ['dispute', 'appeal', 'court', 'local government', 'vendor'],
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
        'Seeds the database with SAMPLE legal sources and referrals for development/demo. '
        'Replace sample text with verified full text before production.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--index',
            action='store_true',
            help='Also index sources into ChromaDB after seeding.',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING(
            '\n⚠  SAMPLE DATA: These legal sources use placeholder text. '
            'Replace with verified full text from ULII before production.\n'
        ))

        # Seed legal sources
        for source_data in SAMPLE_SOURCES:
            provisions_data = source_data.pop('provisions', [])
            pub_date = source_data.pop('publication_date', None)

            source, created = LegalSource.objects.update_or_create(
                title=source_data['title'],
                defaults={
                    **source_data,
                    'publication_date': pub_date,
                    'status': 'approved',
                    'last_verified_at': timezone.now(),
                    'verification_notes': 'SAMPLE DATA — not verified for production use.',
                }
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

        # Seed referral organisations
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
            '\n✓ Sample data seeded. '
            'Run with --index to also load into ChromaDB for RAG retrieval.\n'
            'Replace sample text with verified sources before demo/production.\n'
        ))
