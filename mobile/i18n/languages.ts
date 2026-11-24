/**
 * Single source of truth for the languages offered in the app.
 *
 * Codes match the backend SUPPORTED_LANGUAGES map:
 *   en  English
 *   lg  Luganda
 *   nyn Runyankore (ISO 639-3)
 *   ach Acholi     (ISO 639-3)
 *   lgg Lugbara    (ISO 639-3)
 */
import type { Language } from '@/i18n/translations';

export interface LanguageMeta {
  code: Language;
  /** Name shown in the language picker (English). */
  label: string;
  /** Name in the language itself. */
  nativeName: string;
  /** Short code shown in the header switcher. */
  shortCode: string;
  /** Emoji shown in the language picker. */
  emoji: string;
  /** BCP-47 tag used by browser speech synthesis. */
  bcp47: string;
  /** Whether speech recognition / synthesis is reliable for this language. */
  voiceReliable: boolean;
}

export const LANGUAGES: LanguageMeta[] = [
  { code: 'en', label: 'English', nativeName: 'English', shortCode: 'EN', emoji: '🇬🇧', bcp47: 'en-GB', voiceReliable: true },
  { code: 'lg', label: 'Luganda', nativeName: 'Oluganda', shortCode: 'LG', emoji: '🇺🇬', bcp47: 'lg', voiceReliable: false },
  { code: 'nyn', label: 'Runyankore', nativeName: 'Orunyankore', shortCode: 'RUN', emoji: '🇺🇬', bcp47: 'nyn', voiceReliable: false },
  { code: 'ach', label: 'Acholi', nativeName: 'Leb Acoli', shortCode: 'ACH', emoji: '🇺🇬', bcp47: 'ach', voiceReliable: false },
  { code: 'lgg', label: 'Lugbara', nativeName: 'Lugbarati', shortCode: 'LGG', emoji: '🇺🇬', bcp47: 'lgg', voiceReliable: false },
];

export const LANGUAGE_BY_CODE = Object.fromEntries(
  LANGUAGES.map((language) => [language.code, language]),
) as Record<Language, LanguageMeta>;

export function getLanguageMeta(code: Language): LanguageMeta {
  return LANGUAGE_BY_CODE[code] ?? LANGUAGES[0];
}
