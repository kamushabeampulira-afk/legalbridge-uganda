/**
 * Market Vendor dashboard screen.
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
    route: '/document/upload?category=market_vendor',
    icon: 'cloud-upload' as const,
    color: Colors.primary,
    titleKey: 'vendor_upload' as const,
    desc_en: 'Upload allocation slips, receipts, eviction notices',
    desc_lg: 'Isa empapula zo',
  },
  {
    id: 'eviction',
    route: '/vendor/eviction',
    icon: 'exit' as const,
    color: Colors.secondary,
    titleKey: 'vendor_eviction' as const,
    desc_en: 'Answer a few questions and get practical guidance',
    desc_lg: 'Noonya obuyambi ku ngufu y\'okufuluka',
  },
  {
    id: 'history',
    route: '/(tabs)/history',
    icon: 'folder-open' as const,
    color: Colors.textPrimary,
    titleKey: 'vendor_history' as const,
    desc_en: 'View documents you have already uploaded',
    desc_lg: 'Laba empapula z\'edda',
  },
  {
    id: 'rights',
    route: '/ask?category=market_vendor&preset=rights',
    icon: 'shield-checkmark' as const,
    color: Colors.accentStrong,
    titleKey: 'vendor_rights' as const,
    desc_en: 'Ask about market law and your rights',
    desc_lg: 'Buuza ku amateeka g\'akatale',
  },
];

export default function VendorScreen() {
  const router = useRouter();
  const { language } = useAppStore();

  return (
    <ScrollView
      style={styles.scroll}
      contentContainerStyle={styles.container}
      showsVerticalScrollIndicator={false}
    >
      <View style={styles.headerCard}>
        <Text style={styles.emoji}>🏪</Text>
        <View style={styles.headerText}>
          <Text style={styles.title}>{t('vendor_title', language)}</Text>
          <Text style={styles.subtitle}>{t('vendor_subtitle', language)}</Text>
        </View>
      </View>

      {ACTIONS.map((action) => (
        <TouchableOpacity
          key={action.id}
          style={styles.actionCard}
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

      <View style={styles.infoBanner}>
        <Ionicons name="document-text" size={20} color={Colors.accentStrong} />
        <Text style={styles.infoText}>
          {language === 'lg'
            ? 'Kubika empapula zonna ez\'akatale lyo: pepa ly\'okuweebwayo, resiti, n\'obubaka.'
            : 'Keep all your market documents safe: allocation slip, payment receipts, and any notices.'}
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
    // Berry, matching the vendor card on Home. White text: 4.6:1.
    backgroundColor: Colors.secondary,
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
    color: Colors.textOnPrimary,
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
    backgroundColor: Colors.accentTint,
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
    color: Colors.accentText,
    lineHeight: FontSize.sm * 1.6,
  },
});
