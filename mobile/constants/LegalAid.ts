/**
 * Legal aid office and support contact data.
 *
 * Primary area offices are taken from Justice Centres Uganda's published
 * "Find your nearest Justice Centre" list (https://justicecentres.go.ug/contacts/).
 * Only published numbers are included here. Districts not covered by that list
 * do not get an invented fallback office; the app shows the clearly labelled
 * extra-support contacts instead.
 *
 * Counsel Doug and the toll-free line are additional help, not district fallbacks.
 */

export const UGANDA_DISTRICTS = [
  'Abim', 'Adjumani', 'Agago', 'Alebtong', 'Amolatar', 'Amudat', 'Amuria',
  'Amuru', 'Apac', 'Arua', 'Budaka', 'Bududa', 'Bugiri', 'Bugweri', 'Buikwe',
  'Bukedea', 'Bukomansimbi', 'Bukwo', 'Bulambuli', 'Buliisa', 'Bundibugyo',
  'Bunyangabu', 'Bushenyi', 'Busia', 'Butaleja', 'Butambala', 'Butebo',
  'Buvuma', 'Buyende', 'Dokolo', 'Gomba', 'Gulu', 'Hoima', 'Ibanda', 'Iganga',
  'Isingiro', 'Jinja', 'Kaabong', 'Kabale', 'Kaberamaido', 'Kabarole', 'Kagadi',
  'Kalaki', 'Kalangala', 'Kaliro', 'Kalungu', 'Kamuli', 'Kampala', 'Kamwenge',
  'Kanungu', 'Kapchorwa', 'Kapelebyong', 'Karenga', 'Kasese', 'Kassanda',
  'Kayunga', 'Kazo', 'Kibaale', 'Kiboga', 'Kibuku', 'Kikuube', 'Kiruhura',
  'Kiryandongo', 'Kisoro', 'Kitagwenda', 'Kitgum', 'Koboko', 'Kole', 'Kotido',
  'Kumi', 'Kwania', 'Kween', 'Kyankwanzi', 'Kyegegwa', 'Kyenjojo', 'Kyotera',
  'Lamwo', 'Lira', 'Luwero', 'Luuka', 'Lwengo', 'Lyantonde', 'Madi-Okollo',
  'Manafwa', 'Maracha', 'Masaka', 'Masindi', 'Mayuge', 'Mbale', 'Mbarara',
  'Mitooma', 'Mityana', 'Moroto', 'Moyo', 'Mpigi', 'Mubende', 'Mukono',
  'Nakapiripirit', 'Nakaseke', 'Nakasongola', 'Namayingo', 'Namisindwa',
  'Namutumba', 'Napak', 'Nebbi', 'Ngora', 'Ntoroko', 'Ntungamo', 'Nwoya',
  'Obongi', 'Omoro', 'Otuke', 'Oyam', 'Pader', 'Pakwach', 'Pallisa', 'Rakai',
  'Rubanda', 'Rubirizi', 'Rukiga', 'Rukungiri', 'Rwampara', 'Sembabule',
  'Serere', 'Sheema', 'Sironko', 'Soroti', 'Terego', 'Tororo', 'Wakiso',
  'Yumbe', 'Zombo',
] as const;

export interface LegalAidOffice {
  id: string;
  name: string;
  /** Districts the centre officially says it serves. */
  districts: string[];
  /** Phone numbers exactly as published, so local dialling still works. */
  phones: string[];
}

export const AREA_OFFICES: LegalAidOffice[] = [
  {
    id: 'mmengo',
    name: 'Mmengo Justice Centre',
    districts: ['Kampala', 'Mpigi', 'Wakiso'],
    phones: ['0800 100 210', '0800 100 225', '0759 500 440'],
  },
  {
    id: 'lira',
    name: 'Lira Justice Centre',
    districts: ['Apac', 'Pader', 'Lira'],
    phones: ['0800 100 212', '0759 500 442'],
  },
  {
    id: 'mbale',
    name: 'Mbale Justice Centre',
    districts: ['Budaka', 'Mbale', 'Sironko'],
    phones: ['0800 100 219', '0707 500 449'],
  },
  {
    id: 'mukono',
    name: 'Mukono Justice Centre',
    districts: ['Buikwe', 'Kayunga', 'Mukono'],
    phones: ['0800 100 218', '0707 500 448'],
  },
  {
    id: 'hoima',
    name: 'Hoima Justice Centre',
    districts: ['Buliisa', 'Hoima', 'Kiryandongo'],
    phones: ['0800 100 213', '0700 500 444'],
  },
  {
    id: 'bundibugyo',
    name: 'Bundibugyo Justice Centre',
    districts: ['Bundibugyo'],
    phones: ['0800 100 223', '0707 500 451'],
  },
  {
    id: 'jinja',
    name: 'Jinja Justice Centre',
    districts: ['Jinja'],
    phones: ['0800 100 214', '0700 500 447'],
  },
  {
    id: 'fort-portal',
    name: 'Fort Portal Justice Centre',
    districts: ['Kabarole'],
    phones: ['0800 100 216', '0700 500 446'],
  },
  {
    id: 'kasese',
    name: 'Kasese Justice Centre',
    districts: ['Kasese'],
    phones: ['0800 100 224', '0707 500 450'],
  },
  {
    id: 'mubende',
    name: 'Mubende Justice Centre',
    districts: ['Kyegegwa', 'Mubende', 'Mityana'],
    phones: ['0800 100 217', '0707 500 447'],
  },
  {
    id: 'masaka',
    name: 'Masaka Justice Centre',
    districts: ['Masaka'],
    phones: ['0800 100 215', '0700 500 449'],
  },
  {
    id: 'tororo',
    name: 'Tororo Justice Centre',
    districts: ['Tororo', 'Manafwa', 'Butaleja', 'Busia'],
    phones: ['0800 100 211', '0800 100 226', '0759 500 443'],
  },
  {
    id: 'yumbe',
    name: 'Yumbe Justice Centre',
    districts: ['Yumbe'],
    phones: ['0393 254 757', '0200 906 833'],
  },
];

/** Extra help for when an area office is busy or unreachable — not a fallback contact. */
export const EXTRA_SUPPORT = {
  officerName: 'Counsel Doug',
  officerPhone: '+256784122995',
  tollFreePhone: '+256323303969',
} as const;

export function getLegalAidOffice(district?: string | null): LegalAidOffice | null {
  if (!district) return null;
  return AREA_OFFICES.find((office) => office.districts.includes(district)) ?? null;
}

/** Build a tel: URL from a published phone number, keeping local dialling intact. */
export function telHref(phone: string): string {
  return `tel:${phone.replace(/[^\d+]/g, '')}`;
}
