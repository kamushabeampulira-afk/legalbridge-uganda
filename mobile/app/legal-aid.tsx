/**
 * Free Legal Aid — dedicated entry point for district-based legal aid contacts.
 */
import React from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '@/constants/Colors';
import { Spacing, BorderRadius } from '@/constants/Spacing';
import { webShadow } from '@/constants/Shadows';
import { FontFamily, FontSize } from '@/constants/Typography';
import { useAppStore } from '@/store/useAppStore';
import { t } from '@/i18n/translations';
import LegalAidConnectCard from '@/components/ui/LegalAidConnectCard';

export default function LegalAidScreen() {
  const { language } = useAppStore();
  const router = useRouter();

  return (
    <ScrollView
      style={styles.scroll}
      contentContainerStyle={styles.container}
      showsVerticalScrollIndicator={false}
    >
      <View style={styles.hero}>
        <Ionicons name="people-circle" size={28} color={Colors.textOnPrimary} />
        <View style={styles.heroText}>
          <Text style={styles.heroTitle}>{t('stack_legalAid', language)}</Text>
          <Text style={styles.heroSub}>{t('legalAidConnect_subtitle', language)}</Text>
        </View>
      </View>

      <LegalAidConnectCard />

      <TouchableOpacity
        style={[styles.directoryButton, webShadow.sm]}
        onPress={() => router.push('/legal-help')}
        activeOpacity={0.85}
        accessibilityRole="button"
        accessibilityLabel={t('legalHelp_title', language)}
      >
        <Ionicons name="list-outline" size={18} color={Colors.primary} />
        <Text style={styles.directoryButtonText}>{t('legalHelp_title', language)}</Text>
        <Ionicons name="arrow-forward" size={18} color={Colors.primary} />
      </TouchableOpacity>

      <Text style={styles.disclaimer}>{t('disclaimer', language)}</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scroll: { flex: 1, backgroundColor: Colors.background },
  container: { padding: Spacing.base, paddingBottom: Spacing['3xl'], gap: Spacing.base },

  hero: {
    backgroundColor: Colors.primary,
    borderRadius: BorderRadius.xl,
    padding: Spacing.xl,
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: Spacing.base,
  },
  heroText: { flex: 1 },
  heroTitle: {
    fontFamily: FontFamily.bold,
    fontSize: FontSize.lg,
    color: Colors.textOnPrimary,
  },
  heroSub: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.xs,
    color: Colors.textOnPrimaryMuted,
    lineHeight: FontSize.xs * 1.6,
    marginTop: 4,
  },

  directoryButton: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.base,
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
  },
  directoryButtonText: {
    flex: 1,
    fontFamily: FontFamily.medium,
    fontSize: FontSize.sm,
    color: Colors.primary,
  },

  disclaimer: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.xs,
    color: Colors.textMuted,
    textAlign: 'center',
    lineHeight: FontSize.xs * 1.6,
  },
});
