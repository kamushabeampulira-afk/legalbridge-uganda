/**
 * Boda Boda dashboard screen.
 */
import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Colors, withAlpha } from '@/constants/Colors';
import { Spacing, BorderRadius } from '@/constants/Spacing';
import { webShadow } from '@/constants/Shadows';
import { FontFamily, FontSize } from '@/constants/Typography';
import { useAppStore } from '@/store/useAppStore';
import { t } from '@/i18n/translations';
import DisclaimerBanner from '@/components/ui/DisclaimerBanner';

const ACTIONS = [
  {
    id: 'upload',
    route: '/document/upload?category=boda_boda',
    icon: 'cloud-upload' as const,
    color: Colors.primary,
    titleKey: 'boda_upload' as const,
    desc_en: 'Photograph or upload a traffic notice',
    desc_lg: 'Isa obubaka bw\'ekkubo',
  },
  {
    id: 'stopped',
    route: '/boda/stopped',
    icon: 'hand-left' as const,
    color: Colors.secondary,
    titleKey: 'boda_stopped' as const,
    desc_en: 'Answer a few questions and get guidance',
    desc_lg: 'Noonya obuyambi ng\'okuggwa',
  },
  {
    id: 'history',
    route: '/(tabs)/history',
    icon: 'folder-open' as const,
    color: Colors.textPrimary,
    titleKey: 'boda_history' as const,
    desc_en: 'View documents you have already uploaded',
    desc_lg: 'Laba empapula z\'edda',
  },
  {
    id: 'rights',
    route: '/rights?category=boda_boda',
    icon: 'shield-checkmark' as const,
    color: Colors.accentStrong,
    titleKey: 'boda_rights' as const,
    desc_en: 'Your rights under Ugandan traffic law, in plain language',
    desc_lg: 'Eddembe lyo mu mateeka g\'ekkubo, mu lulimi olwangu',
  },
];

export default function BodaScreen() {
  const router = useRouter();
  const { language } = useAppStore();

  return (
    <ScrollView
      style={styles.scroll}
      contentContainerStyle={styles.container}
      showsVerticalScrollIndicator={false}
    >
      {/* Header card */}
      <View style={[styles.headerCard, webShadow.md]}>
        <Text style={styles.emoji}>🏍️</Text>
        <View style={styles.headerText}>
          <Text style={styles.title}>{t('boda_title', language)}</Text>
          <Text style={styles.subtitle}>{t('boda_subtitle', language)}</Text>
        </View>
      </View>

      {/* Action cards */}
      {ACTIONS.map((action) => (
        <TouchableOpacity
          key={action.id}
          style={[styles.actionCard, webShadow.sm]}
          onPress={() => router.push(action.route as any)}
          activeOpacity={0.85}
          accessibilityRole="button"
          accessibilityLabel={t(action.titleKey, language)}
        >
          <View style={[styles.iconBox, { backgroundColor: withAlpha(action.color, 0.1) }]}>
            <Ionicons name={action.icon} size={28} color={action.color} />
          </View>
          <View style={styles.actionText}>
            <Text style={styles.actionTitle}>{t(action.titleKey, language)}</Text>
            <Text style={styles.actionDesc}>
              {language === 'lg' ? action.desc_lg : action.desc_en}
            </Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color={Colors.textMuted} />
        </TouchableOpacity>
      ))}

      {/* Key info banner */}
      <View style={styles.infoBanner}>
        <Ionicons name="information-circle" size={20} color={Colors.primary} />
        <Text style={styles.infoText}>
          {language === 'lg'
            ? 'Obuzibu obw\'ekkubo? Noonya obuyambi obuva eri looya awungeddwa.'
            : 'Facing a traffic issue? Always request a written notice with a reference number.'}
        </Text>
      </View>

      <DisclaimerBanner />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scroll: { flex: 1, backgroundColor: Colors.background },
  container: { padding: Spacing.base, paddingBottom: Spacing['3xl'], gap: Spacing.md },

  headerCard: {
    backgroundColor: Colors.primary,
    borderRadius: BorderRadius.xl,
    padding: Spacing.xl,
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.base,
  },
  emoji: { fontSize: 48 },
  headerText: { flex: 1 },
  title: {
    fontFamily: FontFamily.bold,
    fontSize: FontSize.xl,
    color: Colors.textOnPrimary,
  },
  subtitle: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.sm,
    color: Colors.textOnPrimaryMuted,
    marginTop: 4,
  },

  actionCard: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.base,
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.base,
  },
  iconBox: {
    width: 56,
    height: 56,
    borderRadius: BorderRadius.md,
    alignItems: 'center',
    justifyContent: 'center',
  },
  actionText: { flex: 1 },
  actionTitle: {
    fontFamily: FontFamily.semiBold,
    fontSize: FontSize.base,
    color: Colors.textPrimary,
  },
  actionDesc: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.xs,
    color: Colors.textMuted,
    marginTop: 3,
    lineHeight: FontSize.xs * 1.5,
  },

  infoBanner: {
    backgroundColor: Colors.primaryTint,
    borderRadius: BorderRadius.md,
    padding: Spacing.base,
    flexDirection: 'row',
    gap: Spacing.sm,
    alignItems: 'flex-start',
  },
  infoText: {
    flex: 1,
    fontFamily: FontFamily.regular,
    fontSize: FontSize.sm,
    color: Colors.primary,
    lineHeight: FontSize.sm * 1.6,
  },
});
