/**
 * "I was told to leave my stall" — guided eviction scenario for market vendors.
 */
import React, { useState } from 'react';
import {
  View, Text, StyleSheet, ScrollView,
  TouchableOpacity, TextInput, Alert,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { aiApi } from '@/services/api';
import { Colors } from '@/constants/Colors';
import { Spacing, BorderRadius } from '@/constants/Spacing';
import { FontFamily, FontSize } from '@/constants/Typography';
import { useAppStore } from '@/store/useAppStore';
import { t } from '@/i18n/translations';
import Button from '@/components/ui/Button';
import SectionCard from '@/components/ui/SectionCard';
import DisclaimerBanner from '@/components/ui/DisclaimerBanner';
import UncertaintyBanner from '@/components/ui/UncertaintyBanner';
import LoadingOverlay from '@/components/ui/LoadingOverlay';

type YesNo = 'yes' | 'no' | 'not_sure' | null;

const YesNoSelector = ({
  value, onChange, language,
}: { value: YesNo; onChange: (v: YesNo) => void; language: 'en' | 'lg' }) => (
  <View style={yn.row}>
    {(['yes', 'no', 'not_sure'] as YesNo[]).map((opt) => (
      <TouchableOpacity
        key={opt!}
        style={[yn.btn, value === opt && yn.selected]}
        onPress={() => onChange(opt)}
        activeOpacity={0.8}
      >
        <Text style={[yn.label, value === opt && yn.labelSelected]}>
          {opt === 'yes' ? t('yes', language) : opt === 'no' ? t('no', language) : t('notSure', language)}
        </Text>
      </TouchableOpacity>
    ))}
  </View>
);

const yn = StyleSheet.create({
  row: { flexDirection: 'row', gap: Spacing.sm },
  btn: {
    flex: 1,
    paddingVertical: Spacing.md,
    borderRadius: BorderRadius.md,
    borderWidth: 1.5,
    borderColor: Colors.border,
    backgroundColor: Colors.surface,
    alignItems: 'center',
  },
  selected: { borderColor: Colors.primary, backgroundColor: Colors.primaryTint },
  label: { fontFamily: FontFamily.medium, fontSize: FontSize.sm, color: Colors.textMuted },
  labelSelected: { color: Colors.primary },
});

export default function VendorEvictionScreen() {
  const { language } = useAppStore();
  const router = useRouter();

  const [hasAllocationSlip, setHasAllocationSlip] = useState<YesNo>(null);
  const [hasReceipts, setHasReceipts] = useState<YesNo>(null);
  const [noticeIssuer, setNoticeIssuer] = useState('');
  const [reasonGiven, setReasonGiven] = useState('');
  const [deadline, setDeadline] = useState('');
  const [additionalDetails, setAdditionalDetails] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const res = await aiApi.evictionGuidance({
        has_allocation_slip: hasAllocationSlip,
        has_receipts: hasReceipts,
        notice_issuer: noticeIssuer || 'Not specified',
        reason_given: reasonGiven || 'No reason given',
        deadline: deadline || 'Not specified',
        additional_details: additionalDetails,
        language,
      });
      setResult(res);
    } catch (err: any) {
      Alert.alert('Error', err.message ?? t('error_generic', language));
    } finally {
      setLoading(false);
    }
  };

  if (result) {
    return (
      <ScrollView style={styles.scroll} contentContainerStyle={styles.container} showsVerticalScrollIndicator={false}>
        <View style={styles.resultHeader}>
          <Text style={styles.resultEmoji}>🏪</Text>
          <Text style={styles.resultTitle}>Your Guidance</Text>
        </View>

        {result.uncertainty_flag && <UncertaintyBanner />}

        <SectionCard
          title="Guidance for Your Situation"
          content={result.guidance}
          iconName="shield-checkmark"
          iconColor={Colors.secondary}
        />

        {result.legal_sources?.length > 0 && (
          <View style={styles.sourcesBox}>
            <Text style={styles.sourcesTitle}>{t('section_sources', language)}</Text>
            {result.legal_sources.map((src: any, i: number) => (
              <Text key={i} style={styles.sourceItem}>• {src.short_title || src.title}</Text>
            ))}
          </View>
        )}

        <TouchableOpacity style={styles.helpBtn} onPress={() => router.push('/legal-help')}>
          <Ionicons name="people" size={18} color={Colors.accentStrong} />
          <Text style={styles.helpText}>{t('legalHelp_title', language)}</Text>
        </TouchableOpacity>

        <DisclaimerBanner message={result.disclaimer} />
        <Button label="Start Again" onPress={() => setResult(null)} variant="outline" />
      </ScrollView>
    );
  }

  return (
    <ScrollView style={styles.scroll} contentContainerStyle={styles.container} showsVerticalScrollIndicator={false}>
      <LoadingOverlay visible={loading} message={t('analyzing', language)} />

      <View style={styles.headerCard}>
        <Text style={styles.headerEmoji}>🏚️</Text>
        <Text style={styles.headerTitle}>{t('vendor_eviction', language)}</Text>
        <Text style={styles.headerSub}>
          Answer the questions below so LegalBridge can give you relevant information about your situation.
        </Text>
      </View>

      <View style={styles.questionBlock}>
        <Text style={styles.questionLabel}>{t('vendor_eviction_q1', language)}</Text>
        <YesNoSelector value={hasAllocationSlip} onChange={setHasAllocationSlip} language={language} />
      </View>

      <View style={styles.questionBlock}>
        <Text style={styles.questionLabel}>{t('vendor_eviction_q2', language)}</Text>
        <YesNoSelector value={hasReceipts} onChange={setHasReceipts} language={language} />
      </View>

      <View style={styles.questionBlock}>
        <Text style={styles.questionLabel}>{t('vendor_eviction_q3', language)}</Text>
        <TextInput
          style={styles.textInput}
          value={noticeIssuer}
          onChangeText={setNoticeIssuer}
          placeholder="e.g. Market manager / Local council / Unknown"
          placeholderTextColor={Colors.textMuted}
        />
      </View>

      <View style={styles.questionBlock}>
        <Text style={styles.questionLabel}>{t('vendor_eviction_q4', language)}</Text>
        <TextInput
          style={styles.textArea}
          value={reasonGiven}
          onChangeText={setReasonGiven}
          multiline
          numberOfLines={3}
          placeholder="e.g. Unpaid fees / Market redevelopment / No reason given"
          placeholderTextColor={Colors.textMuted}
          textAlignVertical="top"
        />
      </View>

      <View style={styles.questionBlock}>
        <Text style={styles.questionLabel}>{t('vendor_eviction_q5', language)}</Text>
        <TextInput
          style={styles.textInput}
          value={deadline}
          onChangeText={setDeadline}
          placeholder="e.g. 30 June 2024 / No deadline given"
          placeholderTextColor={Colors.textMuted}
        />
      </View>

      <View style={styles.questionBlock}>
        <Text style={styles.questionLabel}>{t('optional', language)}: Any other details?</Text>
        <TextInput
          style={styles.textArea}
          value={additionalDetails}
          onChangeText={setAdditionalDetails}
          multiline
          numberOfLines={3}
          placeholder="Any other information that may be relevant..."
          placeholderTextColor={Colors.textMuted}
          textAlignVertical="top"
        />
      </View>

      <Button label={t('submit', language)} onPress={handleSubmit} loading={loading} />
      <DisclaimerBanner />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scroll: { flex: 1, backgroundColor: Colors.background },
  container: { padding: Spacing.base, paddingBottom: Spacing['3xl'], gap: Spacing.base },
  headerCard: {
    // Berry, as on the vendor dashboard (white on gold failed contrast)
    backgroundColor: Colors.secondary,
    borderRadius: BorderRadius.xl,
    padding: Spacing.xl,
    gap: Spacing.sm,
  },
  headerEmoji: { fontSize: 40 },
  headerTitle: { fontFamily: FontFamily.bold, fontSize: FontSize.xl, color: Colors.textOnPrimary },
  headerSub: {
    fontFamily: FontFamily.regular, fontSize: FontSize.sm,
    color: Colors.textOnPrimary, lineHeight: FontSize.sm * 1.6,
  },
  questionBlock: { gap: Spacing.sm },
  questionLabel: { fontFamily: FontFamily.semiBold, fontSize: FontSize.base, color: Colors.textPrimary },
  textInput: {
    backgroundColor: Colors.surface, borderRadius: BorderRadius.md,
    borderWidth: 1.5, borderColor: Colors.border,
    paddingHorizontal: Spacing.base, paddingVertical: Spacing.md,
    fontFamily: FontFamily.regular, fontSize: FontSize.base, color: Colors.textPrimary, minHeight: 52,
  },
  textArea: {
    backgroundColor: Colors.surface, borderRadius: BorderRadius.md,
    borderWidth: 1.5, borderColor: Colors.border,
    paddingHorizontal: Spacing.base, paddingVertical: Spacing.md,
    fontFamily: FontFamily.regular, fontSize: FontSize.base, color: Colors.textPrimary, minHeight: 90,
  },
  resultHeader: { flexDirection: 'row', alignItems: 'center', gap: Spacing.base, marginBottom: Spacing.sm },
  resultEmoji: { fontSize: 36 },
  resultTitle: { fontFamily: FontFamily.bold, fontSize: FontSize.xl, color: Colors.textPrimary },
  sourcesBox: {
    backgroundColor: Colors.surfaceMuted, borderRadius: BorderRadius.md, padding: Spacing.base, gap: Spacing.xs,
  },
  sourcesTitle: {
    fontFamily: FontFamily.semiBold, fontSize: FontSize.xs, color: Colors.textMuted, textTransform: 'uppercase',
  },
  sourceItem: { fontFamily: FontFamily.regular, fontSize: FontSize.xs, color: Colors.textSecondary },
  helpBtn: {
    flexDirection: 'row', alignItems: 'center', gap: Spacing.sm,
    backgroundColor: Colors.accentTint, borderRadius: BorderRadius.md, padding: Spacing.base,
  },
  helpText: { fontFamily: FontFamily.medium, fontSize: FontSize.sm, color: Colors.accentText },
});
