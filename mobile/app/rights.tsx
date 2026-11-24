/**
 * Know Your Rights — bilingual guides for boda boda riders and market vendors.
 * Content is authored in mobile/constants/LegalRights.ts and follows the app
 * language setting. All citations link to published Ugandan law.
 */
import React, { useState } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity, Linking,
} from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Colors, withAlpha } from '@/constants/Colors';
import { Spacing, BorderRadius } from '@/constants/Spacing';
import { webShadow } from '@/constants/Shadows';
import { FontFamily, FontSize } from '@/constants/Typography';
import { useAppStore } from '@/store/useAppStore';
import { t } from '@/i18n/translations';
import {
  getRightsGuide,
  localized,
  rightsGuides,
  type LegalRight,
  type RightsCategory,
} from '@/constants/LegalRights';
import DisclaimerBanner from '@/components/ui/DisclaimerBanner';

function RightCard({ right, language }: { right: LegalRight; language: 'en' | 'lg' }) {
  const openSource = () => {
    Linking.openURL(right.source.url).catch(() => undefined);
  };

  return (
    <View style={[styles.rightCard, webShadow.sm]}>
      <View style={styles.rightHeading}>
        <View style={[styles.rightIcon, { backgroundColor: withAlpha(Colors.primary, 0.1) }]}>
          <Ionicons name="shield-checkmark" size={20} color={Colors.primary} />
        </View>
        <Text style={styles.rightTitle}>{localized(right.title, language)}</Text>
      </View>

      <View style={styles.lawBlock}>
        <Text style={styles.blockLabel}>{t('rights_whatLaw', language)}</Text>
        <Text style={styles.blockText}>{localized(right.law, language)}</Text>
      </View>

      <View style={styles.plainBlock}>
        <Text style={styles.blockLabel}>{t('rights_plain', language)}</Text>
        <Text style={styles.blockText}>{localized(right.plain, language)}</Text>
      </View>

      <View style={styles.stepsBlock}>
        <Text style={styles.blockLabel}>{t('rights_steps', language)}</Text>
        {right.steps.map((step, index) => (
          <View key={index} style={styles.stepRow}>
            <Text style={styles.stepNumber}>{index + 1}.</Text>
            <Text style={styles.stepText}>{localized(step, language)}</Text>
          </View>
        ))}
      </View>

      <View style={styles.sourceBlock}>
        <Text style={styles.sourceLabel}>{t('rights_source', language)}: </Text>
        <Text style={styles.sourceText}>{localized(right.source.label, language)}</Text>
        <TouchableOpacity style={styles.sourceButton} onPress={openSource} accessibilityRole="button">
          <Text style={styles.sourceButtonText}>{t('rights_openSource', language)}</Text>
          <Ionicons name="open-outline" size={14} color={Colors.textLink} />
        </TouchableOpacity>
      </View>
    </View>
  );
}

