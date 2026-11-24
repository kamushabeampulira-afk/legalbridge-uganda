/**
 * Voice interaction screen — record question, receive spoken answer.
 */
import React, { useState, useRef } from 'react';
import {
  View, Text, StyleSheet, ScrollView,
  TouchableOpacity, Alert, Animated,
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
import { t } from '@/i18n/translations';
import DisclaimerBanner from '@/components/ui/DisclaimerBanner';
import UncertaintyBanner from '@/components/ui/UncertaintyBanner';
import SectionCard from '@/components/ui/SectionCard';
import LoadingOverlay from '@/components/ui/LoadingOverlay';

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

  // ── Recording ─────────────────────────────────────────────────────────────

  const startRecording = async () => {
    try {
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission needed', 'Microphone access is required for voice questions.');
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
      Alert.alert('Recording failed', 'Could not start recording. Please try typing your question.');
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
        setTranscriptionWarning(result.warning ?? t('voice_fallback', language));
        setState('transcribed');
        return;
      }
      setTranscription(result.transcription);
      setTranscriptionWarning(result.warning ?? '');
      setState('transcribed');
    } catch (err: any) {
      setTranscription('');
      setTranscriptionWarning(t('voice_fallback', language));
      setState('transcribed');
    }
  };

  const submitTranscription = async () => {
    if (!transcription.trim()) {
      Alert.alert('No text', t('voice_fallback', language));
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

      // Auto-synthesize audio response
      if (res.answer && !res.uncertainty_flag) {
        const audioRes = await voiceApi.synthesize(res.answer.slice(0, 800), language);
        if (audioRes.audio_url) {
          const { sound: s } = await Audio.Sound.createAsync({ uri: audioRes.audio_url });
          setSound(s);
          setPlayingAudio(true);
          await s.playAsync();
          s.setOnPlaybackStatusUpdate((status) => {
            if (!status.isLoaded || (status as any).didJustFinish) setPlayingAudio(false);
          });
        }
      }
    } catch (err: any) {
      Alert.alert('Error', err.message ?? t('error_generic', language));
      setState('transcribed');
    }
  };

  const reset = () => {
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

  const stopAudio = async () => {
    await sound?.stopAsync();
    setPlayingAudio(false);
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
          <Text style={styles.headerSub}>English & Luganda</Text>
        </View>
      </View>

      {/* Luganda warning */}
      {language === 'lg' && (
        <View style={styles.warningBox}>
          <Ionicons name="warning" size={16} color={Colors.warningMutedCoral} />
          <Text style={styles.warningText}>{t('voice_luganda_warning', language)}</Text>
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
              accessibilityLabel={state === 'recording' ? 'Stop recording' : 'Start recording'}
            >
              <Ionicons
                name={state === 'recording' ? 'stop' : 'mic'}
                size={48}
                color={Colors.textOnPrimary}
              />
            </TouchableOpacity>
          </Animated.View>

          <Text style={styles.micLabel}>
            {state === 'recording' ? 'Tap to stop' : 'Tap to record'}
          </Text>

          {/* Fallback: type instead */}
          <TouchableOpacity
            style={styles.typeInstead}
            onPress={() => router.push('/ask')}
            activeOpacity={0.8}
          >
            <Ionicons name="create-outline" size={16} color={Colors.textMuted} />
            <Text style={styles.typeInsteadText}>Type your question instead</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Transcription review */}
      {state === 'transcribed' && (
        <View style={styles.transcriptionSection}>
          <Text style={styles.sectionTitle}>Your question</Text>

          {transcriptionWarning ? (
            <View style={styles.warningBox}>
              <Ionicons name="warning" size={16} color={Colors.warningMutedCoral} />
              <Text style={styles.warningText}>{transcriptionWarning}</Text>
            </View>
          ) : null}

          {transcription ? (
            <>
              <View style={styles.transcriptionBox}>
                <Text style={styles.transcriptionText}>{transcription}</Text>
              </View>
              <TouchableOpacity style={styles.submitBtn} onPress={submitTranscription} activeOpacity={0.85}>
                <Ionicons name="send" size={18} color={Colors.textOnPrimary} />
                <Text style={styles.submitBtnText}>Submit Question</Text>
              </TouchableOpacity>
            </>
          ) : (
            <TouchableOpacity style={styles.submitBtn} onPress={() => router.push('/ask')} activeOpacity={0.85}>
              <Ionicons name="create" size={18} color={Colors.textOnPrimary} />
              <Text style={styles.submitBtnText}>Type Question Instead</Text>
            </TouchableOpacity>
          )}

          <TouchableOpacity style={styles.retryLink} onPress={reset}>
            <Text style={styles.retryLinkText}>Record Again</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Answer */}
      {state === 'answered' && result && (
        <View style={styles.answerSection}>
          {/* Audio playback control */}
          <TouchableOpacity
            style={styles.audioRow}
            onPress={playingAudio ? stopAudio : async () => {
              if (sound) { setPlayingAudio(true); await sound.replayAsync(); }
            }}
          >
            <Ionicons
              name={playingAudio ? 'stop-circle' : 'play-circle'}
              size={24}
              color={Colors.secondaryBurntOrange}
            />
            <Text style={styles.audioLabel}>
              {playingAudio ? t('voice_stop', language) : t('voice_playback', language)}
            </Text>
          </TouchableOpacity>

          {result.uncertainty_flag && <UncertaintyBanner />}

          <SectionCard
            title="LegalBridge Answer"
            content={result.answer}
            iconName="shield-checkmark"
            iconColor={Colors.primaryDeepTeal}
          />

          {result.legal_sources?.length > 0 && (
            <View style={styles.sourcesBox}>
              <Text style={styles.sourcesTitle}>{t('section_sources', language)}</Text>
              {result.legal_sources.map((s: any, i: number) => (
                <Text key={i} style={styles.sourceItem}>• {s.short_title || s.title}</Text>
              ))}
            </View>
          )}

          <DisclaimerBanner message={result.disclaimer} />

          <TouchableOpacity style={styles.resetBtn} onPress={reset} activeOpacity={0.8}>
            <Ionicons name="mic" size={18} color={Colors.primaryDeepTeal} />
            <Text style={styles.resetBtnText}>Ask Another Question</Text>
          </TouchableOpacity>
        </View>
      )}

      <DisclaimerBanner />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scroll: { flex: 1, backgroundColor: Colors.backgroundOffWhite },
  container: { padding: Spacing.base, paddingBottom: Spacing['3xl'], gap: Spacing.base },

  header: {
    backgroundColor: Colors.primaryDeepPurple,
    borderRadius: BorderRadius.xl,
    padding: Spacing.xl,
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.base,
  },
  headerTitle: { fontFamily: FontFamily.bold, fontSize: FontSize.lg, color: Colors.textOnPrimary },
  headerSub: { fontFamily: FontFamily.regular, fontSize: FontSize.xs, color: Colors.accentSoftPeach, marginTop: 2 },

  warningBox: {
    flexDirection: 'row', gap: Spacing.sm, alignItems: 'flex-start',
    backgroundColor: Colors.warningLight, borderRadius: BorderRadius.md, padding: Spacing.base,
  },
  warningText: { flex: 1, fontFamily: FontFamily.regular, fontSize: FontSize.xs, color: Colors.textSecondary, lineHeight: FontSize.xs * 1.6 },

  recordSection: { alignItems: 'center', gap: Spacing.xl, paddingVertical: Spacing['2xl'] },
  instruction: {
    fontFamily: FontFamily.medium, fontSize: FontSize.base, color: Colors.textSecondary,
    textAlign: 'center', lineHeight: FontSize.base * 1.6,
  },
  micBtn: {
    width: 120, height: 120, borderRadius: 60,
    backgroundColor: Colors.primaryDeepPurple,
    alignItems: 'center', justifyContent: 'center',
  },
  micBtnRecording: { backgroundColor: Colors.warningMutedCoral },
  micLabel: { fontFamily: FontFamily.medium, fontSize: FontSize.sm, color: Colors.textMuted },
  typeInstead: {
    flexDirection: 'row', gap: Spacing.sm, alignItems: 'center',
    padding: Spacing.md,
  },
  typeInsteadText: { fontFamily: FontFamily.regular, fontSize: FontSize.sm, color: Colors.textMuted },

  transcriptionSection: { gap: Spacing.base },
  sectionTitle: { fontFamily: FontFamily.semiBold, fontSize: FontSize.base, color: Colors.textPrimary },
  transcriptionBox: {
    backgroundColor: Colors.surfaceWhite, borderRadius: BorderRadius.lg,
    padding: Spacing.base, borderWidth: 1.5, borderColor: Colors.primaryDeepTeal,
  },
  transcriptionText: {
    fontFamily: FontFamily.regular, fontSize: FontSize.base,
    color: Colors.textPrimary, lineHeight: FontSize.base * 1.6,
  },
  submitBtn: {
    backgroundColor: Colors.primaryDeepTeal, borderRadius: BorderRadius.lg,
    padding: Spacing.base, flexDirection: 'row', alignItems: 'center',
    justifyContent: 'center', gap: Spacing.sm,
  },
  submitBtnText: { fontFamily: FontFamily.semiBold, fontSize: FontSize.base, color: Colors.textOnPrimary },
  retryLink: { alignItems: 'center', padding: Spacing.sm },
  retryLinkText: { fontFamily: FontFamily.medium, fontSize: FontSize.sm, color: Colors.textMuted },

  answerSection: { gap: Spacing.sm },
  audioRow: {
    flexDirection: 'row', alignItems: 'center', gap: Spacing.sm,
    backgroundColor: '#FEF0E8', borderRadius: BorderRadius.md, padding: Spacing.base,
  },
  audioLabel: { fontFamily: FontFamily.medium, fontSize: FontSize.sm, color: Colors.secondaryBurntOrange },

  sourcesBox: { backgroundColor: Colors.surfaceLight, borderRadius: BorderRadius.md, padding: Spacing.base, gap: Spacing.xs },
  sourcesTitle: { fontFamily: FontFamily.semiBold, fontSize: FontSize.xs, color: Colors.textMuted, textTransform: 'uppercase' },
  sourceItem: { fontFamily: FontFamily.regular, fontSize: FontSize.xs, color: Colors.textSecondary },

  resetBtn: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center',
    gap: Spacing.sm, backgroundColor: '#E8F4F7',
    borderRadius: BorderRadius.lg, padding: Spacing.base,
  },
  resetBtnText: { fontFamily: FontFamily.semiBold, fontSize: FontSize.base, color: Colors.primaryDeepTeal },
});
