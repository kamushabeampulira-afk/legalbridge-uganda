/**
 * Bilingual "Know Your Rights" guides for boda boda riders and market vendors.
 *
 * Every statement below is taken from a published Ugandan Act, regulation or
 * byelaw. The citation is shown in the app so users can check the source.
 * This is legal information, not legal advice.
 *
 * Source PDFs are stored in legal_sources/official/ at the repository root.
 * Links open the same documents at their official publisher.
 */

export type Language = 'en' | 'lg';

export interface LocalizedText {
  en: string;
  lg: string;
}

export interface LegalSourceLink {
  label: LocalizedText;
  url: string;
}

export interface LegalRight {
  id: string;
  title: LocalizedText;
  /** What the law actually says, with the section cited. */
  law: LocalizedText;
  /** The same point explained in everyday language. */
  plain: LocalizedText;
  /** Practical steps for the user. */
  steps: LocalizedText[];
  source: LegalSourceLink;
}

export interface LegalDocument {
  id: string;
  title: LocalizedText;
  summary: LocalizedText;
  caution?: LocalizedText;
  url: string;
}

export type RightsCategory = 'boda_boda' | 'market_vendor';

export interface RightsGuide {
  category: RightsCategory;
  title: LocalizedText;
  intro: LocalizedText;
  rights: LegalRight[];
  documents: LegalDocument[];
}

const SOURCE_TRAFFIC_ACT: LegalSourceLink = {
  label: {
    en: 'Traffic and Road Safety Act (Amendment) Act 2020, Act 6 of 2020',
    lg: 'Traffic and Road Safety Act (Amendment) Act 2020, Act 6 of 2020',
  },
  url: 'https://works.go.ug/wp-content/uploads/2026/04/Traffic-Road-Safety-Amendment-Act-2020-FINAL.pdf',
};

const SOURCE_MOTORCYCLE_REGULATIONS: LegalSourceLink = {
  label: {
    en: 'Motorcycles and Motorised Tricycles (Amendment) Regulations, 2023, S.I. 34 of 2023',
    lg: 'Motorcycles and Motorised Tricycles (Amendment) Regulations, 2023, S.I. 34 of 2023',
  },
  url: 'https://works.go.ug/wp-content/uploads/2026/04/Traffic-and-Road-Safety-Motorcycles-and-Motorised-Tricycles-Amendment-Regulations-2023.pdf',
};

const SOURCE_MARKETS_ACT: LegalSourceLink = {
  label: {
    en: 'Markets Act, 2023, Act 7 of 2023',
    lg: 'Markets Act, 2023, Act 7 of 2023',
  },
  url: 'https://www.bills.parliament.ug/attachments/Markets%20Act,%202023.pdf',
};

const SOURCE_KCCA_BYELAWS: LegalSourceLink = {
  label: {
    en: 'Kampala Street Traders Byelaws, S.I. 243-23',
    lg: 'Kampala Street Traders Byelaws, S.I. 243-23',
  },
  url: 'https://kcca.go.ug/uploads/acts/Kampala%20Street%20Traders%20By-laws.pdf',
};

