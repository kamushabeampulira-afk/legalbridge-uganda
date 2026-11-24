import React from 'react';
import { TouchableOpacity, Text, StyleSheet } from 'react-native';
import { useAppStore } from '@/store/useAppStore';
import { LANGUAGES, getLanguageMeta } from '@/i18n/languages';
import { Colors } from '@/constants/Colors';
import { FontFamily, FontSize } from '@/constants/Typography';
import { Spacing, BorderRadius } from '@/constants/Spacing';

/**
 * Compact language switcher — tap to cycle through supported languages.
 * The full picker is available on the language screen and in Profile.
 */
export default function LanguageSwitcher() {
  const { language, setLanguage } = useAppStore();
  const meta = getLanguageMeta(language);

  const cycle = () => {
    const index = LANGUAGES.findIndex((item) => item.code === language);
    const next = LANGUAGES[(index + 1) % LANGUAGES.length];
    setLanguage(next.code);
  };

  return (
    <TouchableOpacity
      style={styles.container}
      onPress={cycle}
      activeOpacity={0.8}
      accessibilityLabel={`Current language: ${meta.label}. Tap to change language.`}
      accessibilityRole="button"
    >
      <Text style={styles.flag}>{meta.emoji}</Text>
      <Text style={styles.label}>{meta.shortCode}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.18)',
    borderRadius: BorderRadius.full,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.xs,
    gap: 4,
  },
  flag: { fontSize: 14 },
  label: {
    fontFamily: FontFamily.semiBold,
    fontSize: FontSize.xs,
    color: Colors.textOnPrimary,
    letterSpacing: 0.5,
  },
});
