import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '@/constants/Colors';
import { Spacing, BorderRadius } from '@/constants/Spacing';
import { webShadow } from '@/constants/Shadows';
import { FontFamily, FontSize } from '@/constants/Typography';
import { useAppStore } from '@/store/useAppStore';

export default function LanguageScreen() {
  const router = useRouter();
  const { setLanguage } = useAppStore();

  const select = (lang: 'en' | 'lg') => {
    setLanguage(lang);
    router.replace('/(auth)/login');
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.logo}>⚖️</Text>
        <Text style={styles.title}>Choose Your Language</Text>
        <Text style={styles.subtitle}>Londa Olulimi Lwo</Text>
      </View>

      <View style={styles.options}>
        <TouchableOpacity
          style={[styles.option, webShadow.md]}
          onPress={() => select('en')}
          activeOpacity={0.8}
          accessibilityLabel="Select English"
        >
          <Text style={styles.flag}>🇬🇧</Text>
          <View style={styles.optionText}>
            <Text style={styles.optionTitle}>English</Text>
            <Text style={styles.optionSub}>Continue in English</Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color={Colors.textMuted} />
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.option, webShadow.md]}
          onPress={() => select('lg')}
          activeOpacity={0.8}
          accessibilityLabel="Londa Oluganda"
        >
          <Text style={styles.flag}>🇺🇬</Text>
          <View style={styles.optionText}>
            <Text style={styles.optionTitle}>Luganda</Text>
            <Text style={styles.optionSub}>Endeera mu Luganda</Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color={Colors.textMuted} />
        </TouchableOpacity>
      </View>

      <Text style={styles.note}>
        You can change your language at any time in Settings.{'\n'}
        Osobola okyusa olulimi enkanya mu Nteekateeka.
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.primaryDeepPurple,
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
    color: Colors.accentSoftPeach,
    marginTop: Spacing.xs,
  },
  options: { gap: Spacing.base },
  option: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.surfaceWhite,
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
    color: Colors.accentSoftPeach,
    textAlign: 'center',
    marginTop: Spacing['2xl'],
    lineHeight: FontSize.xs * 1.8,
    opacity: 0.8,
  },
});
