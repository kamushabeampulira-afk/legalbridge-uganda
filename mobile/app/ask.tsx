/**
 * Ask LegalBridge — free-text legal question screen.
 */
import React, { useState } from 'react';
import {
  View, Text, StyleSheet, ScrollView,
  TextInput, TouchableOpacity, Alert, KeyboardAvoidingView, Platform,
} from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { legalApi } from '@/services/api';
import { Colors } from '@/constants/Colors';
import { Spacing, BorderRadius } from '@/constants/Spacing';
import { webShadow } from '@/constants/Shadows';
import { FontFamily, FontSize } from '@/constants/Typography';
import { useAppStore } from '@/store/useAppStore';
import { t } from '@/i18n/translations';
import Button from '@/components/ui/Button';
import SectionCard from '@/components/ui/SectionCard';
import DisclaimerBanner from '@/components/ui/DisclaimerBanner';
import UncertaintyBanner from '@/components/ui/UncertaintyBanner';
import LoadingOverlay from '@/components/ui/LoadingOverlay';

const PRESET_QUESTIONS: Record<string, { en: string; lg: string }[]> = {
  boda_boda: [
    { en: 'What documents must I carry when riding my boda boda?', lg: 'Empapula ki ezinaabikibwa ng\'nkuba boda boda?' },
    { en: 'What should I do when stopped by a traffic officer?', lg: 'Nkole ki poliisi ng\'yansinzya ku kkubo?' },
    { en: 'What are the official payment procedures for traffic fines?', lg: 'Enkola ki y\'okusasula emisango gy\'ekkubo?' },
    { en: 'Is an officer allowed to take my motorcycle?', lg: 'Omusirikale asobola okutwala boda yange?' },
  ],
  market_vendor: [
    { en: 'What rights do I have as a market vendor?', lg: 'Eddembe ki ly\'olina nga omusuubuzi wa akatale?' },
    { en: 'Can I be evicted from my stall without written notice?', lg: 'Basobola okuggya ku essimbi lyange nga batandiikidde?' },
    { en: 'What should an allocation slip include?', lg: 'Pepa ly\'okuweebwayo linaabikibwa ki?' },
    { en: 'What can I do if I receive an eviction notice?', lg: 'Nkole ki ng\'nkuwa obubaka bw\'okufulumizibwa?' },
  ],
};

