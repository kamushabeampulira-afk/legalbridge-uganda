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

export default function DocumentDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { language } = useAppStore();
  const router = useRouter();

  const [doc, setDoc] = useState<any>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [playingAudio, setPlayingAudio] = useState(false);
  const [sound, setSound] = useState<Audio.Sound | null>(null);

  const loadDocument = useCallback(async () => {
    try {
      const data = await documentsApi.getDetail(id!);
      setDoc(data);
      if (data.analysis) setAnalysis(data.analysis);
      else if (data.status === 'completed') triggerAnalysis();
    } catch {
      Alert.alert(t('alert_error', language), t('error_generic', language));
    } finally {
      setLoading(false);
    }
  }, [id, language]);

  const triggerAnalysis = async () => {
    setAnalyzing(true);
    try {
      const result = await documentsApi.analyze(id!, language);
      setAnalysis(result);
    } catch {
      Alert.alert(t('alert_analysisFailed', language), t('error_generic', language));
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
        <Text style={styles.headerIcon}>
          {doc?.doc_type === 'traffic_notice' ? '🚦' :
           doc?.doc_type === 'eviction_notice' ? '🏚️' :
           doc?.doc_type === 'allocation_slip' ? '📋' :
           doc?.doc_type === 'payment_receipt' ? '🧾' : '📄'}
        </Text>
        <View style={styles.headerInfo}>
          <Text style={styles.headerTitle}>{t('analysisTitle', language)}</Text>
          <Text style={styles.headerSub}>
            {doc?.doc_type?.replace(/_/g, ' ') ?? t('document_defaultTitle', language)}
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
            color={Colors.textOnPrimary}
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
            color={playingAudio ? Colors.warningMutedCoral : Colors.secondaryBurntOrange}
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
              iconColor={Colors.primaryDeepTeal}
            />
          ) : null}

          {analysis.what_it_means ? (
            <SectionCard
              title={t('section_meaning', language)}
              content={analysis.what_it_means}
              iconName="bulb"
              iconColor={Colors.secondaryBurntOrange}
              collapsible
            />
          ) : null}

          {analysis.relevant_law ? (
            <SectionCard
              title={t('section_law', language)}
              content={analysis.relevant_law}
              iconName="library"
              iconColor={Colors.successLeafGreen}
              collapsible
            />
          ) : null}

          {analysis.details_to_check ? (
            <SectionCard
              title={t('section_check', language)}
              content={analysis.details_to_check}
              iconName="checkmark-circle"
              iconColor={Colors.warningMutedCoral}
              collapsible
            />
          ) : null}

          {analysis.missing_information ? (
            <SectionCard
              title={t('section_missing', language)}
              content={analysis.missing_information}
              iconName="alert-circle"
              iconColor={Colors.warningMutedCoral}
              collapsible
            />
          ) : null}

          {analysis.next_steps?.length > 0 ? (
            <SectionCard
              title={t('section_steps', language)}
              content={analysis.next_steps}
              iconName="footsteps"
              iconColor={Colors.primaryDeepTeal}
            />
          ) : null}

          {analysis.where_to_get_help ? (
            <SectionCard
              title={t('section_help', language)}
              content={analysis.where_to_get_help}
              iconName="people"
              iconColor={Colors.successLeafGreen}
              collapsible
            />
          ) : null}

          {/* Sources */}
          {analysis.legal_sources_used?.length > 0 && (
            <View style={styles.sourcesBox}>
              <Text style={styles.sourcesTitle}>{t('section_sources', language)}</Text>
              {analysis.legal_sources_used.map((src: any, i: number) => (
                <Text key={i} style={styles.sourceItem}>
                  • {src.short_title || src.title}
                  {src.issuing_authority ? ` — ${src.issuing_authority}` : ''}
                </Text>
              ))}
            </View>
          )}
        </>
      ) : (
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
        <Ionicons name="chatbubble-ellipses" size={20} color={Colors.primaryDeepPurple} />
        <Text style={styles.followUpText}>{t('askFollowUp', language)}</Text>
        <Ionicons name="arrow-forward" size={16} color={Colors.primaryDeepPurple} />
      </TouchableOpacity>

      {/* Find legal help */}
      <TouchableOpacity
        style={styles.helpBtn}
        onPress={() => router.push('/legal-help')}
        activeOpacity={0.85}
      >
        <Ionicons name="people" size={20} color={Colors.secondaryGold} />
        <Text style={styles.helpBtnText}>{t('legalHelp_title', language)}</Text>
        <Ionicons name="arrow-forward" size={16} color={Colors.secondaryBurntOrange} />
      </TouchableOpacity>

      <DisclaimerBanner />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scroll: { flex: 1, backgroundColor: Colors.backgroundOffWhite },
  container: { padding: Spacing.base, paddingBottom: Spacing['3xl'], gap: Spacing.sm },

  header: {
    backgroundColor: Colors.primaryDeepPurple,
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
    color: Colors.accentSoftPeach, textTransform: 'capitalize', marginTop: 2,
  },
  audioBtn: {
    padding: Spacing.sm,
    backgroundColor: 'rgba(255,255,255,0.15)',
    borderRadius: BorderRadius.full,
    width: 44, height: 44,
    alignItems: 'center', justifyContent: 'center',
  },
  audioBtnActive: { backgroundColor: Colors.warningMutedCoral },

  listenRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    paddingVertical: Spacing.sm,
    paddingHorizontal: Spacing.base,
    backgroundColor: Colors.accentSoftPeach + '60',
    borderRadius: BorderRadius.md,
  },
  listenRowActive: { backgroundColor: Colors.warningLight },
  listenText: { flex: 1, fontFamily: FontFamily.medium, fontSize: FontSize.sm, color: Colors.secondaryBurntOrange },
  listenTextActive: { color: Colors.warningMutedCoral },
  freeBadge: {
    backgroundColor: Colors.successLeafGreen,
    paddingHorizontal: Spacing.sm,
    paddingVertical: 2,
    borderRadius: BorderRadius.full,
  },
  freeBadgeText: { fontFamily: FontFamily.semiBold, fontSize: 10, color: Colors.textOnPrimary },

  sourcesBox: {
    backgroundColor: Colors.surfaceLight,
    borderRadius: BorderRadius.md,
    padding: Spacing.base,
    gap: Spacing.xs,
  },
  sourcesTitle: {
    fontFamily: FontFamily.semiBold, fontSize: FontSize.xs,
    color: Colors.textMuted, textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: Spacing.xs,
  },
  sourceItem: { fontFamily: FontFamily.regular, fontSize: FontSize.xs, color: Colors.textSecondary, lineHeight: FontSize.xs * 1.6 },

  noAnalysis: { padding: Spacing.xl, alignItems: 'center', gap: Spacing.base },
  noAnalysisText: { fontFamily: FontFamily.regular, fontSize: FontSize.base, color: Colors.textMuted, textAlign: 'center' },
  retryBtn: { backgroundColor: Colors.primaryDeepTeal, paddingHorizontal: Spacing.xl, paddingVertical: Spacing.md, borderRadius: BorderRadius.lg },
  retryText: { fontFamily: FontFamily.semiBold, fontSize: FontSize.base, color: Colors.textOnPrimary },

  followUpBtn: {
    backgroundColor: '#EDE8F5', borderRadius: BorderRadius.lg, padding: Spacing.base,
    flexDirection: 'row', alignItems: 'center', gap: Spacing.sm,
  },
  followUpText: { flex: 1, fontFamily: FontFamily.medium, fontSize: FontSize.sm, color: Colors.primaryDeepPurple },

  helpBtn: {
    backgroundColor: '#FDF3DC', borderRadius: BorderRadius.lg, padding: Spacing.base,
    flexDirection: 'row', alignItems: 'center', gap: Spacing.sm,
  },
  helpBtnText: { flex: 1, fontFamily: FontFamily.medium, fontSize: FontSize.sm, color: Colors.secondaryGoldDark },
});