const bodaGuide: RightsGuide = {
  category: 'boda_boda',
  title: {
    en: 'Boda boda riders',
    lg: 'Abavuzi ba boda boda',
  },
  intro: {
    en: 'Ugandan traffic law gives riders duties and protections. Each point below cites the Act or regulation it comes from.',
    lg: 'Amateeka g’ekkubo ga Uganda gali n’obujulizi n’obuwajjiiro bw’omuvuzi. Buli kintu wano kiragira etteeka kye kiva.',
  },
  rights: [
    {
      id: 'boda-documents',
      title: {
        en: 'Carry your licence and registration documents',
        lg: 'Twala layisensi yo n’empapula z’ebidduka',
      },
      law: {
        en: 'Section 146(1) of the Traffic and Road Safety Act, as amended in 2020, says a person driving on a road must carry a copy of a valid driving licence at all times and produce the original within 72 hours when a uniformed police officer asks. Section 146(2) says the same for a copy of the registration book, with the original within 120 hours.',
        lg: 'Ekitundu 146(1) kya Traffic and Road Safety Act, ng’ekyusiddwa mu 2020, kigamba omuntu avuza ku kkubo ateekwa okutwala kopi ya layisensi eneetaasibwa enkanya, n’alaga ey’edda mu ssaawa 72 ng’omusirikale y’akiraba. Ekitundu 146(2) kigamba kikyo ku kopi y’empapula y’ebidduka, n’ey’edda mu ssaawa 120.',
      },
      plain: {
        en: 'You do not have to carry the original licence every day, but you must carry a copy. If an officer asks, show the original licence within 3 days (72 hours) and the original registration book within 5 days (120 hours).',
        lg: 'Si ky’eetaagibwa kutwala ey’edda buli lunaku, naye oteekwa okutwala kopi. Ng’omusirikale akubuuza, laga layisensi ey’edda mu nnaku 3 (ssaawa 72) n’empapula y’ebidduka ey’edda mu nnaku 5 (ssaawa 120).',
      },
      steps: [
        {
          en: 'Keep a clear copy or photo of your licence and the motorcycle registration book.',
          lg: 'Kubika kopi etegeerekeka oba ekifaananyi kya layisensi yo n’empapula y’ebidduka.',
        },
        {
          en: 'If asked for the original, take it to the police station within the time the law allows.',
          lg: 'Ng’obasuubizibwa ey’edda, gitwale ku ofiisi ya poliisi mu kiseera amateeka kye gakuwa.',
        },
        {
          en: 'Write down the officer’s name, station, and the section of the law on any notice you receive.',
          lg: 'Wandiika erinnya ly’omusirikale, ofiisi ye, n’ekitundu ky’amateeka ekiri ku bubaka bwe bakuwa.',
        },
      ],
      source: SOURCE_TRAFFIC_ACT,
    },
    {
      id: 'boda-licence-class',
      title: {
        en: 'Your licence must match the motorcycle you ride',
        lg: 'Layisensi yo erina okukwatagana n’ebidduka by’ovuza',
      },
      law: {
        en: 'Section 35(1) of the Traffic and Road Safety Act requires a person to hold a valid licence for the group of vehicle they drive. Section 36 sets out licence groups, and sections 70(1)(g) and 94(1)(g) deal with licences for commercial motorcycles and tricycles, including Class M.',
        lg: 'Ekitundu 35(1) kya Traffic and Road Safety Act kikwata ku kubeera n’layisensi eneetaasibwa ey’ekika ky’ebidduka by’ovuza. Ekitundu 36 kilaga ebika by’amayisensi, ate ebitundu 70(1)(g) ne 94(1)(g) bikwata ku layisensi z’ebidduka by’okubaga abantu, okugattako Class M.',
      },
      plain: {
        en: 'A licence for one group of vehicles does not automatically cover another. If you carry passengers for payment, check that the class printed on your licence covers that kind of work.',
        lg: 'Layisensi ey’ekika kimu tejjanga kukwata ku kkirala. Ng’osutula abantu ku ssente, kebera nga ekika ekiri ku layisensi yo kikwata ku mulimu ogwo.',
      },
      steps: [
        {
          en: 'Check the class printed on your licence.',
          lg: 'Kebera ekika ekiri ku layisensi yo.',
        },
        {
          en: 'Do not ride for hire if your licence does not cover that class.',
          lg: 'Tokubaga bantu ku ssente singa layisensi yo tekwata ku kika kino.',
        },
        {
          en: 'Ask the licensing office or a legal aid provider if you are unsure.',
          lg: 'Buuza ofiisi evuga amayisensi oba omuwagizi w’amateeka ng’otamanyi.',
        },
      ],
      source: SOURCE_TRAFFIC_ACT,
    },
    {
      id: 'boda-helmet',
      title: {
        en: 'Wear a proper helmet, fastened',
        lg: 'Funa enkufiira ennungi era ogisibe bulungi',
      },
      law: {
        en: 'Regulation 11 of the Traffic and Road Safety (Motorcycles and Motorised Tricycles) Regulations, 2016 (S.I. 30 of 2016), as amended by S.I. 34 of 2023, requires helmets to be worn and properly fastened. The 2023 amendment also requires helmets to meet Uganda National Bureau of Standards requirements.',
        lg: 'Ekitundu 11 kya Traffic and Road Safety (Motorcycles and Motorised Tricycles) Regulations, 2016 (S.I. 30 of 2016), ng’ekyusiddwa S.I. 34 of 2023, kigamba enkufiira zirina okusibibwa bulungi. Ekyusiddwa mu 2023 kigattako nti enkufiira zirina okutuukana n’ebipimo bya Uganda National Bureau of Standards.',
      },
      plain: {
        en: 'The helmet must be on your head and properly strapped, not just carried with you. It should meet the UNBS standard. The passenger also needs a helmet.',
        lg: 'Enkufiira erina okuba ku mutwe n’okusibibwa bulungi, si kugitwala yokka. Erina okutuukana n’ekipimo kya UNBS. N’omuntu gy’osutula ateekwa okuba n’enkufiira.',
      },
      steps: [
        {
          en: 'Fasten the strap before every trip.',
          lg: 'Siba enkufiira bulungi nga tonnabanga kugenda.',
        },
        {
          en: 'Use a helmet that meets the UNBS standard.',
          lg: 'Kozesa enkufiira etuukana n’ekipimo kya UNBS.',
        },
        {
          en: 'Ask your passenger to wear one too.',
          lg: 'Saba n’omuntu gy’osutula okwambala enkufiira.',
        },
      ],
      source: SOURCE_MOTORCYCLE_REGULATIONS,
    },
    {
      id: 'boda-demerit',
      title: {
        en: 'Traffic convictions can be recorded against your licence',
        lg: 'Omusango gw’ekkubo gusobola okuweerereza ku layisensi yo',
      },
      law: {
        en: 'Section 122A, inserted by the Traffic and Road Safety Act (Amendment) Act 2020, allows the Minister to make regulations on a demerit points system. Those regulations provide for offences to be grouped by seriousness and for points to be recorded against a licence held by that person.',
        lg: 'Ekitundu 122A, ekyayongerwa Traffic and Road Safety Act (Amendment) Act 2020, kikkiriza Minisita okuteeka amateeka ag’obubonero bw’emisango (demerit points). Amateeka ago galaga ebika by’emisango n’obubonero obuweererezebwa ku layisensi y’omuntu.',
      },
      plain: {
        en: 'If you are convicted of some traffic offences, points can be recorded against your licence. Take every written notice seriously and get advice before pleading guilty.',
        lg: 'Ng’osangibwa omusango ogumu ku ekkubo, obubonero busobola okuweererezebwa ku layisensi yo. Tosuusuza bubaka bwonna, era noonya obuyambi nga tonnasasula.',
      },
      steps: [
        {
          en: 'Ask for a written notice stating the exact offence and the law cited.',
          lg: 'Saba obubaka obuwandiikiddwa obulaga omusango n’etteeka erikuwakirira.',
        },
        {
          en: 'Keep the notice and any official receipt safely.',
          lg: 'Kubika obubaka ne resiti ey’esigika bulungi.',
        },
        {
          en: 'Ask a legal aid provider what the notice means before you pay or plead guilty.',
          lg: 'Buuza omuwagizi w’amateeka kye kitegeza nga tonnasasula.',
        },
      ],
      source: SOURCE_TRAFFIC_ACT,
    },
  ],
  documents: [
    {
      id: 'doc-markets-act',
      title: {
        en: 'Markets Act, 2023',
        lg: 'Markets Act, 2023',
      },
      summary: {
        en: 'The current Ugandan law on public and private markets, vendor registration, stall allocation, fees and disputes.',
        lg: 'Etteeka lya Uganda erikwata ku katale, okuweebwa kwa basuubuzi, essimbi, n’obutakaayanwa.',
      },
      url: SOURCE_MARKETS_ACT.url,
    },
    {
      id: 'doc-traffic-amendment',
      title: {
        en: 'Traffic and Road Safety Act (Amendment) Act, 2020',
        lg: 'Traffic and Road Safety Act (Amendment) Act, 2020',
      },
      summary: {
        en: 'Amends the Traffic and Road Safety Act: licence documents, demerit points, offences and penalties.',
        lg: 'Ekyusa Traffic and Road Safety Act: empapula z’obuvuzi, obubonero bw’emisango, n’emisango.',
      },
      url: SOURCE_TRAFFIC_ACT.url,
    },
    {
      id: 'doc-motorcycle-regulations',
      title: {
        en: 'Motorcycles and Motorised Tricycles (Amendment) Regulations, 2023',
        lg: 'Motorcycles and Motorised Tricycles (Amendment) Regulations, 2023',
      },
      summary: {
        en: 'Amends the 2016 motorcycle regulations, including helmet rules and public transport provider rules.',
        lg: 'Ekyusa amateeka g’ebidduka ega 2016, okugattako eby’enkufiira n’abagaba obuvuzi bw’abantu.',
      },
      url: SOURCE_MOTORCYCLE_REGULATIONS.url,
    },
    {
      id: 'doc-kcca-bylaws',
      title: {
        en: 'Kampala Street Traders Byelaws, S.I. 243-23',
        lg: 'Kampala Street Traders Byelaws, S.I. 243-23',
      },
      summary: {
        en: 'KCCA rules for certain named street trading activities in Kampala.',
        lg: 'Amateeka ga KCCA ku bimu ku bikolwa by’obusuubuzi ku nguudo mu Kampala.',
      },
      caution: {
        en: 'Applies only to specific street trader activities in Kampala — not to every market stall.',
        lg: 'Ekwata ku bimu ku bikolwa by’obusuubuzi ku nguudo mu Kampala yokka — si ku buli ssimbi ly’akatale.',
      },
      url: SOURCE_KCCA_BYELAWS.url,
    },
  ],
};

