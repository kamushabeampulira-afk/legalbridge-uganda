# LegalBridge — Legal Sources

This directory is for storing verified Ugandan legal documents
used by the LegalBridge RAG pipeline.

## ⚠️ Important Notice

- Only add documents obtained from verified, authoritative sources.
- Do NOT commit copyrighted documents without appropriate licensing.
- All documents must be reviewed and approved by an admin before
  they are used in AI responses.
- Documents are loaded into ChromaDB via the Django admin panel.

## Verified Sources to Obtain

| Document | Source | Status |
|----------|--------|--------|
| Traffic and Road Safety Act, Cap 361 | https://ulii.org | Obtain from ULII |
| Markets Act, 2023 | https://ulii.org | Obtain from ULII |
| Employment Act, Cap 219 | https://ulii.org | Obtain from ULII |
| Local Governments Act, Cap 243 | https://ulii.org | Obtain from ULII |
| Data Protection and Privacy Act, 2019 | https://ulii.org | Obtain from ULII |

## Directory Structure

```
legal_sources/
├── README.md
├── sample_docs/          # Sample documents for demos (fictional)
│   ├── sample_traffic_notice.jpg
│   ├── sample_eviction_notice.jpg
│   ├── sample_allocation_slip.jpg
│   └── sample_payment_receipt.jpg
└── raw/                  # Full verified PDFs (gitignored — add locally)
    └── .gitkeep
```

## Adding a Legal Source

1. Obtain the full text from an authoritative source (ULII, Uganda Gazette).
2. Log in to Django admin: http://localhost:8000/admin/
3. Navigate to Legal Data → Legal Sources → Add Legal Source.
4. Fill in:
   - Title (official name of the Act/regulation)
   - Category (act / regulation / bylaw / etc.)
   - Subject (traffic / markets / employment / etc.)
   - Issuing Authority
   - Publication date and Source URL
   - Full text (paste the verified text)
   - Summary (plain-language overview)
5. Set Status to "Pending Review".
6. Have a second admin review and use the "Approve and index" action.
7. The source will be chunked and indexed into ChromaDB.
8. Only then will it appear in AI responses.

## Sample Documents for Demo

Create sample documents in `sample_docs/` with clearly visible labels:
"SAMPLE — FOR DEMONSTRATION ONLY"

Use fictional names and reference numbers.
Do NOT use real people's names or real case numbers.
