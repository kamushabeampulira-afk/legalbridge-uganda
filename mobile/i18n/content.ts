/**
 * Translations of longer app content (the Know Your Rights guides) for
 * languages the guides are not written in.
 *
 * Each ./content/<code>.json file maps the exact English text to its
 * translation. If the English text changes, the old translation no longer
 * matches and the English is shown instead, so a stale translation of the
 * law is never displayed.
 *
 * These are drafts that a native speaker must review before release.
 */
import type { Language } from '@/i18n/translations';
import nynContent from './content/nyn.json';
import achContent from './content/ach.json';
import lggContent from './content/lgg.json';

const CONTENT: Partial<Record<Language, Record<string, string>>> = {
  nyn: nynContent,
  ach: achContent,
  lgg: lggContent,
};

/** The translation of an English content string, or undefined if there is none. */
export function translateContent(english: string, language: Language): string | undefined {
  return CONTENT[language]?.[english] || undefined;
}
