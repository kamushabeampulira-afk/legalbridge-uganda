import React from 'react';
import { TouchableOpacity, Text, StyleSheet, View } from 'react-native';
import { useAppStore } from '@/store/useAppStore';
import { Colors } from '@/constants/Colors';
import { FontFamily, FontSize } from '@/constants/Typography';
import { Spacing, BorderRadius } from '@/constants/Spacing';

/**
 * Compact language toggle — shows current language and taps to switch.
 * Place in navigation header or settings screen.
 */
export default function LanguageSwitcher() {
  const { language, setLanguage } = useAppStore();

  const toggle = () => setLanguage(language === 'en' ? 'lg' : 'en');

  return (
    <TouchableOpacity
      style={styles.container}
      onPress={toggle}
      activeOpacity={0.8}
      accessibilityLabel={`Current language: ${language === 'en' ? 'English' : 'Luganda'}. Tap to switch.`}
      accessibilityRole="button"
    >
      <Text style={styles.flag}>{language === 'en' ? '🇬🇧' : '🇺🇬'}</Text>
      <Text style={styles.label}>{language === 'en' ? 'EN' : 'LG'}</Text>
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
