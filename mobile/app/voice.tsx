/**
 * Voice interaction screen — record question, receive spoken answer.
 */
import React, { useState, useRef, useEffect } from 'react';
import {
  View, Text, TextInput, StyleSheet, ScrollView,
  TouchableOpacity, Alert, Animated, Platform,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Audio } from 'expo-av';
import { Ionicons } from '@expo/vector-icons';
import { voiceApi, legalApi } from '@/services/api';
import { Colors } from '@/constants/Colors';
import { Spacing, BorderRadius } from '@/constants/Spacing';
import { webShadow } from '@/constants/Shadows';
import { FontFamily, FontSize } from '@/constants/Typography';
import { useAppStore } from '@/store/useAppStore';
import { t, type Language } from '@/i18n/translations';
import { getLanguageMeta } from '@/i18n/languages';
import DisclaimerBanner from '@/components/ui/DisclaimerBanner';
import UncertaintyBanner from '@/components/ui/UncertaintyBanner';
import SectionCard from '@/components/ui/SectionCard';
import LoadingOverlay from '@/components/ui/LoadingOverlay';

// ── Browser-native TTS (web only, no API key or voice ID required) ───────────
function speakWithBrowser(text: string, lang: Language): boolean {
  if (Platform.OS !== 'web') return false;
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) return false;
  window.speechSynthesis.cancel();
  const utter = new (window as any).SpeechSynthesisUtterance(text);
  const voices = window.speechSynthesis.getVoices();
  const meta = getLanguageMeta(lang);
  const prefix = meta.bcp47.split('-')[0].toLowerCase();
  // Prefer the selected language; fall back to English when no voice exists.
  const preferred = voices.find((v: any) => v.lang.toLowerCase().startsWith(prefix))
    ?? voices.find((v: any) => v.lang.toLowerCase().startsWith('en'));
  if (preferred) utter.voice = preferred;
  utter.lang = meta.bcp47;
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

type State = 'idle' | 'recording' | 'processing' | 'transcribed' | 'answered';

