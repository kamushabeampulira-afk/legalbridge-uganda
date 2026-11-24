import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '@/constants/Colors';
import { Spacing, BorderRadius } from '@/constants/Spacing';
import { webShadow } from '@/constants/Shadows';
import { FontFamily, FontSize } from '@/constants/Typography';
import { useAppStore } from '@/store/useAppStore';
import { t } from '@/i18n/translations';

export default function LanguageScreen() {
  const router = useRouter();
  const { language, setLanguage } = useAppStore();

  const select = (lang: 'en' | 'lg') => {
    setLanguage(lang);
    router.replace('/(auth)/login');
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.logo}>⚖️</Text>
        <Text style={styles.title}>{t('selectLanguage', language)}</Text>
        <Text style={styles.subtitle}>{t('selectLanguage', 'lg')}</Text>
      </View>

      <View style={styles.options}>
        <TouchableOpacity
          style={[styles.option, webShadow.md]}
          onPress={() => select('en')}
          activeOpacity={0.8}
          accessibilityLabel={t('language_select_en_a11y', language)}
        >
          <Text style={styles.flag}>🇬🇧</Text>
          <View style={styles.optionText}>
            <Text style={styles.optionTitle}>{t('english', language)}</Text>
            <Text style={styles.optionSub}>{t('language_continue_en', language)}</Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color={Colors.textMuted} />
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.option, webShadow.md]}
          onPress={() => select('lg')}
          activeOpacity={0.8}
          accessibilityLabel={t('language_select_lg_a11y', language)}
        >
          <Text style={styles.flag}>🇺🇬</Text>
          <View style={styles.optionText}>
            <Text style={styles.optionTitle}>{t('luganda', language)}</Text>
            <Text style={styles.optionSub}>{t('language_continue_lg', language)}</Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color={Colors.textMuted} />
        </TouchableOpacity>
      </View>

      <Text style={styles.note}>
        {t('language_note', language)}{'\n'}
        {t('language_note', 'lg')}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.primary,
    padding: Spacing.xl,
    justifyContent: 'center',
  },
  header: { alignItems: 'center', marginBottom: Spacing['3xl'] },
  logo: { fontSize: 56, marginBottom: Spacing.base },
  title: {
    fontFamily: FontFamily.bold,
    fontSize: FontSize['2xl'],
    color: Colors.textOnPrimary,
    textAlign: 'center',
  },
  subtitle: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.md,
    color: Colors.textOnPrimaryMuted,
    marginTop: Spacing.xs,
  },
  options: { gap: Spacing.base },
  option: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.xl,
    padding: Spacing.lg,
    gap: Spacing.base,
  },
  flag: { fontSize: 32 },
  optionText: { flex: 1 },
  optionTitle: {
    fontFamily: FontFamily.bold,
    fontSize: FontSize.lg,
    color: Colors.textPrimary,
  },
  optionSub: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.sm,
    color: Colors.textMuted,
    marginTop: 2,
  },
  note: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.xs,
    color: Colors.textOnPrimaryMuted,
    textAlign: 'center',
    marginTop: Spacing['2xl'],
    lineHeight: FontSize.xs * 1.8,
  },
});
