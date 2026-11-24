/**
 * AI Explanation screen — displays document analysis results.
 * Includes audio playback via browser Web Speech API (web)
 * or OpenAI TTS (native).
 */
import React, { useEffect, useState, useCallback } from 'react';
import {
  View, Text, StyleSheet, ScrollView,
  TouchableOpacity, Alert, Platform,
} from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Audio } from 'expo-av';
import { documentsApi, voiceApi } from '@/services/api';
import { Colors } from '@/constants/Colors';
import { Spacing, BorderRadius } from '@/constants/Spacing';
import { webShadow } from '@/constants/Shadows';
import { FontFamily, FontSize } from '@/constants/Typography';
import { useAppStore } from '@/store/useAppStore';
import { t } from '@/i18n/translations';
import SectionCard from '@/components/ui/SectionCard';
import DisclaimerBanner from '@/components/ui/DisclaimerBanner';
import UncertaintyBanner from '@/components/ui/UncertaintyBanner';
import LoadingOverlay from '@/components/ui/LoadingOverlay';

// ── Browser-native TTS (web only, no API key required) ───────────────────────
function speakWithBrowser(text: string, lang: string = 'en'): boolean {
  if (Platform.OS !== 'web') return false;
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) return false;
  window.speechSynthesis.cancel();
  const utter = new (window as any).SpeechSynthesisUtterance(text);
  utter.lang = lang === 'lg' ? 'sw' : 'en-GB';
  utter.rate = 0.88;
  utter.pitch = 1.0;
  window.speechSynthesis.speak(utter);
  return true;
}

