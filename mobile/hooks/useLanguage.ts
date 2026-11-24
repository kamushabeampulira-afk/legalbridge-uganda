/**
 * Hook: useLanguage
 * Convenience hook that returns the current language and t() bound to it.
 */
import { useAppStore } from '@/store/useAppStore';
import { t, TranslationKey } from '@/i18n/translations';

export function useLanguage() {
  const language = useAppStore((s) => s.language);
  const setLanguage = useAppStore((s) => s.setLanguage);

  const translate = (key: TranslationKey) => t(key, language);

  return { language, setLanguage, t: translate };
}
