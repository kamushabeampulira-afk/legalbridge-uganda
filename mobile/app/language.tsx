import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '@/constants/Colors';
import { Spacing, BorderRadius } from '@/constants/Spacing';
import { webShadow } from '@/constants/Shadows';
import { FontFamily, FontSize } from '@/constants/Typography';
import { useAppStore, type Language } from '@/store/useAppStore';
import { LANGUAGES } from '@/i18n/languages';
import { t } from '@/i18n/translations';

export default function LanguageScreen() {
  const router = useRouter();
  const { language, setLanguage } = useAppStore();

  const select = (lang: Language) => {
    setLanguage(lang);
    router.replace('/(auth)/login');
  };

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        <View style={styles.header}>
          <Text style={styles.logo}>⚖️</Text>
          <Text style={styles.title}>{t('selectLanguage', language)}</Text>
          <Text style={styles.subtitle}>Choose the language you prefer</Text>
        </View>

        <View style={styles.options}>
          {LANGUAGES.map((item) => (
            <TouchableOpacity
              key={item.code}
              style={[
                styles.option,
                item.code === language && styles.optionSelected,
                webShadow.md,
              ]}
              onPress={() => select(item.code)}
              activeOpacity={0.8}
              accessibilityLabel={`Select ${item.label}`}
            >
              <Text style={styles.flag}>{item.emoji}</Text>
              <View style={styles.optionText}>
                <Text style={styles.optionTitle}>{item.nativeName}</Text>
                <Text style={styles.optionSub}>{item.label}</Text>
              </View>
              {item.code === language ? (
                <Ionicons name="checkmark-circle" size={22} color={Colors.primary} />
              ) : (
                <Ionicons name="chevron-forward" size={20} color={Colors.textMuted} />
              )}
            </TouchableOpacity>
          ))}
        </View>

        <Text style={styles.note}>
          {t('changeLanguage', language)} → {t('profile_title', language)}
        </Text>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.primary,
  },
  content: {
    padding: Spacing.xl,
    flexGrow: 1,
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
    textAlign: 'center',
  },
  options: { gap: Spacing.sm },
  option: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.xl,
    padding: Spacing.md,
    gap: Spacing.base,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  optionSelected: { borderColor: Colors.accent },
  flag: { fontSize: 28 },
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