function stopBrowserSpeech() {
  if (Platform.OS === 'web' && typeof window !== 'undefined' && 'speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
}

function isBrowserSpeaking(): boolean {
  if (Platform.OS === 'web' && typeof window !== 'undefined' && 'speechSynthesis' in window) {
    return window.speechSynthesis.speaking;
  }
  return false;
}
// ─────────────────────────────────────────────────────────────────────────────

const DETAIL_FIELDS = [
  ['document_type', 'detail_document_type'],
  ['issuing_institution', 'detail_issuing_institution'],
  ['issuing_office', 'detail_issuing_office'],
  ['reference_numbers', 'detail_reference_numbers'],
  ['date_of_issue', 'detail_date_of_issue'],
  ['recipient', 'detail_recipient'],
  ['subject_or_offence', 'detail_subject_or_offence'],
  ['deadlines', 'detail_deadlines'],
  ['amounts', 'detail_amounts'],
  ['instructions', 'detail_instructions'],
  ['signature_or_stamp', 'detail_signature_or_stamp'],
  ['contact_information', 'detail_contact_information'],
  ['legal_provisions_mentioned', 'detail_legal_provisions_mentioned'],
] as const;

function docIcon(docType?: string): string {
  if (!docType) return '📄';
  if (docType.startsWith('traffic') || docType.startsWith('vehicle')) return '🚦';
  if (docType.startsWith('police') || docType === 'complaint_to_police') return '👮';
  if (docType === 'court_summons') return '⚖️';
  if (['eviction_notice', 'trading_space_vacate_notice', 'landlord_correspondence'].includes(docType)) return '🏚️';
  if (['allocation_slip', 'trading_licence', 'market_notice', 'local_authority_notice'].includes(docType)) return '📋';
  if (['payment_receipt', 'rent_record'].includes(docType)) return '🧾';
  return '📄';
}

function verificationStyle(status?: string) {
  if (status === 'verified_official') return styles.statusVerified;
  if (status === 'verification_incomplete') return styles.statusNeutral;
  if (status === 'type_identified') return styles.statusInfo;
  return styles.statusCaution;
}

export default function DocumentDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { language } = useAppStore();
  const router = useRouter();

  const [doc, setDoc] = useState<any>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [playingAudio, setPlayingAudio] = useState(false);
  const [sound, setSound] = useState<Audio.Sound | null>(null);

  const loadDocument = useCallback(async () => {
    try {
      const data = await documentsApi.getDetail(id!);
      setDoc(data);
      if (data.analysis) setAnalysis(data.analysis);
      else if (data.status === 'completed') triggerAnalysis();
    } catch {
      setLoadError(t('error_generic', language));
    } finally {
      setLoading(false);
    }
  }, [id, language]);

  const triggerAnalysis = async () => {
    setAnalyzing(true);
    setAnalysisError(null);
    try {
      const result = await documentsApi.analyze(id!, language);
      setAnalysis(result);
    } catch (err: any) {
      // Shown on screen (Alert.alert does nothing on web)
      setAnalysisError(err?.message || t('error_generic', language));
    } finally {
      setAnalyzing(false);
    }
  };

  useEffect(() => {
    loadDocument();
    return () => {
      sound?.unloadAsync();
      stopBrowserSpeech();
    };
  }, []);

  // ── Audio playback ──────────────────────────────────────────────────────────
  const handlePlayAudio = async () => {
    if (!analysis) return;

    // Already playing → stop
    if (playingAudio) {
      stopBrowserSpeech();
      await sound?.stopAsync();
      setPlayingAudio(false);
      return;
    }

    const textToRead = [
      analysis.summary,
      analysis.what_it_means,
    ].filter(Boolean).join('. ').slice(0, 1500);

    if (!textToRead) return;

    // Web: use browser speech synthesis (free, no API needed)
    if (Platform.OS === 'web') {
      const started = speakWithBrowser(textToRead, language);
      if (started) {
        setPlayingAudio(true);
        // Poll for end of speech
        const interval = setInterval(() => {
          if (!isBrowserSpeaking()) {
            setPlayingAudio(false);
            clearInterval(interval);
          }
        }, 500);
      }
      return;
    }

    // Native: try backend TTS (requires OpenAI credits)
    // Fall back to browser speech if unavailable
    try {
      setPlayingAudio(true);
      const result = await voiceApi.synthesize(textToRead, language);
      if (result.audio_url) {
        const { sound: newSound } = await Audio.Sound.createAsync({ uri: result.audio_url });
        setSound(newSound);
        await newSound.playAsync();
        newSound.setOnPlaybackStatusUpdate((status) => {
          if (!status.isLoaded || (status as any).didJustFinish) setPlayingAudio(false);
        });
      } else {
        setPlayingAudio(false);
        Alert.alert(
          t('alert_voiceUnavailable', language),
          result.warning ?? t('voice_synthesisUnavailable', language)
        );
      }
    } catch {
      setPlayingAudio(false);
    }
  };

  if (loading || analyzing) {
    return (
      <LoadingOverlay
        visible
        message={analyzing ? t('analyzing', language) : t('loading', language)}
      />
    );
  }

  return (
    <ScrollView
      style={styles.scroll}
      contentContainerStyle={styles.container}
      showsVerticalScrollIndicator={false}
    >
      {/* Doc header */}
      <View style={[styles.header, webShadow.md]}>
        <Text style={styles.headerIcon}>{docIcon(doc?.doc_type)}</Text>
        <View style={styles.headerInfo}>
          <Text style={styles.headerTitle}>{t('analysisTitle', language)}</Text>
          <Text style={styles.headerSub}>
            {doc?.doc_type_label ?? doc?.doc_type?.replace(/_/g, ' ') ?? t('document_defaultTitle', language)}
          </Text>
        </View>
        {/* Audio button in header */}
        <TouchableOpacity
          style={[styles.audioBtn, playingAudio && styles.audioBtnActive]}
          onPress={handlePlayAudio}
          disabled={!analysis}
          accessibilityLabel={playingAudio ? t('voice_stop', language) : t('listenToExplanation', language)}
        >
          <Ionicons
            name={playingAudio ? 'stop-circle' : 'volume-high'}
            size={26}
            color={playingAudio ? Colors.primary : Colors.textOnPrimary}
          />
        </TouchableOpacity>
      </View>

      {/* Audio listen row */}
      {analysis && (
        <TouchableOpacity
          style={[styles.listenRow, playingAudio && styles.listenRowActive]}
          onPress={handlePlayAudio}
          activeOpacity={0.8}
        >
          <Ionicons
            name={playingAudio ? 'stop-circle' : 'play-circle'}
            size={22}
            color={playingAudio ? Colors.primary : Colors.secondary}
          />
          <Text style={[styles.listenText, playingAudio && styles.listenTextActive]}>
            {playingAudio
              ? t('document_stopAudio', language)
              : t('listenToExplanation', language)}
          </Text>
          {Platform.OS === 'web' && !playingAudio && (
            <View style={styles.freeBadge}>
              <Text style={styles.freeBadgeText}>{t('document_free', language)}</Text>
            </View>
          )}
        </TouchableOpacity>
      )}

      {loadError && (
        <View style={[styles.statusCard, styles.statusError]}>
          <Text style={styles.statusTitle}>{loadError}</Text>
        </View>
      )}

      {/* Authenticity: recognising a document is not the same as verifying it */}
      {doc?.verification_status_label ? (
        <View style={[styles.statusCard, verificationStyle(doc.verification_status)]}>
          <View style={styles.statusRow}>
            <Ionicons
              name={doc.verification_status === 'verified_official' ? 'shield-checkmark' : 'shield-half'}
              size={18}
              color={Colors.textSecondary}
            />
            <Text style={styles.statusTitle}>{doc.verification_status_label}</Text>
          </View>
          {doc.verification_guidance ? (
            <Text style={styles.statusBody}>{doc.verification_guidance}</Text>
          ) : null}
        </View>
      ) : null}

      {/* What LegalBridge read from the document */}
      {doc?.document_details && Object.keys(doc.document_details).length > 0 && (
        <View style={styles.detailsBox}>
          <Text style={styles.sourcesTitle}>{t('detail_title', language)}</Text>
          {DETAIL_FIELDS.map(([key, labelKey]) => {
            const field = doc.document_details[key];
            if (!field || !['found', 'unclear'].includes(field.status) || !field.value) return null;
            const value = Array.isArray(field.value) ? field.value.join(' · ') : String(field.value);
            return (
              <View key={key} style={styles.detailRow}>
                <Text style={styles.detailLabel}>{t(labelKey, language)}</Text>
                <Text style={styles.detailValue}>{value}</Text>
                {field.status === 'unclear' && (
                  <Text style={styles.detailUnclear}>{t('detail_unclear', language)}: {field.note}</Text>
                )}
              </View>
            );
          })}
          <Text style={styles.detailFootnote}>
            {t('detail_footnote', language)}
          </Text>
        </View>
      )}

      {/* Analysis could not be generated: say why, keep the details above, allow retry */}
      {analysisError && !analysis && (
        <View style={[styles.statusCard, styles.statusError]}>
          <Text style={styles.statusTitle}>{t('analysis_unavailable', language)}</Text>
          <Text style={styles.statusBody}>{analysisError}</Text>
          <TouchableOpacity style={styles.retryBtn} onPress={triggerAnalysis}>
            <Text style={styles.retryText}>{t('retry', language)}</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Uncertainty flag */}
      {analysis?.uncertainty_flag && <UncertaintyBanner />}

      {/* Analysis sections */}
      {analysis ? (
        <>
          {analysis.summary ? (
            <SectionCard
              title={t('section_summary', language)}
              content={analysis.summary}
              iconName="document-text"
              iconColor={Colors.primary}
            />
          ) : null}

          {analysis.what_it_means ? (
            <SectionCard
              title={t('section_meaning', language)}
              content={analysis.what_it_means}
              iconName="bulb"
              iconColor={Colors.secondary}
              collapsible
            />
          ) : null}

          {analysis.relevant_law ? (
            <SectionCard
              title={t('section_law', language)}
              content={analysis.relevant_law}
              iconName="library"
              iconColor={Colors.success}
              collapsible
            />
          ) : null}

          {analysis.details_to_check ? (
            <SectionCard
              title={t('section_check', language)}
              content={analysis.details_to_check}
              iconName="checkmark-circle"
              iconColor={Colors.warning}
              collapsible
            />
          ) : null}

          {analysis.missing_information ? (
            <SectionCard
              title={t('section_missing', language)}
              content={analysis.missing_information}
              iconName="alert-circle"
              iconColor={Colors.warning}
              collapsible
            />
          ) : null}

          {analysis.next_steps?.length > 0 ? (
            <SectionCard
              title={t('section_steps', language)}
              content={analysis.next_steps}
              iconName="footsteps"
              iconColor={Colors.primary}
            />
          ) : null}

          {analysis.where_to_get_help ? (
            <SectionCard
              title={t('section_help', language)}
              content={analysis.where_to_get_help}
              iconName="people"
              iconColor={Colors.success}
              collapsible
            />
          ) : null}

          {/* Sources */}
          {analysis.legal_sources_used?.length > 0 && (
            <View style={styles.sourcesBox}>
              <Text style={styles.sourcesTitle}>{t('section_sources', language)}</Text>
              {analysis.legal_sources_used.map((src: any, i: number) => (
                <View key={i} style={styles.sourceEntry}>
                  <Text style={styles.sourceItem}>
                    • {src.title || src.short_title}
                    {src.instrument_number ? ` (${src.instrument_number})` : ''}
                    {src.section_number ? `, section ${src.section_number}` : ''}
                    {src.section_title ? `: ${src.section_title}` : ''}
                  </Text>
                  <Text style={styles.sourceMeta}>
                    {[
                      src.issuing_authority,
                      src.legal_status ? `Status: ${src.legal_status}` : null,
                      src.last_verified_at ? `Last verified ${src.last_verified_at}` : null,
                    ].filter(Boolean).join(' · ')}
                  </Text>
                  {src.source_url ? <Text style={styles.sourceMeta}>{src.source_url}</Text> : null}
                  {src.is_current_verified === false && (
                    <Text style={styles.detailUnclear}>
                      Not verified as current law
                      {src.currency_warnings?.length ? `: ${src.currency_warnings.join(' ')}` : ''}
                    </Text>
                  )}
                </View>
              ))}
            </View>
          )}
        </>
      ) : analysisError ? null : (
        <View style={styles.noAnalysis}>
          <Text style={styles.noAnalysisText}>
            {doc?.status === 'processing'
              ? t('document_processingWait', language)
              : t('document_notAvailable', language)}
          </Text>
          {doc?.status === 'completed' && (
            <TouchableOpacity style={styles.retryBtn} onPress={triggerAnalysis}>
              <Text style={styles.retryText}>{t('document_analyseNow', language)}</Text>
            </TouchableOpacity>
          )}
        </View>
      )}

      {/* Ask follow-up */}
      <TouchableOpacity
        style={styles.followUpBtn}
        onPress={() => router.push('/ask' as any)}
        activeOpacity={0.85}
      >
        <Ionicons name="chatbubble-ellipses" size={20} color={Colors.primary} />
        <Text style={styles.followUpText}>{t('askFollowUp', language)}</Text>
        <Ionicons name="arrow-forward" size={16} color={Colors.primary} />
      </TouchableOpacity>

      {/* Find legal help */}
      <TouchableOpacity
        style={styles.helpBtn}
        onPress={() => router.push('/legal-help')}
        activeOpacity={0.85}
      >
        <Ionicons name="people" size={20} color={Colors.accentStrong} />
        <Text style={styles.helpBtnText}>{t('legalHelp_title', language)}</Text>
        <Ionicons name="arrow-forward" size={16} color={Colors.accentStrong} />
      </TouchableOpacity>

      <DisclaimerBanner />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scroll: { flex: 1, backgroundColor: Colors.background },
  container: { padding: Spacing.base, paddingBottom: Spacing['3xl'], gap: Spacing.sm },

  header: {
    backgroundColor: Colors.primary,
    borderRadius: BorderRadius.xl,
    padding: Spacing.base,
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    marginBottom: Spacing.sm,
  },
  headerIcon: { fontSize: 36 },
  headerInfo: { flex: 1 },
  headerTitle: { fontFamily: FontFamily.bold, fontSize: FontSize.md, color: Colors.textOnPrimary },
  headerSub: {
    fontFamily: FontFamily.regular, fontSize: FontSize.xs,
    color: Colors.textOnPrimaryMuted, textTransform: 'capitalize', marginTop: 2,
  },
  audioBtn: {
    padding: Spacing.sm,
    backgroundColor: Colors.onPrimarySubtle,
    borderRadius: BorderRadius.full,
    width: 44, height: 44,
    alignItems: 'center', justifyContent: 'center',
  },
  audioBtnActive: { backgroundColor: Colors.surface },

  listenRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    paddingVertical: Spacing.sm,
    paddingHorizontal: Spacing.base,
    backgroundColor: Colors.secondaryTint,
    borderRadius: BorderRadius.md,
  },
  listenRowActive: { backgroundColor: Colors.primaryTint },
  listenText: { flex: 1, fontFamily: FontFamily.medium, fontSize: FontSize.sm, color: Colors.secondaryText },
  listenTextActive: { color: Colors.primary },
  freeBadge: {
    backgroundColor: Colors.success,
    paddingHorizontal: Spacing.sm,
    paddingVertical: 2,
    borderRadius: BorderRadius.full,
  },
  freeBadgeText: { fontFamily: FontFamily.semiBold, fontSize: 10, color: Colors.textOnPrimary },

  sourcesBox: {
    backgroundColor: Colors.surfaceMuted,
    borderRadius: BorderRadius.md,
    padding: Spacing.base,
    gap: Spacing.xs,
  },
  sourcesTitle: {
    fontFamily: FontFamily.semiBold, fontSize: FontSize.xs,
    color: Colors.textMuted, textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: Spacing.xs,
  },
  sourceItem: { fontFamily: FontFamily.regular, fontSize: FontSize.xs, color: Colors.textSecondary, lineHeight: FontSize.xs * 1.6 },
  sourceEntry: { marginBottom: Spacing.xs },
  sourceMeta: { fontFamily: FontFamily.regular, fontSize: 11, color: Colors.textMuted, marginLeft: Spacing.sm },

  statusCard: { borderRadius: BorderRadius.md, padding: Spacing.base, gap: Spacing.xs, borderWidth: 1 },
  statusRow: { flexDirection: 'row', alignItems: 'center', gap: Spacing.xs },
  statusTitle: { flex: 1, fontFamily: FontFamily.semiBold, fontSize: FontSize.sm, color: Colors.textPrimary },
  statusBody: { fontFamily: FontFamily.regular, fontSize: FontSize.xs, color: Colors.textSecondary, lineHeight: FontSize.xs * 1.6 },
  statusCaution: { backgroundColor: Colors.warningBg, borderColor: Colors.warningBorder },
  statusInfo: { backgroundColor: Colors.infoBg, borderColor: Colors.infoBorder },
  statusNeutral: { backgroundColor: Colors.surfaceMuted, borderColor: Colors.border },
  statusVerified: { backgroundColor: Colors.successBg, borderColor: Colors.successBorder },
  statusError: { backgroundColor: Colors.errorBg, borderColor: Colors.errorBorder },

  detailsBox: { backgroundColor: Colors.surface, borderRadius: BorderRadius.md, padding: Spacing.base, gap: Spacing.sm, borderWidth: 1, borderColor: Colors.border },
  detailRow: { gap: 2 },
  detailLabel: { fontFamily: FontFamily.semiBold, fontSize: 11, color: Colors.textMuted, textTransform: 'uppercase', letterSpacing: 0.4 },
  detailValue: { fontFamily: FontFamily.regular, fontSize: FontSize.sm, color: Colors.textPrimary },
  detailUnclear: { fontFamily: FontFamily.regular, fontSize: 11, color: Colors.warning },
  detailFootnote: { fontFamily: FontFamily.regular, fontSize: 11, color: Colors.textMuted, fontStyle: 'italic' },

  noAnalysis: { padding: Spacing.xl, alignItems: 'center', gap: Spacing.base },
  noAnalysisText: { fontFamily: FontFamily.regular, fontSize: FontSize.base, color: Colors.textMuted, textAlign: 'center' },
  retryBtn: { backgroundColor: Colors.primary, paddingHorizontal: Spacing.xl, paddingVertical: Spacing.md, borderRadius: BorderRadius.lg },
  retryText: { fontFamily: FontFamily.semiBold, fontSize: FontSize.base, color: Colors.textOnPrimary },

  followUpBtn: {
    backgroundColor: Colors.primaryTint, borderRadius: BorderRadius.lg, padding: Spacing.base,
    flexDirection: 'row', alignItems: 'center', gap: Spacing.sm,
  },
  followUpText: { flex: 1, fontFamily: FontFamily.medium, fontSize: FontSize.sm, color: Colors.primary },

  helpBtn: {
    backgroundColor: Colors.accentTint, borderRadius: BorderRadius.lg, padding: Spacing.base,
    flexDirection: 'row', alignItems: 'center', gap: Spacing.sm,
  },
  helpBtnText: { flex: 1, fontFamily: FontFamily.medium, fontSize: FontSize.sm, color: Colors.accentText },
});