export default function RightsScreen() {
  const params = useLocalSearchParams<{ category?: string | string[] }>();
  const language = useAppStore((s) => s.language);
  const router = useRouter();
  const [category, setCategory] = useState<RightsCategory>(
    () => getRightsGuide(params.category).category,
  );

  const guide = rightsGuides[category];

  const switchCategory = (next: RightsCategory) => {
    setCategory(next);
    router.setParams({ category: next });
  };

  return (
    <ScrollView
      style={styles.scroll}
      contentContainerStyle={styles.container}
      showsVerticalScrollIndicator={false}
    >
      <View style={[styles.headerCard, webShadow.md]}>
        <Ionicons name="book-outline" size={28} color={Colors.textOnPrimary} />
        <View style={styles.headerText}>
          <Text style={styles.title}>{t('stack_rights', language)}</Text>
          <Text style={styles.subtitle}>{localized(guide.title, language)}</Text>
        </View>
      </View>

      <View style={styles.tabs}>
        {(['boda_boda', 'market_vendor'] as RightsCategory[]).map((key) => (
          <TouchableOpacity
            key={key}
            style={[styles.tab, category === key && styles.tabActive]}
            onPress={() => switchCategory(key)}
            accessibilityRole="tab"
            accessibilityState={{ selected: category === key }}
          >
            <Text style={[styles.tabText, category === key && styles.tabTextActive]}>
              {key === 'boda_boda' ? t('rights_tab_boda', language) : t('rights_tab_vendor', language)}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <Text style={styles.intro}>{localized(guide.intro, language)}</Text>

      {guide.rights.map((right) => (
        <RightCard key={right.id} right={right} language={language} />
      ))}

      <View style={styles.documentsHeading}>
        <Ionicons name="document-text-outline" size={20} color={Colors.accentStrong} />
        <Text style={styles.documentsTitle}>{t('rights_documents', language)}</Text>
      </View>

      {guide.documents.map((doc) => (
        <View key={doc.id} style={[styles.docCard, webShadow.sm]}>
          <Text style={styles.docTitle}>{localized(doc.title, language)}</Text>
          <Text style={styles.docSummary}>{localized(doc.summary, language)}</Text>
          {doc.caution && (
            <Text style={styles.docCaution}>
              {t('rights_note', language)}: {localized(doc.caution, language)}
            </Text>
          )}
          <TouchableOpacity
            style={styles.docButton}
            onPress={() => Linking.openURL(doc.url).catch(() => undefined)}
            accessibilityRole="button"
          >
            <Text style={styles.docButtonText}>{t('rights_openSource', language)}</Text>
            <Ionicons name="open-outline" size={14} color={Colors.textLink} />
          </TouchableOpacity>
        </View>
      ))}

      <TouchableOpacity
        style={[styles.askButton, webShadow.sm]}
        onPress={() => router.push(`/ask?category=${category}` as any)}
        accessibilityRole="button"
      >
        <Ionicons name="chatbubble-outline" size={20} color={Colors.textOnPrimary} />
        <Text style={styles.askButtonText}>{t('rights_ask', language)}</Text>
      </TouchableOpacity>

      <Text style={styles.footerNote}>{t('rights_footer', language)}</Text>
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

  tabs: { flexDirection: 'row', gap: Spacing.sm },
  tab: {
    flex: 1,
    paddingVertical: Spacing.sm,
    borderRadius: BorderRadius.full,
    backgroundColor: Colors.surface,
    borderWidth: 1,
    borderColor: Colors.border,
    alignItems: 'center',
  },
  tabActive: { backgroundColor: Colors.primary, borderColor: Colors.primary },
  tabText: {
    fontFamily: FontFamily.semiBold,
    fontSize: FontSize.sm,
    color: Colors.textSecondary,
  },
  tabTextActive: { color: Colors.textOnPrimary },

  intro: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.sm,
    color: Colors.textSecondary,
    lineHeight: FontSize.sm * 1.6,
  },

  rightCard: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.base,
    gap: Spacing.md,
  },
  rightHeading: { flexDirection: 'row', alignItems: 'center', gap: Spacing.sm },
  rightIcon: {
    width: 36,
    height: 36,
    borderRadius: BorderRadius.sm,
    alignItems: 'center',
    justifyContent: 'center',
  },
  rightTitle: {
    flex: 1,
    fontFamily: FontFamily.bold,
    fontSize: FontSize.md,
    color: Colors.textPrimary,
    lineHeight: FontSize.md * 1.35,
  },

  lawBlock: {
    backgroundColor: Colors.primaryTint,
    borderRadius: BorderRadius.md,
    padding: Spacing.md,
  },
  plainBlock: {
    backgroundColor: Colors.successBg,
    borderRadius: BorderRadius.md,
    padding: Spacing.md,
  },
  stepsBlock: {
    backgroundColor: Colors.surfaceMuted,
    borderRadius: BorderRadius.md,
    padding: Spacing.md,
  },
  blockLabel: {
    fontFamily: FontFamily.bold,
    fontSize: FontSize.xs,
    color: Colors.primary,
    letterSpacing: 0.4,
    marginBottom: Spacing.xs,
  },
  blockText: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.sm,
    color: Colors.textPrimary,
    lineHeight: FontSize.sm * 1.65,
  },
  stepRow: { flexDirection: 'row', marginTop: Spacing.sm },
  stepNumber: {
    fontFamily: FontFamily.bold,
    fontSize: FontSize.sm,
    color: Colors.primary,
    marginRight: Spacing.sm,
  },
  stepText: {
    flex: 1,
    fontFamily: FontFamily.regular,
    fontSize: FontSize.sm,
    color: Colors.textPrimary,
    lineHeight: FontSize.sm * 1.6,
  },

  sourceBlock: {
    borderTopWidth: 1,
    borderTopColor: Colors.border,
    paddingTop: Spacing.sm,
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  sourceLabel: {
    fontFamily: FontFamily.semiBold,
    fontSize: FontSize.xs,
    color: Colors.textMuted,
  },
  sourceText: {
    flex: 1,
    fontFamily: FontFamily.regular,
    fontSize: FontSize.xs,
    color: Colors.textMuted,
    lineHeight: FontSize.xs * 1.5,
  },
  sourceButton: {
    width: '100%',
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.xs,
    marginTop: Spacing.sm,
  },
  sourceButtonText: {
    fontFamily: FontFamily.semiBold,
    fontSize: FontSize.xs,
    color: Colors.textLink,
  },

  documentsHeading: { flexDirection: 'row', alignItems: 'center', gap: Spacing.sm, marginTop: Spacing.sm },
  documentsTitle: {
    fontFamily: FontFamily.bold,
    fontSize: FontSize.md,
    color: Colors.textPrimary,
  },
  docCard: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.base,
  },
  docTitle: {
    fontFamily: FontFamily.semiBold,
    fontSize: FontSize.base,
    color: Colors.textPrimary,
  },
  docSummary: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.sm,
    color: Colors.textSecondary,
    lineHeight: FontSize.sm * 1.6,
    marginTop: Spacing.xs,
  },
  docCaution: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.xs,
    color: Colors.warning,
    lineHeight: FontSize.xs * 1.5,
    marginTop: Spacing.sm,
  },
  docButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.xs,
    marginTop: Spacing.sm,
  },
  docButtonText: {
    fontFamily: FontFamily.semiBold,
    fontSize: FontSize.xs,
    color: Colors.textLink,
  },

  askButton: {
    backgroundColor: Colors.secondary,
    borderRadius: BorderRadius.lg,
    padding: Spacing.base,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: Spacing.sm,
  },
  askButtonText: {
    fontFamily: FontFamily.semiBold,
    fontSize: FontSize.base,
    color: Colors.textOnPrimary,
  },
  footerNote: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.xs,
    color: Colors.textMuted,
    lineHeight: FontSize.xs * 1.5,
    textAlign: 'center',
  },
});
