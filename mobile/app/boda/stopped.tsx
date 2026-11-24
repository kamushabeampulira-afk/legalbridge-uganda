/**
 * "I was stopped by an officer" — guided scenario for boda riders.
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
  <View style={yesNoStyles.row}>
    {(['yes', 'no', 'not_sure'] as YesNo[]).map((opt) => (
      <TouchableOpacity
        key={opt!}
        style={[yesNoStyles.btn, value === opt && yesNoStyles.selected]}
        onPress={() => onChange(opt)}
        activeOpacity={0.8}
      >
        <Text style={[yesNoStyles.label, value === opt && yesNoStyles.labelSelected]}>
          {opt === 'yes' ? t('yes', language) : opt === 'no' ? t('no', language) : t('notSure', language)}
        </Text>
      </TouchableOpacity>
    ))}
  </View>
);

const yesNoStyles = StyleSheet.create({
  row: { flexDirection: 'row', gap: Spacing.sm },
  btn: {
    flex: 1,
    paddingVertical: Spacing.md,
    borderRadius: BorderRadius.md,
    borderWidth: 1.5,
    borderColor: Colors.borderLight,
    backgroundColor: Colors.surfaceWhite,
    alignItems: 'center',
  },
  selected: { borderColor: Colors.primaryDeepTeal, backgroundColor: '#E8F4F7' },
  label: {
    fontFamily: FontFamily.medium,
    fontSize: FontSize.sm,
    color: Colors.textMuted,
  },
  labelSelected: { color: Colors.primaryDeepTeal },
});

export default function BodaStoppedScreen() {
  const { language } = useAppStore();
  const router = useRouter();

  const [toldAbout, setToldAbout] = useState('');
  const [hasWrittenNotice, setHasWrittenNotice] = useState<YesNo>(null);
  const [penaltyMentioned, setPenaltyMentioned] = useState('');
  const [hasReference, setHasReference] = useState<YesNo>(null);
  const [additionalDetails, setAdditionalDetails] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSubmit = async () => {
    if (!toldAbout.trim()) {
      Alert.alert('Required', 'Please describe what the officer told you.');
      return;
    }
    setLoading(true);
    try {
      const res = await aiApi.bodaStopped({
        told_about: toldAbout,
        has_written_notice: hasWrittenNotice,
        penalty_mentioned: penaltyMentioned,
        has_reference: hasReference,
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
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.container}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.resultHeader}>
          <Text style={styles.resultEmoji}>🏍️</Text>
          <Text style={styles.resultTitle}>Your Guidance</Text>
        </View>

        {result.uncertainty_flag && <UncertaintyBanner />}

        <SectionCard
          title="Guidance for Your Situation"
          content={result.guidance}
          iconName="shield-checkmark"
          iconColor={Colors.primaryDeepTeal}
        />

        {result.legal_sources?.length > 0 && (
          <View style={styles.sourcesBox}>
            <Text style={styles.sourcesTitle}>{t('section_sources', language)}</Text>
            {result.legal_sources.map((src: any, i: number) => (
              <Text key={i} style={styles.sourceItem}>
                • {src.short_title || src.title}
              </Text>
            ))}
          </View>
        )}

        <TouchableOpacity
          style={styles.helpBtn}
          onPress={() => router.push('/legal-help')}
        >
          <Ionicons name="people" size={18} color={Colors.secondaryBurntOrange} />
          <Text style={styles.helpText}>{t('legalHelp_title', language)}</Text>
        </TouchableOpacity>

        <DisclaimerBanner message={result.disclaimer} />

        <Button
          label="Start Again"
          onPress={() => setResult(null)}
          variant="outline"
        />
      </ScrollView>
    );
  }

  return (
    <ScrollView
      style={styles.scroll}
      contentContainerStyle={styles.container}
      showsVerticalScrollIndicator={false}
    >
      <LoadingOverlay visible={loading} message={t('analyzing', language)} />

      <View style={styles.headerCard}>
        <Text style={styles.headerEmoji}>✋</Text>
        <Text style={styles.headerTitle}>{t('boda_stopped', language)}</Text>
        <Text style={styles.headerSub}>
          Answer a few questions so LegalBridge can give you relevant information.
        </Text>
      </View>

      {/* Q1 */}
      <View style={styles.questionBlock}>
        <Text style={styles.questionLabel}>{t('boda_stopped_q1', language)} *</Text>
        <TextInput
          style={styles.textArea}
          value={toldAbout}
          onChangeText={setToldAbout}
          multiline
          numberOfLines={3}
          placeholder="e.g. The officer said I was riding without a helmet / I had expired insurance..."
          placeholderTextColor={Colors.textMuted}
          textAlignVertical="top"
        />
      </View>

      {/* Q2 */}
      <View style={styles.questionBlock}>
        <Text style={styles.questionLabel}>{t('boda_stopped_q2', language)}</Text>
        <YesNoSelector value={hasWrittenNotice} onChange={setHasWrittenNotice} language={language} />
      </View>

      {/* Q3 */}
      <View style={styles.questionBlock}>
        <Text style={styles.questionLabel}>{t('boda_stopped_q3', language)}</Text>
        <TextInput
          style={styles.textInput}
          value={penaltyMentioned}
          onChangeText={setPenaltyMentioned}
          placeholder="e.g. UGX 50,000 / Not mentioned"
          placeholderTextColor={Colors.textMuted}
        />
      </View>

      {/* Q4 */}
      <View style={styles.questionBlock}>
        <Text style={styles.questionLabel}>{t('boda_stopped_q4', language)}</Text>
        <YesNoSelector value={hasReference} onChange={setHasReference} language={language} />
      </View>

      {/* Additional */}
      <View style={styles.questionBlock}>
        <Text style={styles.questionLabel}>
          {t('optional', language)}: Any other details?
        </Text>
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

      <Button
        label={t('boda_stopped_submit', language)}
        onPress={handleSubmit}
        loading={loading}
      />

      <DisclaimerBanner />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scroll: { flex: 1, backgroundColor: Colors.backgroundOffWhite },
  container: { padding: Spacing.base, paddingBottom: Spacing['3xl'], gap: Spacing.base },

  headerCard: {
    backgroundColor: Colors.primaryDeepPurple,
    borderRadius: BorderRadius.xl,
    padding: Spacing.xl,
    gap: Spacing.sm,
  },
  headerEmoji: { fontSize: 40 },
  headerTitle: {
    fontFamily: FontFamily.bold,
    fontSize: FontSize.xl,
    color: Colors.textOnPrimary,
  },
  headerSub: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.sm,
    color: Colors.accentSoftPeach,
    lineHeight: FontSize.sm * 1.6,
  },

  questionBlock: { gap: Spacing.sm },
  questionLabel: {
    fontFamily: FontFamily.semiBold,
    fontSize: FontSize.base,
    color: Colors.textPrimary,
  },
  textInput: {
    backgroundColor: Colors.surfaceWhite,
    borderRadius: BorderRadius.md,
    borderWidth: 1.5,
    borderColor: Colors.borderLight,
    paddingHorizontal: Spacing.base,
    paddingVertical: Spacing.md,
    fontFamily: FontFamily.regular,
    fontSize: FontSize.base,
    color: Colors.textPrimary,
    minHeight: 52,
  },
  textArea: {
    backgroundColor: Colors.surfaceWhite,
    borderRadius: BorderRadius.md,
    borderWidth: 1.5,
    borderColor: Colors.borderLight,
    paddingHorizontal: Spacing.base,
    paddingVertical: Spacing.md,
    fontFamily: FontFamily.regular,
    fontSize: FontSize.base,
    color: Colors.textPrimary,
    minHeight: 90,
  },

  resultHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.base,
    marginBottom: Spacing.sm,
  },
  resultEmoji: { fontSize: 36 },
  resultTitle: {
    fontFamily: FontFamily.bold,
    fontSize: FontSize.xl,
    color: Colors.textPrimary,
  },
  sourcesBox: {
    backgroundColor: Colors.surfaceLight,
    borderRadius: BorderRadius.md,
    padding: Spacing.base,
    gap: Spacing.xs,
  },
  sourcesTitle: {
    fontFamily: FontFamily.semiBold,
    fontSize: FontSize.xs,
    color: Colors.textMuted,
    textTransform: 'uppercase',
  },
  sourceItem: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.xs,
    color: Colors.textSecondary,
  },
  helpBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    backgroundColor: '#FEF0E8',
    borderRadius: BorderRadius.md,
    padding: Spacing.base,
  },
  helpText: {
    fontFamily: FontFamily.medium,
    fontSize: FontSize.sm,
    color: Colors.secondaryBurntOrange,
  },
});