const vendorGuide: RightsGuide = {
  category: 'market_vendor',
  title: {
    en: 'Market vendors',
    lg: 'Abasuubuzi b’akatale',
  },
  intro: {
    en: 'The Markets Act, 2023 sets out how public markets must be run. These are the parts that most often affect vendors.',
    lg: 'Markets Act, 2023 egamba ku nkola y’akatale. Bino bye bisinga okukwata abasuubuzi.',
  },
  rights: [
    {
      id: 'vendor-registration',
      title: {
        en: 'Vendor registration must be free',
        lg: 'Okuweebwa ng’omusuubuzi kwa bwereere',
      },
      law: {
        en: 'Section 18(4) of the Markets Act, 2023 provides that a vendor is registered free of charge. Section 18(5) requires a registration number, and section 18(8) requires the register to be displayed.',
        lg: 'Ekitundu 18(4) kya Markets Act, 2023 kigamba omuzuulidde aweebebwa ku bwereere. Ekitundu 18(5) ketaaga namba y’okuweebwa, ate 18(8) ketaaga akatabo k’abasuubuzi okulagibwa.',
      },
      plain: {
        en: 'You should not be charged just to be registered. You should get a registration number, and the vendor register should be displayed so you can check your name.',
        lg: 'Tobazibwa sente olwa kubeera omuzuuliddwa ng’omusuubuzi. Oteekwa okufuna namba, n’akatabo k’abasuubuzi kalina okulagibwa osobolenga okwekenneenya erinnya lyo.',
      },
      steps: [
        {
          en: 'Ask for your registration number.',
          lg: 'Saba namba yo y’okuweebwa.',
        },
        {
          en: 'Check that your name appears on the displayed register.',
          lg: 'Kebera nga erinnya lyo liri ku katabo akalagiddwa.',
        },
        {
          en: 'Keep your registration slip or card safe.',
          lg: 'Kubika pepa lyo ly’okuweebwa oba kaadi bulungi.',
        },
      ],
      source: SOURCE_MARKETS_ACT,
    },
    {
      id: 'vendor-allocation',
      title: {
        en: 'A committee allocates stalls',
        lg: 'Ekitiibwa kye kigaba ebbanga ly’okutuuza',
      },
      law: {
        en: 'Section 21 of the Markets Act, 2023 provides for an allocation committee to allocate work spaces, shops, pitches and stalls in public markets. Existing registered vendors have priority. A vendor may not hold more than one stall, and subletting without authorisation is not allowed; a person who sublets without authorisation must vacate.',
        lg: 'Ekitundu 21 kya Markets Act, 2023 kiteeka ekitiibwa ekigaba eby’okukoleramu mu katale. Abasuubuzi abamaze okuweebwa basinga kufuna ebbanga. Omusuubuzi talina kuba n’essimbi lingi okusinga limu, era takkirizibwa kuwaayo essimbi ye ku mulala nga teyasabye lukusa.',
      },
      plain: {
        en: 'A committee, not just one official, decides who gets a stall. If you were already registered there, you should be considered first. You can hold only one stall and cannot sublet it without permission.',
        lg: 'Ssi omu muntu yekka, wabula ekitiibwa kye kisalawo ani afulumizibwa. Ng’owandibadde oweereddwa mu katale kano, osinga kufuna ebbanga. Osobola okuba n’essimbi limu yokka, era tosobola ku liwa ku mulala nga tolina lukusa.',
      },
      steps: [
        {
          en: 'Keep your allocation slip and registration documents.',
          lg: 'Kubika pepa lyo ly’okuweebwa n’empapula z’okuweereddwa.',
        },
        {
          en: 'Ask who sits on the allocation committee.',
          lg: 'Buuza ani ali ku kitiibwa ekigaba ebbanga.',
        },
        {
          en: 'Get written authorisation before subletting.',
          lg: 'Funa lukusa mu mpapula nga tonnawaayo essimbi ku mulala.',
        },
      ],
      source: SOURCE_MARKETS_ACT,
    },
    {
      id: 'vendor-notice',
      title: {
        en: 'Written notice before layout changes',
        lg: 'Obubaka mu mpapula nga bateekateeka okukyusa akatale',
      },
      law: {
        en: 'Section 16(2) of the Markets Act, 2023 requires at least three months’ written notice before the layout or design of a public market is altered.',
        lg: 'Ekitundu 16(2) kya Markets Act, 2023 ketaaga obubaka mu mpapula okutuuka ku myezi esatu nga bannakyusa enteekateeka oba ekifaananyi kya katale.',
      },
      plain: {
        en: 'If the market will be reorganised or rebuilt, vendors must be told in writing at least three months before. A spoken warning is not enough.',
        lg: 'Ng’akatale kagenda kutereebwa oba okuzimbibwa, abasuubuzi balina okubuulirwa mu mpapula okutuuka ku myezi esatu nga kinnatandika. Okubuulira mu kamwa tekumala.',
      },
      steps: [
        {
          en: 'Ask for the written notice and keep it.',
          lg: 'Saba obubaka obuwandiikiddwa era obukubike.',
        },
        {
          en: 'Check the date on the notice.',
          lg: 'Kebera olunaku oluri ku bubaka.',
        },
        {
          en: 'Raise your objections through the market committee before work starts.',
          lg: 'Weereza eby’okawagalawo mu kitiibwa k’akatale nga emirimu tenatandika.',
        },
      ],
      source: SOURCE_MARKETS_ACT,
    },
    {
      id: 'vendor-fees',
      title: {
        en: 'Market fees must be set and displayed',
        lg: 'Omusaasizo gw’akatale gulina okulagibwa',
      },
      law: {
        en: 'Section 24(1) and (2) of the Markets Act, 2023 provides that market fees are set by the administrative authority and must be displayed.',
        lg: 'Ekitundu 24(1) ne (2) kya Markets Act, 2023 kigamba omusaasizo gw’akatale gusembebwa omulabirira akatale era gulina okulagibwa.',
      },
      plain: {
        en: 'You should be able to see the official fee list. Ask for a written explanation and a receipt if you are asked to pay an amount that is not on it.',
        lg: 'Osobola okulaba olukalala lw’omusaasizo olw’esigika. Ng’obazibwa sente ezitali ku lukalala, saba ebyannyonnyola mu mpapula ne resiti.',
      },
      steps: [
        {
          en: 'Ask to see the displayed fee list.',
          lg: 'Saba okulaba olukalala lw’omusaasizo olulagiddwa.',
        },
        {
          en: 'Get a receipt for every payment.',
          lg: 'Funa resiti ku buli kusasula.',
        },
        {
          en: 'Keep all receipts together.',
          lg: 'Tereka resiti zonna awamu.',
        },
      ],
      source: SOURCE_MARKETS_ACT,
    },
    {
      id: 'vendor-abandonment',
      title: {
        en: 'When a stall may be treated as abandoned',
        lg: 'Essimbi lye litya okutwalibwa ng’eletiddwa',
      },
      law: {
        en: 'Section 22 of the Markets Act, 2023 treats a stall as abandoned if it is unoccupied for three months or the vendor is in default of market fees for three months. Section 26(2) to (5) provides for goods to be seized and sold after 14 days, for any surplus to be reimbursed, and for the allocation to be reallocated.',
        lg: 'Ekitundu 22 kya Markets Act, 2023 kifuula essimbi ng’eletiddwa singa liba tekulimu muntu kumyezi esatu oba ng’omusuubuzi alinga omusaasizo kumyezi esatu. Ekitundu 26(2) okutuuka (5) kigamba ebintu bisobola okukwatibwa n’okutundibwa oluvannyuma lwa nnaku 14, ekisigale kizzibwa omuzuulidde, ate essimbi ne liweebwa omuntu mulala.',
      },
      plain: {
        en: 'If your stall is empty for three months, or you fall three months behind on fees, the authority may treat it as abandoned. If goods are seized, the law sets a process: sale after 14 days, and any money left after costs belongs to you.',
        lg: 'Essimbi ng’elibeera tekulimu muntu kumyezi esatu, oba ng’olingira omusaasizo kumyezi esatu, omulabirira akatale asobola okugitwala ng’eletiddwa. Ebintu bwe bikwatibwa, amateeka galaga enkola: okutundibwa oluvannyuma lwa nnaku 14, ate sente ezisigala ku bubi bwe zibe zeyo.',
      },
      steps: [
        {
          en: 'Keep paying fees or agree a written payment plan.',
          lg: 'Sasula omusaasizo oba kakase enteekateeka y’okusasula mu mpapula.',
        },
        {
          en: 'If you will be away, tell market management in writing.',
          lg: 'Ng’ogenda ewala, manya akulira akatale mu mpapula.',
        },
        {
          en: 'If goods are seized, ask for a written inventory and what happens to any surplus.',
          lg: 'Ebintu bwe bikwatibwa, saba olukalala mu mpapula n’ekye kigenda ku bintu ebisisigale.',
        },
      ],
      source: SOURCE_MARKETS_ACT,
    },
    {
      id: 'vendor-disputes',
      title: {
        en: 'Disputes are handled by elected department heads',
        lg: 'Obutakaayanwa bukolebwa abakubirira abalondeddwa',
      },
      law: {
        en: 'Section 19(3) and 19(5)(c) of the Markets Act, 2023 provides for elected heads of market departments and gives them functions including the settlement of disputes.',
        lg: 'Ekitundu 19(3) ne 19(5)(c) kya Markets Act, 2023 kiteeka abakubirira abalondeddwa ku bitundu by’akatale, era kibawa omulimu ogw’okutereeza obutakaayanwa.',
      },
      plain: {
        en: 'If you disagree with market management or another vendor, the Act expects the elected department heads to handle the dispute first.',
        lg: 'Ng’otakaayangana n’akulira akatale oba omuzuulidde munno, etteeka lyagala abakubirira abalondeddwa bakoleeko ku nsonga eno nga ekitannatwala ku kkooti.',
      },
      steps: [
        {
          en: 'Ask which department head handles your dispute.',
          lg: 'Buuza ani ku bakubirira akwata ku nsonga yo.',
        },
        {
          en: 'Put your complaint in writing and keep a copy.',
          lg: 'Wandiika ekikubuuza mu mpapula era kubika kopi.',
        },
        {
          en: 'If it is not resolved, contact a legal aid provider.',
          lg: 'Ng’ekitaterereeze, kwatana n’omuwagizi w’amateeka.',
        },
      ],
      source: SOURCE_MARKETS_ACT,
    },
    {
      id: 'vendor-designated-space',
      title: {
        en: 'Trade in your designated space',
        lg: 'Suubuziza mu kifo kye wakuweereddwa',
      },
      law: {
        en: 'Section 32 of the Markets Act, 2023 prohibits selling outside the designated space and in pathways or drains.',
        lg: 'Ekitundu 32 kya Markets Act, 2023 kikiraaza okutunda nga toggweredde mu kifo ekituukiriddwa oba mu nguudo z’abantu n’amakulukuta.',
      },
      plain: {
        en: 'Trade from the space allocated to you. Displaying goods in walkways or blocking drains can lead to enforcement action.',
        lg: 'Suubuziza mu kifo kye wakuweereddwa. Okuteeka ebintu mu kkubo ly’abantu oba okuziyiza amakulukuta kisobola okukuviirako ekisago.',
      },
      steps: [
        {
          en: 'Check where your allocated space is.',
          lg: 'Kebera ekifo kye wakuweereddwa.',
        },
        {
          en: 'Do not display goods in paths or drains.',
          lg: 'Toteeka bintu mu nguudo z’abantu oba mu makulukuta.',
        },
        {
          en: 'Ask market management to confirm your space in writing.',
          lg: 'Saba akulira akatale okukakasa ekifo kyo mu mpapula.',
        },
      ],
      source: SOURCE_MARKETS_ACT,
    },
  ],
  documents: [
    {
      id: 'doc-markets-act-vendor',
      title: {
        en: 'Markets Act, 2023',
        lg: 'Markets Act, 2023',
      },
      summary: {
        en: 'The current Ugandan law on vendor registration, stall allocation, fees, notice and disputes.',
        lg: 'Etteeka lya Uganda ku kuweebwa kw’abasuubuzi, essimbi, obubaka, n’obutakaayanwa.',
      },
      url: SOURCE_MARKETS_ACT.url,
    },
    {
      id: 'doc-traffic-amendment-vendor',
      title: {
        en: 'Traffic and Road Safety Act (Amendment) Act, 2020',
        lg: 'Traffic and Road Safety Act (Amendment) Act, 2020',
      },
      summary: {
        en: 'Relevant if a dispute involves a vehicle or transport of goods to or from the market.',
        lg: 'Ekwata ku butakaayanwa obubaawo ng’ekidduka kikwata ku by’akatale.',
      },
      url: SOURCE_TRAFFIC_ACT.url,
    },
    {
      id: 'doc-kcca-bylaws-vendor',
      title: {
        en: 'Kampala Street Traders Byelaws, S.I. 243-23',
        lg: 'Kampala Street Traders Byelaws, S.I. 243-23',
      },
      summary: {
        en: 'KCCA rules for certain named street trading activities in Kampala.',
        lg: 'Amateeka ga KCCA ku bimu ku bikolwa by’obusuubuzi ku nguudo mu Kampala.',
      },
      caution: {
        en: 'Applies only to specific street trader activities in Kampala — not to every market stall.',
        lg: 'Ekwata ku bimu ku bikolwa by’obusuubuzi ku nguudo mu Kampala yokka — si ku buli ssimbi ly’akatale.',
      },
      url: SOURCE_KCCA_BYELAWS.url,
    },
  ],
};

export const rightsGuides: Record<RightsCategory, RightsGuide> = {
  boda_boda: bodaGuide,
  market_vendor: vendorGuide,
};

export function getRightsGuide(category?: string | string[] | null): RightsGuide {
  const value = Array.isArray(category) ? category[0] : category;
  return value === 'market_vendor' ? vendorGuide : bodaGuide;
}

export function localized(text: LocalizedText, language: Language): string {
  return language === 'lg' ? text.lg : text.en;
}
