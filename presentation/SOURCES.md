# LegalBridge judge deck — sources

Every factual claim in `LegalBridge_Judge_Deck.pptx` maps to a published source
below. No district stations, bail figures, contact persons or legal claims were
invented. Checked 25 Nov 2026.

## Boda boda / pre-trial detention story (slides 1–3)

| Claim used | Source | URL |
|---|---|---|
| **12,217 motorcycles** impounded nationwide in six days (7–12 Nov 2022); **10,167** express-penalty tickets; **2,050** motorcycles still pending at stations — figures given by Traffic Police spokesperson Faridah Nampiima | The Source, “12,217 Boda-bodas impounded country-wide during police crackdown,” 14 Nov 2022 (also Daily Monitor, 15 Nov 2022) | https://thesource.co.ug/national/12217-boda-bodas-impounded-country-wide-during-police-crackdown · https://www.monitor.co.ug/uganda/news/national/police-impound-more-than-12-000-boda-motorcycles-4020670 |
| **787 riders** stopped in the week 7–13 Jul 2024 for riding without helmets/reflective jackets; police said operations would continue; unclaimed motorcycles with no case under inquiry were sitting at stations and owners were told to bring relevant documents | Uganda Police Force, “Traffic Police Urges Owners to Reclaim Impounded Motorcycles,” 15 Jul 2024 | https://upf.go.ug/traffic-police-urges-owners-to-reclaim-impounded-motorcycles/ |
| Police position that motorcycles in custody are released to claimants on proof of ownership and after checking they are not linked to crime | Uganda Police Force official X post, Jul 2024 | https://x.com/PoliceUg/status/1813149997157736895 |
| High Court ordered **UGX 225 million** compensation for an unlawful impoundment after the owner was never told why his vehicle was held and a 2013 release order was not honoured | Business Focus, “Gov't to Pay Shs 225m for Vehicle Illegally Impounded by Police,” 25 Jun 2021 | https://businessfocus.co.ug/govt-to-pay-shs-225m-for-vehicle-illegally-impounded-by-police/ |
| **37,188** people in pre-trial/remand imprisonment in Aug 2026 = **44.9%** of Uganda's prison population; total population **82,734**; official capacity **23,437**; occupancy **353%** | World Prison Brief (Institute for Crime & Justice Policy Research, Birkbeck), Uganda country page, Aug 2026 data | https://prisonstudies.org/country/uganda |
| **46.2%** of over 79,000 prisoners on pre-trial detention (= 36,498); **65%** of detainees interviewed spent more than six months on remand without trial; **10.3%** of interviewees were boda-boda riders before arrest; two-thirds knew about bail but only **7%** applied; **98%** of households lost income | New Vision, “Pre-trial detention taking heavy toll on families — study,” 29 Oct 2026, reporting the ASF / LASPNET study *Beyond the Cell: The Hidden Socio-Economic Costs of Pre-Trial Detention in Uganda* | https://newvision.co.ug/category/news/pre-trial-detention-taking-heavy-toll-on-fami-NV_243433_112026 |
| Example of prolonged pre-trial detention of a rider: **David Kato**, 24, held at Kitalya for **4 years 11 months** without trial | Daily Monitor commentary, “Presumed guilty: Pre-trial detention crisis in Uganda” | https://monitor.co.ug/uganda/oped/commentary/presumed-guilty-pre-trial-detention-crisis-in-uganda-5184644 |
| **Article 23**: a person must be brought to court within **48 hours** of arrest; **Article 28**: right to a fair, speedy and public hearing. ULII decisions record that detention beyond 48 hours is false imprisonment and the State is liable | Constitution of the Republic of Uganda (ULII) and ULII “Arrest and detention” case topic | https://ulii.org/akn/ug/act/statute/1995/constitution/eng@2023-12-31 · https://ulii.org/en/judgments/topics/67096/ |

## Access-to-justice and inclusion context (slides 2, 6)

| Claim used | Source | URL |
|---|---|---|
| Uganda ranked **126 / 142** overall and **115 / 142** on civil justice, WJP Rule of Law Index 2024 | World Justice Project — Uganda 2024 | https://worldjusticeproject.org/rule-of-law-index/country/2024/Uganda · https://worldjusticeproject.org/rule-of-law-index/factors/2024/Uganda |
| SDG target **16.3** (equal access to justice) and indicator **16.3.3**; metadata lists lack of knowledge, advice, distance and cost as barriers | UN Statistics Division — SDG 16.3.3 metadata | https://unstats.un.org/sdgs/metadata/files/Metadata-16-03-03.pdf |
| USSD works on basic and feature phones, needs no smartphone app or mobile data, and works across GSM networks | GSMA Mobile for Development — “Low Tech, High Impact: USSD in the time of COVID-19” | https://www.gsma.com/solutions-and-impact/connectivity-for-good/mobile-for-development/uncategorized/low-tech-high-impact-ussd-in-the-time-of-covid-19/ |

## Photographs used (real, published, credited on-slide)

| Slide | Image used | Caption / credit | Source URL |
|---|---|---|---|
| 2 | `assets/10-police-operation.jpg` | “Police officers engage boda boda riders during the ongoing operation in Kampala on November 8, 2022.” PHOTO/ISAAC KASAMANI · DAILY MONITOR | https://www.monitor.co.ug/uganda/news/national/police-impound-more-than-12-000-boda-motorcycles-4020670 |
| 3 | `assets/11-impounded-motorcycles.jpg` | “Some of the impounded motorcycles parked at the Central Police Station Kampala recently.” PHOTO \| STEPHEN OTAGE · DAILY MONITOR, 18 Jul 2024 | https://monitor.co.ug/uganda/news/national/police-ask-owners-of-rotting-motorcycles-to-pick-them-4694052 |

These are downloaded published press photographs, credited visibly on the slides.
If the deck will be distributed publicly rather than shown to judges, clear
reuse rights with Daily Monitor / Nation Media Group first.

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

- **No daily national arrest figure is claimed.** No official published daily
  count of boda boda arrests exists; the deck uses documented operations
  (12,217 impounded in six days; 787 riders in one week) instead.
- No accusation that any rider is a thief, and no invented police stations,
  bail amounts, contact persons or case outcomes.
- No claim that LegalBridge is a lawyer, a court, or a substitute for legal advice.
- No measured user outcomes; pilot metrics are presented as future work.
- No Figma images: all solution screenshots come from the live hosted product.
