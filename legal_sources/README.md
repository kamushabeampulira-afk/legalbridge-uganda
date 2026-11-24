# LegalBridge — Legal Sources

Verified Ugandan legal documents used by the rider and vendor rights guides and
by the RAG pipeline.

## ⚠️ Important notice

- Only documents from authoritative publishers are listed here.
- The `official/` PDFs are the publisher's files. They are **not** edited.
- The in-app guides in `mobile/constants/LegalRights.ts` are plain-language
  explanations with section citations. They are legal information, not legal
  advice, and are not verbatim copies of the law.
- Backend seed extracts in
  `backend/legal_data/management/commands/seed_legal_data.py` are labelled
  "verified plain-language extracts" and link to the official PDF.
- All sources must be reviewed by an admin before being used in AI responses.

## Downloaded official documents

| Local file | Official document | Publisher / source URL |
|------------|-------------------|------------------------|
| `official/markets-act-2023.pdf` | Markets Act, 2023 (Act 7 of 2023) | https://www.bills.parliament.ug/attachments/Markets%20Act,%202023.pdf |
| `official/traffic-road-safety-amendment-act-2020.pdf` | Traffic and Road Safety Act (Amendment) Act, 2020 (Act 6 of 2020) | https://works.go.ug/wp-content/uploads/2026/04/Traffic-Road-Safety-Amendment-Act-2020-FINAL.pdf |
| `official/motorcycles-amendment-regulations-2023.pdf` | Traffic and Road Safety (Motorcycles and Motorised Tricycles) (Amendment) Regulations, 2023 (S.I. 34 of 2023) | https://works.go.ug/wp-content/uploads/2026/04/Traffic-and-Road-Safety-Motorcycles-and-Motorised-Tricycles-Amendment-Regulations-2023.pdf |
| `official/kampala-street-traders-bylaws-2023.pdf` | Local Governments (Kampala City) (Street Traders) Byelaws, S.I. 243-23 | https://kcca.go.ug/uploads/acts/Kampala%20Street%20Traders%20By-laws.pdf |

`official/SHA256SUMS.txt` records the checksums of the downloaded files so a
reviewer can confirm nothing was edited after download.

ULII (`ulii.org` / `media.ulii.org`) is behind a bot challenge and its media
host does not resolve in this environment, so the consolidated base
**Traffic and Road Safety Act, Cap 361** PDF could not be stored locally. The
2020 Amendment Act (Act 6 of 2020) and the 2023 Regulations were downloaded
from the Ministry of Works and Transport instead, and they contain the
provisions used by the guides. To check the unamended base text, use ULII:
https://ulii.org/en/akn/ug/act/1998/15/eng@2020-05-22

The Markets Act 2023 repealed the old Markets Act, Cap 94. The older
`MARKETS-ACT.pdf` on the MTIC website is the 1942 Act and is **not** used.

## Verified provisions used

### Boda boda riders

| Topic | Provision | Source |
|-------|-----------|--------|
| Carry a copy of a valid licence; original within 72 hours | Traffic and Road Safety Act s.146(1), as amended by Act 6 of 2020 | `official/traffic-road-safety-amendment-act-2020.pdf` |
| Carry a copy of the registration book; original within 120 hours | s.146(2) | same |
| Licence must match the vehicle group | s.35(1) (groups in s.36) | same |
| Commercial motorcycles / Class M | s.70(1)(g), s.94(1)(g) | same |
| Using a vehicle without a licence: up to 100 currency points or 1 year | s.105(1), penalty substituted by Act 6 of 2020 | same |
| Demerit points on conviction | s.122A, inserted by Act 6 of 2020 | same |
| Helmets worn, fastened and to UNBS standard | S.I. 30 of 2016 reg. 11(4), (5), (5a) as amended by S.I. 34 of 2023 | `official/motorcycles-amendment-regulations-2023.pdf` |
| Public transport providers entity | S.I. 34 of 2023 regs. 11A–11B | same |

Sections 118 and 130 are **not** used: s.118 was repealed by the 2020
amendment, and s.130 deals with taking a vehicle without the owner's consent,
not fixed penalty notices.

### Market vendors

| Topic | Provision |
|-------|-----------|
| Three months' written notice before layout/design changes | Markets Act 2023 s.16(2) |
| Registration free, registration number, register displayed | s.18(4), (5), (8) |
| Elected department heads handle disputes | s.19(3), 19(5)(c) |
| Allocation committee, priority for existing registered vendors, one stall, no unauthorised subletting | s.21 |
| Abandonment after 3 months unoccupied or 3 months in default of fees | s.22 |
| Market fees set and displayed | s.24(1), (2) |
| Seizure and sale after 14 days, surplus reimbursed, reallocation | s.26(2)–(5) |
| No selling outside designated space, pathways or drains | s.32 |

The KCCA byelaws apply only to the specific street trader activities named by
KCCA in Kampala; they are not a general rule for market stalls.

## Directory structure

```
legal_sources/
├── README.md                 # this manifest
├── official/                 # publisher PDFs (downloaded, unedited)
├── sample_docs/              # fictional demo documents
│   └── README.md
└── raw/                      # full verified text added locally (gitignored)
    └── .gitkeep
```

## Adding a legal source

1. Obtain the document from an authoritative publisher (Parliament, Ministry,
   ULII, KCCA, Uganda Gazette).
2. Record the exact URL and date checked in this README.
3. Log in to Django admin: http://localhost:8000/admin/
4. Add a Legal Source with the official title, instrument number, category,
   issuing authority, publication date, source URL and verified text.
5. Set status to "Pending Review" and have a second admin approve and index it.
6. Only approved, in-force, non-sample sources are presented as current law.

## Sample documents for demo

Create fictional documents in `sample_docs/` with a visible
"SAMPLE — FOR DEMONSTRATION ONLY" label. Do not use real people's names or
real case numbers.
