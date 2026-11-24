/**
 * LegalBridge — UI translations.
 * Keep strings short and use plain language.
 *
 * Languages: en (English), lg (Luganda), nyn (Runyankore),
 * ach (Acholi), lgg (Lugbara). Codes follow ISO 639-3 where no
 * ISO 639-1 code exists.
 *
 * The strings live in ./locales/<code>.json. English and Luganda are complete
 * (a missing Luganda key fails the type check). Runyankore, Acholi and Lugbara
 * may be partial: any key they leave out is shown in English.
 *
 * nyn, ach and lgg are drafts that a native speaker must review before
 * release. Missing keys can be machine-drafted with Sunbird AI:
 *   cd backend && python manage.py translate_app_text --language lgg
 */
import enStrings from './locales/en.json';
import lgStrings from './locales/lg.json';
import nynStrings from './locales/nyn.json';
import achStrings from './locales/ach.json';
import lggStrings from './locales/lgg.json';

const en = enStrings;

export type TranslationKey = keyof typeof en;

type Strings = Record<TranslationKey, string>;

const lg: Strings = lgStrings;

/** Partial translations: keys that are not translated yet fall back to English. */
function withEnglishFallback(partial: Partial<Strings>): Strings {
  return { ...en, ...partial };
}

export const translations = {
  en,
  lg,
  nyn: withEnglishFallback(nynStrings),
  ach: withEnglishFallback(achStrings),
  lgg: withEnglishFallback(lggStrings),
};

export type Language = keyof typeof translations;

export const SUPPORTED_LANGUAGES: Language[] = ['en', 'lg', 'nyn', 'ach', 'lgg'];

export function isSupportedLanguage(value: unknown): value is Language {
  return typeof value === 'string' && SUPPORTED_LANGUAGES.includes(value as Language);
}

export function normalizeLanguage(value: unknown): Language {
  return isSupportedLanguage(value) ? value : 'en';
}

export function t(key: TranslationKey, lang: Language = 'en'): string {
  const dictionary = translations[lang] ?? translations.en;
  return dictionary[key] ?? translations.en[key] ?? key;
}
