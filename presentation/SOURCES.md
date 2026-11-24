# LegalBridge judge deck — sources

Every factual claim in `LegalBridge_Judge_Deck.pptx` maps to a published source
below. No district offices, section numbers, contact persons or legal claims were
invented. Checked 25 Nov 2026.

| Slide | Claim used | Source | URL |
|---|---|---|---|
| 2 | Uganda ranked **126 / 142** overall and **115 / 142** on civil justice, WJP Rule of Law Index 2024 | World Justice Project — Uganda 2024 country insights | https://worldjusticeproject.org/rule-of-law-index/country/2024/Uganda |
| 2 | Same WJP ranking, with factor methodology (civil justice measures accessibility, affordability, delay, enforcement) | World Justice Project — Factors 2024, Uganda | https://worldjusticeproject.org/rule-of-law-index/factors/2024/Uganda |
| 2 | Backlog fell from **26.3% (FY2023/24)** to **24.2% (FY2024/25)**, but **46,000+ cases** still pending | Judiciary of Uganda, “Judiciary Launches Digital Tool to Boost Efficiency, Transparency, and Accountability,” 17 Oct 2025 | https://judiciary.go.ug/data/news/1738/31609/Judiciary%20Launches%20Digital%20Tool%20to%20Boost%20Efficiency,%20Transparency,%20and%20Accountability.html |
| 2, 3, 6 | SDG target **16.3**: equal access to justice for all; indicator **16.3.3** counts people who accessed formal or informal dispute resolution. Metadata lists lack of knowledge, advice, distance and cost as barriers | UN Statistics Division — SDG indicator 16.3.3 metadata (updated 2023-03-31) | https://unstats.un.org/sdgs/metadata/files/Metadata-16-03-03.pdf |
| 3, 6 | Constitution of Uganda **Article 28**: right to a fair, speedy and public hearing before an independent court | Uganda Legal Information Institute (ULII), Constitution of the Republic of Uganda | https://ulii.org/akn/ug/act/statute/1995/constitution/eng@2023-12-31 |
| 3, 6 | USSD works on basic and feature phones, needs no smartphone app or internet, and functions across GSM networks; nine in ten mobile-money transactions in Sub-Saharan Africa flow through USSD | GSMA Mobile for Development — “Low Tech, High Impact: USSD in the time of COVID-19” (17 Dec 2020, modified 7 Jan 2026) | https://www.gsma.com/solutions-and-impact/connectivity-for-good/mobile-for-development/uncategorized/low-tech-high-impact-ussd-in-the-time-of-covid-19/ |
| 6 | GSMA research on low-tech channels for the SDGs | GSMA — “Start-ups using USSD to tackle SDGs” | https://www.gsma.com/solutions-and-impact/connectivity-for-good/mobile-for-development/wp-content/uploads/2018/05/Start-ups-using-USSD-to-tackle-SDGs.pdf |

## Product evidence (not external research)

- Live app: https://legalbridge-app-free.onrender.com
- Health-checked API: https://legalbridge-api-free.onrender.com/healthz
- Screen captures in `presentation/assets/` were taken from the hosted app on
  25 Nov 2026 (routes `/onboarding`, `/rights`, `/boda`, `/vendor`, `/ask`,
  `/voice`, `/legal-help`, `/document/upload`, `/language`).
- Rights guides and the official-document manifest in `backend/legal_data/` are
  the source of the “verified sources” claim; English and Luganda are complete,
  Runyankore/Acholi/Lugbara are drafts that fall back to English.

## Deliberate exclusions

- No claim that LegalBridge is a lawyer, a court, or a substitute for legal advice.
- No invented legal-aid office names, phone numbers or coverage figures.
- No claim of measured user outcomes; the deck states pilot metrics as future work.
- No Figma images: all solution screenshots are from the live hosted product.