export default function VoiceScreen() {
  const { language, user } = useAppStore();
  const router = useRouter();

  const [state, setState] = useState<State>('idle');
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [transcription, setTranscription] = useState('');
  const [transcriptionWarning, setTranscriptionWarning] = useState('');
  const [result, setResult] = useState<any>(null);
  const [playingAudio, setPlayingAudio] = useState(false);
  const [sound, setSound] = useState<Audio.Sound | null>(null);
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const speechPoll = useRef<ReturnType<typeof setInterval> | null>(null);

  // ── Recording ─────────────────────────────────────────────────────────────

  const startRecording = async () => {
    try {
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert(t('alert_permissionNeeded', language), t('voice_microphonePermission', language));
        return;
      }
      await Audio.setAudioModeAsync({ allowsRecordingIOS: true, playsInSilentModeIOS: true });
      const { recording: rec } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      setRecording(rec);
      setState('recording');
      startPulse();
    } catch (e) {
      Alert.alert(t('alert_recordingFailed', language), t('voice_recordingRetry', language));
    }
  };

  const stopRecording = async () => {
    if (!recording) return;
    stopPulse();
    setState('processing');
    try {
      await recording.stopAndUnloadAsync();
      await Audio.setAudioModeAsync({ allowsRecordingIOS: false });
      const uri = recording.getURI();
      setRecording(null);

      if (!uri) throw new Error('No audio recorded.');

      // Transcribe
      const result = await voiceApi.transcribe(uri, language);
      if (!result.transcription) {
        setTranscription('');
        setTranscriptionWarning(t('voice_fallback', language));
        setState('transcribed');
        return;
      }
      setTranscription(result.transcription);
      // The server's warning text is English; show the app's translation instead.
      setTranscriptionWarning(result.warning ? t('voice_accuracy_warning', language) : '');
      setState('transcribed');
    } catch (err: any) {
      setTranscription('');
      setTranscriptionWarning(t('voice_fallback', language));
      setState('transcribed');
    }
  };

  // ── Answer playback ────────────────────────────────────────────────────────
  const clearSpeechPoll = () => {
    if (speechPoll.current) {
      clearInterval(speechPoll.current);
      speechPoll.current = null;
    }
  };

  const stopAudio = async () => {
    clearSpeechPoll();
    stopBrowserSpeech();
    await sound?.stopAsync();
    setPlayingAudio(false);
  };

  const playAnswer = async (answerText?: string) => {
    const text = (answerText ?? result?.answer ?? '').slice(0, 800);
    if (!text) return;

    await stopAudio();

    // Web: browser speech synthesis works without any API key or Luganda voice ID.
    if (Platform.OS === 'web' && speakWithBrowser(text, language)) {
      setPlayingAudio(true);
      speechPoll.current = setInterval(() => {
        if (!isBrowserSpeaking()) {
          clearSpeechPoll();
          setPlayingAudio(false);
        }
      }, 500);
      return;
    }

    // Native: backend TTS (needs a configured provider and key).
    try {
      const audioRes = await voiceApi.synthesize(text, language);
      if (audioRes.audio_url) {
        const { sound: s } = await Audio.Sound.createAsync({ uri: audioRes.audio_url });
        setSound(s);
        setPlayingAudio(true);
        await s.playAsync();
        s.setOnPlaybackStatusUpdate((status) => {
          if (!status.isLoaded || (status as any).didJustFinish) setPlayingAudio(false);
        });
      } else {
        Alert.alert(
          t('alert_voiceUnavailable', language),
          t('voice_synthesisUnavailable', language)
        );
      }
    } catch {
      Alert.alert(t('alert_voiceUnavailable', language), t('voice_synthesisUnavailable', language));
    }
  };

  useEffect(() => () => {
    clearSpeechPoll();
    stopBrowserSpeech();
    sound?.unloadAsync();
  }, []);

  const submitTranscription = async () => {
    if (!transcription.trim()) {
      Alert.alert(t('alert_noText', language), t('voice_fallback', language));
      return;
    }
    setState('processing');
    try {
      const res = await legalApi.ask(
        transcription,
        user?.user_type ?? 'general',
        language
      );
      setResult(res);
      setState('answered');

      // Speak the answer (browser TTS on web, backend TTS on native)
      if (res.answer && !res.uncertainty_flag) {
        await playAnswer(res.answer);
      }
    } catch (err: any) {
      Alert.alert(t('alert_error', language), err.message ?? t('error_generic', language));
      setState('transcribed');
    }
  };

  const reset = () => {
    clearSpeechPoll();
    stopBrowserSpeech();
    sound?.unloadAsync();
    setSound(null);
    setPlayingAudio(false);
    setTranscription('');
    setTranscriptionWarning('');
    setResult(null);
    setState('idle');
  };

  // ── Pulse animation ───────────────────────────────────────────────────────

  const startPulse = () => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, { toValue: 1.3, duration: 600, useNativeDriver: true }),
        Animated.timing(pulseAnim, { toValue: 1, duration: 600, useNativeDriver: true }),
      ])
    ).start();
  };

  const stopPulse = () => {
    pulseAnim.stopAnimation();
    pulseAnim.setValue(1);
  };

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <ScrollView style={styles.scroll} contentContainerStyle={styles.container} showsVerticalScrollIndicator={false}>
      <LoadingOverlay visible={state === 'processing'} message={
        transcription ? t('analyzing', language) : t('voice_processing', language)
      } />

      {/* Header */}
      <View style={styles.header}>
        <Ionicons name="mic" size={28} color={Colors.textOnPrimary} />
        <View>
          <Text style={styles.headerTitle}>{t('voice_title', language)}</Text>
          <Text style={styles.headerSub}>{getLanguageMeta(language).nativeName}</Text>
        </View>
      </View>

      {/* Speech accuracy warning for languages without reliable STT support */}
      {!getLanguageMeta(language).voiceReliable && (
        <View style={styles.warningBox}>
          <Ionicons name="warning" size={16} color={Colors.warning} />
          <Text style={styles.warningText}>{t('voice_accuracy_warning', language)}</Text>
        </View>
      )}

      {/* Idle / recording state */}
      {(state === 'idle' || state === 'recording') && (
        <View style={styles.recordSection}>
          <Text style={styles.instruction}>
            {state === 'recording'
              ? t('voice_recording', language)
              : t('voice_instruction', language)}
          </Text>

          <Animated.View style={{ transform: [{ scale: pulseAnim }] }}>
            <TouchableOpacity
              style={[styles.micBtn, state === 'recording' && styles.micBtnRecording, webShadow.lg]}
              onPress={state === 'recording' ? stopRecording : startRecording}
              activeOpacity={0.8}
              accessibilityLabel={state === 'recording'
                ? t('voice_stopRecording', language)
                : t('voice_startRecording', language)}
            >
              <Ionicons
                name={state === 'recording' ? 'stop' : 'mic'}
                size={48}
                color={Colors.textOnPrimary}
              />
            </TouchableOpacity>
          </Animated.View>

          <Text style={styles.micLabel}>
            {state === 'recording'
              ? t('voice_tapStop', language)
              : t('voice_tapRecord', language)}
          </Text>

          {/* Fallback: type instead */}
          <TouchableOpacity
            style={styles.typeInstead}
            onPress={() => router.push('/ask')}
            activeOpacity={0.8}
          >
            <Ionicons name="create-outline" size={16} color={Colors.textMuted} />
            <Text style={styles.typeInsteadText}>{t('voice_typeInstead', language)}</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Transcription review */}
      {state === 'transcribed' && (
        <View style={styles.transcriptionSection}>
          <Text style={styles.sectionTitle}>{t('voice_yourQuestion', language)}</Text>

          {transcriptionWarning ? (
            <View style={styles.warningBox}>
              <Ionicons name="warning" size={16} color={Colors.warning} />
              <Text style={styles.warningText}>{transcriptionWarning}</Text>
            </View>
          ) : null}

          {transcription ? (
            <>
              <Text style={styles.editHint}>{t('voice_edit_hint', language)}</Text>
              <TextInput
                style={styles.transcriptionInput}
                value={transcription}
                onChangeText={setTranscription}
                multiline
                textAlignVertical="top"
                accessibilityLabel={t('voice_edit_hint', language)}
              />
              <TouchableOpacity style={styles.submitBtn} onPress={submitTranscription} activeOpacity={0.85}>
                <Ionicons name="send" size={18} color={Colors.textOnPrimary} />
                <Text style={styles.submitBtnText}>{t('voice_submitQuestion', language)}</Text>
              </TouchableOpacity>
            </>
          ) : (
            <TouchableOpacity style={styles.submitBtn} onPress={() => router.push('/ask')} activeOpacity={0.85}>
              <Ionicons name="create" size={18} color={Colors.textOnPrimary} />
              <Text style={styles.submitBtnText}>{t('voice_typeQuestion', language)}</Text>
            </TouchableOpacity>
          )}

          <TouchableOpacity style={styles.retryLink} onPress={reset}>
            <Text style={styles.retryLinkText}>{t('voice_recordAgain', language)}</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Answer */}
      {state === 'answered' && result && (
        <View style={styles.answerSection}>
          {/* Audio playback control */}
          <TouchableOpacity
            style={styles.audioRow}
            onPress={playingAudio ? stopAudio : () => playAnswer()}
          >
            <Ionicons
              name={playingAudio ? 'stop-circle' : 'play-circle'}
              size={24}
              color={Colors.secondary}
            />
            <Text style={styles.audioLabel}>
              {playingAudio ? t('voice_stop', language) : t('voice_playback', language)}
            </Text>
          </TouchableOpacity>

          {result.uncertainty_flag && <UncertaintyBanner />}

          <SectionCard
            title={t('voice_answer', language)}
            content={result.answer}
            iconName="shield-checkmark"
            iconColor={Colors.primary}
          />

          {result.legal_sources?.length > 0 && (
            <View style={styles.sourcesBox}>
              <Text style={styles.sourcesTitle}>{t('section_sources', language)}</Text>
              {result.legal_sources.map((s: any, i: number) => (
                <Text key={i} style={styles.sourceItem}>• {s.short_title || s.title}</Text>
              ))}
            </View>
          )}

          <DisclaimerBanner />

          <TouchableOpacity style={styles.resetBtn} onPress={reset} activeOpacity={0.8}>
            <Ionicons name="mic" size={18} color={Colors.primary} />
            <Text style={styles.resetBtnText}>{t('voice_askAnother', language)}</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Free legal aid connection */}
      <TouchableOpacity
        style={styles.legalAidButton}
        onPress={() => router.push('/legal-aid' as any)}
        activeOpacity={0.85}
        accessibilityRole="button"
        accessibilityLabel={t('voice_freeLegalAid', language)}
      >
        <Ionicons name="people-outline" size={20} color={Colors.primary} />
        <Text style={styles.legalAidButtonText}>{t('voice_freeLegalAid', language)}</Text>
        <Ionicons name="chevron-forward" size={18} color={Colors.primary} />
      </TouchableOpacity>

      <DisclaimerBanner />
    </ScrollView>
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

  warningBox: {
    flexDirection: 'row', gap: Spacing.sm, alignItems: 'flex-start',
    backgroundColor: Colors.warningBg, borderRadius: BorderRadius.md, padding: Spacing.base,
  },
  warningText: { flex: 1, fontFamily: FontFamily.regular, fontSize: FontSize.xs, color: Colors.textSecondary, lineHeight: FontSize.xs * 1.6 },

  recordSection: { alignItems: 'center', gap: Spacing.xl, paddingVertical: Spacing['2xl'] },
  instruction: {
    fontFamily: FontFamily.medium, fontSize: FontSize.base, color: Colors.textSecondary,
    textAlign: 'center', lineHeight: FontSize.base * 1.6,
  },
  micBtn: {
    width: 120, height: 120, borderRadius: 60,
    backgroundColor: Colors.primary,
    alignItems: 'center', justifyContent: 'center',
  },
  micBtnRecording: { backgroundColor: Colors.error },
  micLabel: { fontFamily: FontFamily.medium, fontSize: FontSize.sm, color: Colors.textMuted },
  typeInstead: {
    flexDirection: 'row', gap: Spacing.sm, alignItems: 'center',
    padding: Spacing.md,
  },
  typeInsteadText: { fontFamily: FontFamily.regular, fontSize: FontSize.sm, color: Colors.textMuted },

  transcriptionSection: { gap: Spacing.base },
  sectionTitle: { fontFamily: FontFamily.semiBold, fontSize: FontSize.base, color: Colors.textPrimary },
  transcriptionBox: {
    backgroundColor: Colors.surface, borderRadius: BorderRadius.lg,
    padding: Spacing.base, borderWidth: 1.5, borderColor: Colors.primary,
  },
  transcriptionText: {
    fontFamily: FontFamily.regular, fontSize: FontSize.base,
    color: Colors.textPrimary, lineHeight: FontSize.base * 1.6,
  },
  editHint: {
    fontFamily: FontFamily.regular, fontSize: FontSize.xs, color: Colors.textMuted,
  },
  transcriptionInput: {
    backgroundColor: Colors.surface, borderRadius: BorderRadius.lg,
    padding: Spacing.base, borderWidth: 1.5, borderColor: Colors.primary,
    fontFamily: FontFamily.regular, fontSize: FontSize.base,
    color: Colors.textPrimary, lineHeight: FontSize.base * 1.6,
    minHeight: 90,
  },
  submitBtn: {
    backgroundColor: Colors.primary, borderRadius: BorderRadius.lg,
    padding: Spacing.base, flexDirection: 'row', alignItems: 'center',
    justifyContent: 'center', gap: Spacing.sm,
  },
  submitBtnText: { fontFamily: FontFamily.semiBold, fontSize: FontSize.base, color: Colors.textOnPrimary },
  retryLink: { alignItems: 'center', padding: Spacing.sm },
  retryLinkText: { fontFamily: FontFamily.medium, fontSize: FontSize.sm, color: Colors.textMuted },

  legalAidButton: {
    backgroundColor: Colors.primaryTint,
    borderRadius: BorderRadius.lg,
    padding: Spacing.base,
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
  },
  legalAidButtonText: {
    flex: 1,
    fontFamily: FontFamily.semiBold,
    fontSize: FontSize.sm,
    color: Colors.primary,
  },

  answerSection: { gap: Spacing.sm },
  audioRow: {
    flexDirection: 'row', alignItems: 'center', gap: Spacing.sm,
    backgroundColor: Colors.secondaryTint, borderRadius: BorderRadius.md, padding: Spacing.base,
  },
  audioLabel: { fontFamily: FontFamily.medium, fontSize: FontSize.sm, color: Colors.secondaryText },

  sourcesBox: { backgroundColor: Colors.surfaceMuted, borderRadius: BorderRadius.md, padding: Spacing.base, gap: Spacing.xs },
  sourcesTitle: { fontFamily: FontFamily.semiBold, fontSize: FontSize.xs, color: Colors.textMuted, textTransform: 'uppercase' },
  sourceItem: { fontFamily: FontFamily.regular, fontSize: FontSize.xs, color: Colors.textSecondary },

  resetBtn: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center',
    gap: Spacing.sm, backgroundColor: Colors.primaryTint,
    borderRadius: BorderRadius.lg, padding: Spacing.base,
  },
  resetBtnText: { fontFamily: FontFamily.semiBold, fontSize: FontSize.base, color: Colors.primary },
});
