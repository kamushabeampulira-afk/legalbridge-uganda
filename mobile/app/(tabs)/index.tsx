/**
 * Home Dashboard — two primary pathways + quick actions.
 */
import React from 'react';
import {
  View, Text, StyleSheet, ScrollView,
  TouchableOpacity, Linking,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '@/store/useAppStore';
import { LinearGradient } from 'expo-linear-gradient';
import { Colors, Gradients, withAlpha } from '@/constants/Colors';
import { Spacing, BorderRadius } from '@/constants/Spacing';
import { webShadow } from '@/constants/Shadows';
import { FontFamily, FontSize } from '@/constants/Typography';
import { t } from '@/i18n/translations';

const PRIMARY_PATHS = [
  {
    id: 'boda',
    route: '/(tabs)/boda' as const,
    icon: 'bicycle' as const,
    color: Colors.primary,
    emoji: '🏍️',
    titleKey: 'home_boda' as const,
    desc_en: 'Traffic notices, rights & legal info',
    desc_lg: 'Obubaka bw\'ekkubo n\'amateeka',
  },
  {
    id: 'vendor',
    route: '/(tabs)/vendor' as const,
    icon: 'storefront' as const,
    color: Colors.secondary,
    emoji: '🏪',
    titleKey: 'home_vendor' as const,
    desc_en: 'Allocation slips, eviction notices & rights',
    desc_lg: 'Pepa ly\'okuweebwayo n\'amateeka',
  },
];

const QUICK_ACTIONS = [
  {
    id: 'ask',
    route: '/ask' as const,
    icon: 'chatbubble-ellipses' as const,
    color: Colors.secondary,
    titleKey: 'home_askLegal' as const,
  },
  {
    id: 'upload',
    route: '/document/upload' as const,
    icon: 'cloud-upload' as const,
    color: Colors.primary,
    titleKey: 'home_upload' as const,
  },
  {
    id: 'voice',
    route: '/voice' as const,
    icon: 'mic' as const,
    color: Colors.accentStrong,
    titleKey: 'home_voice' as const,
  },
  {
    id: 'help',
    route: '/legal-help' as const,
    icon: 'people' as const,
    color: Colors.textPrimary,
    titleKey: 'home_findHelp' as const,
  },
  {
    id: 'legal-aid',
    route: '/legal-aid' as const,
    icon: 'shield-checkmark' as const,
    color: Colors.secondary,
    titleKey: 'home_freeLegalAid' as const,
  },
];

export default function HomeScreen() {
  const router = useRouter();
  const { user, language } = useAppStore();

  const greeting = user?.full_name
    ? `${t('home_hello', language)} ${user.full_name.split(' ')[0]}`
    : t('home_greeting', language);

  return (
    <ScrollView
      style={styles.scroll}
      contentContainerStyle={styles.container}
      showsVerticalScrollIndicator={false}
    >
      {/* Hero */}
      <LinearGradient
        colors={Gradients.brand}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.hero}
      >
        <Text style={styles.greeting}>{greeting}</Text>
        <Text style={styles.heroSub}>{t('home_greeting', language)}</Text>
      </LinearGradient>

      {/* Primary pathways */}
      <Text style={styles.sectionLabel}>{t('home_chooseSituation', language)}</Text>
      <View style={styles.primaryRow}>
        {PRIMARY_PATHS.map((p) => (
          <TouchableOpacity
            key={p.id}
            style={[styles.primaryCard, { backgroundColor: p.color }, webShadow.md]}
            onPress={() => router.push(p.route)}
            activeOpacity={0.85}
            accessibilityRole="button"
            accessibilityLabel={t(p.titleKey, language)}
          >
            <Text style={styles.primaryEmoji}>{p.emoji}</Text>
            <Text style={styles.primaryTitle}>{t(p.titleKey, language)}</Text>
            <Text style={styles.primaryDesc}>
              {language === 'lg' ? p.desc_lg : p.desc_en}
            </Text>
            <View style={styles.primaryArrow}>
              <Ionicons name="arrow-forward" size={18} color={Colors.textOnPrimary} />
            </View>
          </TouchableOpacity>
        ))}
      </View>

      {/* Quick actions */}
      <Text style={styles.sectionLabel}>{t('home_quickActions', language)}</Text>
      <View style={styles.actionsGrid}>
        {QUICK_ACTIONS.map((a) => (
          <TouchableOpacity
            key={a.id}
            style={[styles.actionCard, webShadow.sm]}
            onPress={() => router.push(a.route)}
            activeOpacity={0.8}
            accessibilityRole="button"
            accessibilityLabel={t(a.titleKey, language)}
          >
            <View style={[styles.actionIcon, { backgroundColor: withAlpha(a.color, 0.1) }]}>
              <Ionicons name={a.icon} size={24} color={a.color} />
            </View>
            <Text style={styles.actionLabel}>{t(a.titleKey, language)}</Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* USSD banner */}
      <TouchableOpacity
        style={[styles.ussdBanner, webShadow.sm]}
        onPress={() => Linking.openURL('tel:*384*0#')}
        activeOpacity={0.85}
        accessibilityLabel={t('home_ussd_accessibility', language)}
      >
        <View style={styles.ussdLeft}>
          <Text style={styles.ussdIcon}>📱</Text>
          <View>
            <Text style={styles.ussdTitle}>{t('ussd_title', language)}</Text>
            <Text style={styles.ussdBody}>{t('ussd_body', language)}</Text>
          </View>
        </View>
        <View style={styles.ussdCode}>
          <Text style={styles.ussdCodeText}>*384*0#</Text>
        </View>
      </TouchableOpacity>

      {/* Disclaimer */}
      <Text style={styles.disclaimer}>{t('disclaimer', language)}</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scroll: { flex: 1, backgroundColor: Colors.background },
  container: { padding: Spacing.base, paddingBottom: Spacing['3xl'] },

  hero: {
    borderRadius: BorderRadius.xl,
    padding: Spacing.xl,
    marginBottom: Spacing.xl,
  },
  greeting: {
    fontFamily: FontFamily.bold,
    fontSize: FontSize['2xl'],
    color: Colors.textOnPrimary,
  },
  heroSub: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.sm,
    // White: the muted tint would fall below 4.5:1 at the berry end of the gradient
    color: Colors.textOnPrimary,
    marginTop: 4,
  },

  sectionLabel: {
    fontFamily: FontFamily.semiBold,
    fontSize: FontSize.sm,
    color: Colors.textSecondary,
    marginBottom: Spacing.sm,
    marginTop: Spacing.sm,
    textTransform: 'uppercase',
    letterSpacing: 0.8,
  },

  primaryRow: { flexDirection: 'row', gap: Spacing.md, marginBottom: Spacing.xl },
  primaryCard: {
    flex: 1,
    borderRadius: BorderRadius.xl,
    padding: Spacing.base,
    minHeight: 160,
    justifyContent: 'space-between',
  },
  primaryEmoji: { fontSize: 36 },
  primaryTitle: {
    fontFamily: FontFamily.bold,
    fontSize: FontSize.md,
    color: Colors.textOnPrimary,
    marginTop: Spacing.sm,
  },
  primaryDesc: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.xs,
    color: Colors.textOnPrimary,
    lineHeight: FontSize.xs * 1.6,
    marginTop: 4,
  },
  primaryArrow: {
    alignSelf: 'flex-end',
    marginTop: Spacing.sm,
  },

  actionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: Spacing.md,
    marginBottom: Spacing.xl,
  },
  actionCard: {
    width: '47%',
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.base,
    alignItems: 'center',
    gap: Spacing.sm,
  },
  actionIcon: {
    width: 52,
    height: 52,
    borderRadius: 26,
    alignItems: 'center',
    justifyContent: 'center',
  },
  actionLabel: {
    fontFamily: FontFamily.medium,
    fontSize: FontSize.sm,
    color: Colors.textPrimary,
    textAlign: 'center',
  },

  ussdBanner: {
    backgroundColor: Colors.primaryPressed,
    borderRadius: BorderRadius.xl,
    padding: Spacing.base,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: Spacing.xl,
  },
  ussdLeft: { flexDirection: 'row', alignItems: 'center', gap: Spacing.md, flex: 1 },
  ussdIcon: { fontSize: 28 },
  ussdTitle: {
    fontFamily: FontFamily.semiBold,
    fontSize: FontSize.sm,
    color: Colors.textOnPrimary,
  },
  ussdBody: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.xs,
    color: Colors.textOnPrimaryMuted,
    marginTop: 2,
  },
  ussdCode: {
    // White chip with a gold edge: gold as a sparing accent, magenta text for contrast
    backgroundColor: Colors.surface,
    borderWidth: 1.5,
    borderColor: Colors.accent,
    borderRadius: BorderRadius.md,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
  },
  ussdCodeText: {
    fontFamily: FontFamily.bold,
    fontSize: FontSize.md,
    color: Colors.primary,
    letterSpacing: 1,
  },

  disclaimer: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.xs,
    color: Colors.textMuted,
    textAlign: 'center',
    lineHeight: FontSize.xs * 1.6,
  },
});