export default function AskScreen() {
  const params = useLocalSearchParams<{ category?: string; preset?: string }>();
  const { language } = useAppStore();
  const router = useRouter();

  const userCategory = params.category ?? 'general';
  const presets = PRESET_QUESTIONS[userCategory] ?? [];

  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleAsk = async (q?: string) => {
    const finalQuestion = (q ?? question).trim();
    if (!finalQuestion) {
      Alert.alert('Required', 'Please enter your question.');
      return;
    }
    if (finalQuestion.length > 2000) {
      Alert.alert('Too long', 'Please keep your question under 2000 characters.');
      return;
    }
    setLoading(true);
    setResult(null);
    try {
      const res = await legalApi.ask(finalQuestion, userCategory, language);
      setResult({ ...res, question: finalQuestion });
    } catch (err: any) {
      Alert.alert('Error', err.message ?? t('error_generic', language));
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={{ flex: 1 }}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.container}
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
      >
        <LoadingOverlay visible={loading} message={t('analyzing', language)} />

        {/* Header */}
        <View style={styles.header}>
          <Ionicons name="chatbubble-ellipses" size={28} color={Colors.textOnPrimary} />
          <View>
            <Text style={styles.headerTitle}>{t('home_askLegal', language)}</Text>
            <Text style={styles.headerSub}>Ask any question about Ugandan law</Text>
          </View>
        </View>

        {/* Input */}
        <View style={styles.inputCard}>
          <TextInput
            style={styles.textArea}
            value={question}
            onChangeText={setQuestion}
            placeholder={
              language === 'lg'
                ? 'Wandiika ekibuuzo kyo wano...'
                : 'Type your legal question here...'
            }
            placeholderTextColor={Colors.textMuted}
            multiline
            numberOfLines={4}
            textAlignVertical="top"
            maxLength={2000}
          />
          <View style={styles.inputFooter}>
            <Text style={styles.charCount}>{question.length}/2000</Text>
            <TouchableOpacity
              style={[styles.sendBtn, !question.trim() && styles.sendBtnDisabled]}
              onPress={() => handleAsk()}
              disabled={!question.trim() || loading}
              accessibilityLabel="Submit question"
            >
              <Ionicons name="send" size={20} color={Colors.textOnPrimary} />
            </TouchableOpacity>
          </View>
        </View>

        {/* Voice shortcut */}
        <TouchableOpacity
          style={styles.voiceRow}
          onPress={() => router.push('/voice')}
          activeOpacity={0.8}
        >
          <Ionicons name="mic" size={18} color={Colors.secondary} />
          <Text style={styles.voiceText}>
            {language === 'lg' ? 'Yogera ekibuuzo kyo' : 'Prefer to speak your question?'}
          </Text>
          <Ionicons name="chevron-forward" size={16} color={Colors.textMuted} />
        </TouchableOpacity>

        {/* Result */}
        {result && (
          <View style={styles.resultSection}>
            <View style={styles.questionBubble}>
              <Ionicons name="person-circle" size={18} color={Colors.primary} />
              <Text style={styles.questionText}>{result.question}</Text>
            </View>

            {result.uncertainty_flag && <UncertaintyBanner />}

            <SectionCard
              title="LegalBridge Answer"
              content={result.answer}
              iconName="shield-checkmark"
              iconColor={Colors.primary}
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

            <TouchableOpacity style={styles.helpBtn} onPress={() => router.push('/legal-help')}>
              <Ionicons name="people" size={18} color={Colors.accentStrong} />
              <Text style={styles.helpText}>{t('legalHelp_title', language)}</Text>
            </TouchableOpacity>

            <DisclaimerBanner message={result.disclaimer} />

            <Button
              label="Ask Another Question"
              onPress={() => { setResult(null); setQuestion(''); }}
              variant="outline"
            />
          </View>
        )}

        {/* Preset questions */}
        {!result && presets.length > 0 && (
          <View style={styles.presetsSection}>
            <Text style={styles.presetsTitle}>Common questions</Text>
            {presets.map((p, i) => (
              <TouchableOpacity
                key={i}
                style={styles.presetCard}
                onPress={() => {
                  const q = language === 'lg' ? p.lg : p.en;
                  setQuestion(q);
                  handleAsk(q);
                }}
                activeOpacity={0.8}
              >
                <Text style={styles.presetText}>{language === 'lg' ? p.lg : p.en}</Text>
                <Ionicons name="arrow-forward-circle" size={20} color={Colors.primary} />
              </TouchableOpacity>
            ))}
          </View>
        )}

        <DisclaimerBanner />
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  scroll: { flex: 1, backgroundColor: Colors.background },
  container: { padding: Spacing.base, paddingBottom: Spacing['3xl'], gap: Spacing.base },

  header: {
    backgroundColor: Colors.primary,
    borderRadius: BorderRadius.xl,
    padding: Spacing.xl,
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.base,
  },
  headerTitle: { fontFamily: FontFamily.bold, fontSize: FontSize.lg, color: Colors.textOnPrimary },
  headerSub: { fontFamily: FontFamily.regular, fontSize: FontSize.xs, color: Colors.textOnPrimaryMuted, marginTop: 2 },

  inputCard: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.xl,
    padding: Spacing.base,
  },
  textArea: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.base,
    color: Colors.textPrimary,
    minHeight: 100,
    textAlignVertical: 'top',
    lineHeight: FontSize.base * 1.6,
  },
  inputFooter: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: Spacing.sm,
    borderTopWidth: 1,
    borderTopColor: Colors.border,
    paddingTop: Spacing.sm,
  },
  charCount: { fontFamily: FontFamily.regular, fontSize: FontSize.xs, color: Colors.textMuted },
  sendBtn: {
    backgroundColor: Colors.primary,
    width: 42,
    height: 42,
    borderRadius: 21,
    alignItems: 'center',
    justifyContent: 'center',
  },
  sendBtnDisabled: { opacity: 0.4 },

  voiceRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    backgroundColor: Colors.secondaryTint,
    borderRadius: BorderRadius.md,
    padding: Spacing.base,
  },
  voiceText: { flex: 1, fontFamily: FontFamily.medium, fontSize: FontSize.sm, color: Colors.secondaryText },

  resultSection: { gap: Spacing.sm },
  questionBubble: {
    flexDirection: 'row',
    gap: Spacing.sm,
    alignItems: 'flex-start',
    backgroundColor: Colors.surfaceMuted,
    borderRadius: BorderRadius.md,
    padding: Spacing.base,
  },
  questionText: {
    flex: 1,
    fontFamily: FontFamily.medium,
    fontSize: FontSize.sm,
    color: Colors.textPrimary,
    lineHeight: FontSize.sm * 1.6,
  },

  sourcesBox: { backgroundColor: Colors.surfaceMuted, borderRadius: BorderRadius.md, padding: Spacing.base, gap: Spacing.xs },
  sourcesTitle: { fontFamily: FontFamily.semiBold, fontSize: FontSize.xs, color: Colors.textMuted, textTransform: 'uppercase' },
  sourceItem: { fontFamily: FontFamily.regular, fontSize: FontSize.xs, color: Colors.textSecondary },

  helpBtn: {
    flexDirection: 'row', alignItems: 'center', gap: Spacing.sm,
    backgroundColor: Colors.accentTint, borderRadius: BorderRadius.md, padding: Spacing.base,
  },
  helpText: { fontFamily: FontFamily.medium, fontSize: FontSize.sm, color: Colors.accentText },

  presetsSection: { gap: Spacing.sm },
  presetsTitle: {
    fontFamily: FontFamily.semiBold, fontSize: FontSize.sm,
    color: Colors.textSecondary, textTransform: 'uppercase', letterSpacing: 0.5,
  },
  presetCard: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.base,
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
  },
  presetText: { flex: 1, fontFamily: FontFamily.regular, fontSize: FontSize.sm, color: Colors.textPrimary, lineHeight: FontSize.sm * 1.6 },
});
