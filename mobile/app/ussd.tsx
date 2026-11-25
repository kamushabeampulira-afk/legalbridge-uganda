/**
 * USSD simulator — a handset with a dial pad. Type the LegalBridge code, press
 * call, and the USSD pop-up appears just as it does on a basic phone. It calls
 * the same webhook Africa's Talking calls, so the menus and answers are real.
 */
import React, { useEffect, useRef, useState } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  TextInput, ActivityIndicator, Platform, TextStyle,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '@/constants/Colors';
import { Spacing } from '@/constants/Spacing';
import { FontFamily, FontSize } from '@/constants/Typography';
import { USSD_CODE } from '@/constants/Ussd';
import { useAppStore } from '@/store/useAppStore';
import { t } from '@/i18n/translations';
import { ussdApi } from '@/services/api';

// The server remembers each number's language. Logged-out visitors get a made-up
// number for this visit, so one visitor's choice is not used for the next.
function visitPhoneNumber(): string {
  return `+2567${String(Math.floor(Math.random() * 1e8)).padStart(8, '0')}`;
}

// Device colours: the handset copies a generic phone, not the app's brand.
const PHONE = {
  body: '#121212',
  edge: '#3A3A3C',
  sideButton: '#2A2A2C',
  screen: '#FFFFFF',
  ink: '#202124',
  key: '#3D7BC6',
  keySub: '#55759F',
  divider: '#C8D5E2',
  call: '#34A065',
  dim: 'rgba(0, 0, 0, 0.45)',
};

const KEYPAD = [
  [{ key: '1', sub: '' }, { key: '2', sub: 'ABC' }, { key: '3', sub: 'DEF' }],
  [{ key: '4', sub: 'GHI' }, { key: '5', sub: 'JKL' }, { key: '6', sub: 'MNO' }],
  [{ key: '7', sub: 'PQRS' }, { key: '8', sub: 'TUV' }, { key: '9', sub: 'WXYZ' }],
  [{ key: '*', sub: '' }, { key: '0', sub: '+' }, { key: '#', sub: '' }],
];

const MAX_DIALLED = 24;

// Web: no on-screen keyboard over the dial pad (a laptop keyboard still types).
// Native: same, using the platform prop.
const NO_SOFT_KEYBOARD = Platform.OS === 'web'
  ? { inputMode: 'none' as const }
  : { showSoftInputOnFocus: false };

// Browsers draw a focus box round inputs; the dial display shows only its cursor.
const NO_FOCUS_BOX = (Platform.OS === 'web' ? { outlineStyle: 'none' } : {}) as unknown as TextStyle;

type Phase = 'idle' | 'loading' | 'open' | 'ended' | 'error';

function newSessionId(): string {
  return `app-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
}

function cleanDialled(value: string): string {
  return value.replace(/[^0-9*#+]/g, '').slice(0, MAX_DIALLED);
}

export default function UssdSimulatorScreen() {
  const language = useAppStore((s) => s.language);
  const [visitPhone] = useState(visitPhoneNumber);
  const phoneNumber = useAppStore((s) => s.user?.phone_number) || visitPhone;

  const [dialled, setDialled] = useState('');
  const [phase, setPhase] = useState<Phase>('idle');
  const [message, setMessage] = useState('');
  const [reply, setReply] = useState('');

  const displayRef = useRef<TextInput>(null);
  // The session id and every answer so far ('1*2*...'), as Africa's Talking tracks them.
  const session = useRef({ id: '', text: '' });
  // Bumped on hang-up and unmount so a late reply cannot reopen a closed session.
  const requestId = useRef(0);

  useEffect(() => () => { requestId.current += 1; }, []);

  // Put the blinking cursor back in the display whenever the pop-up closes.
  useEffect(() => {
    if (phase === 'idle') displayRef.current?.focus();
  }, [phase]);

  const send = async (text: string) => {
    const thisRequest = ++requestId.current;
    setPhase('loading');
    try {
      const result = await ussdApi.send(session.current.id, USSD_CODE, phoneNumber, text);
      if (thisRequest !== requestId.current) return;
      session.current.text = text;
      setMessage(result.text);
      setReply('');
      setPhase(result.ended ? 'ended' : 'open');
    } catch {
      if (thisRequest !== requestId.current) return;
      setMessage(t('ussdSim_error', language));
      setPhase('error');
    }
  };

  const pressKey = (key: string) => {
    setDialled((current) => cleanDialled(current + key));
    displayRef.current?.focus();
  };

  const backspace = () => {
    setDialled((current) => current.slice(0, -1));
    displayRef.current?.focus();
  };

  const call = () => {
    if (phase !== 'idle') return;
    // Like a phone's redial: an empty display calls the LegalBridge code.
    const code = dialled || USSD_CODE;
    setDialled(code);
    if (code !== USSD_CODE) {
      setMessage(t('ussdSim_invalidCode', language));
      setPhase('error');
      return;
    }
    session.current = { id: newSessionId(), text: '' };
    send('');
  };

  const submitReply = () => {
    const answer = reply.trim();
    if (!answer || phase !== 'open') return;
    const previous = session.current.text;
    send(previous ? `${previous}*${answer}` : answer);
  };

  const hangUp = () => {
    requestId.current += 1;
    session.current = { id: '', text: '' };
    setReply('');
    setMessage('');
    setPhase('idle');
  };

  const goHome = () => {
    hangUp();
    setDialled('');
  };

  const canSend = phase === 'open' && reply.trim().length > 0;

  return (
    <ScrollView
      style={styles.scroll}
      contentContainerStyle={styles.container}
      keyboardShouldPersistTaps="handled"
      showsVerticalScrollIndicator={false}
    >
      <Text style={styles.intro}>{t('ussdSim_intro', language)}</Text>
      <Text style={styles.hint}>
        {t('home_ussd', language)} <Text style={styles.hintCode}>{USSD_CODE}</Text>
      </Text>

      <View style={styles.phone}>
        <View style={[styles.sideButton, styles.sideButtonShort]} />
        <View style={[styles.sideButton, styles.sideButtonLong]} />

        <View style={styles.screen}>
          {/* Status bar */}
          <View style={styles.statusBar}>
            <Text style={styles.carrier}>LegalBridge</Text>
            <View style={styles.statusIcons}>
              <Ionicons name="cellular" size={13} color={PHONE.ink} />
              <Ionicons name="battery-full" size={16} color={PHONE.ink} />
            </View>
          </View>

          {/* Number being dialled */}
          <View style={styles.displayArea}>
            <TextInput
              ref={displayRef}
              style={[styles.display, NO_FOCUS_BOX]}
              value={dialled}
              onChangeText={(value) => setDialled(cleanDialled(value))}
              onSubmitEditing={call}
              keyboardType="phone-pad"
              selectionColor={PHONE.key}
              accessibilityLabel={`${t('home_ussd', language)} ${USSD_CODE}`}
              autoFocus
              {...NO_SOFT_KEYBOARD}
            />
            {dialled.length > 0 && (
              <TouchableOpacity
                style={styles.backspace}
                onPress={backspace}
                onLongPress={() => setDialled('')}
                accessibilityRole="button"
                accessibilityLabel={t('removeDocument', language)}
              >
                <Ionicons name="backspace-outline" size={22} color={PHONE.keySub} />
              </TouchableOpacity>
            )}
          </View>

          <View style={styles.divider} />

          {/* Dial pad */}
          <View style={styles.keypad}>
            {KEYPAD.map((row) => (
              <View key={row[0].key} style={styles.keyRow}>
                {row.map(({ key, sub }) => (
                  <TouchableOpacity
                    key={key}
                    style={styles.key}
                    onPress={() => pressKey(key)}
                    activeOpacity={0.5}
                    accessibilityRole="button"
                    accessibilityLabel={key}
                  >
                    <Text style={styles.keyDigit}>{key}</Text>
                    {key === '1' ? (
                      <Ionicons name="recording-outline" size={12} color={PHONE.keySub} />
                    ) : (
                      <Text style={styles.keySub}>{sub}</Text>
                    )}
                  </TouchableOpacity>
                ))}
              </View>
            ))}
          </View>

          <View style={styles.callRow}>
            <TouchableOpacity
              style={styles.callButton}
              onPress={call}
              activeOpacity={0.85}
              accessibilityRole="button"
              accessibilityLabel={`${t('legalHelp_call', language)} ${dialled || USSD_CODE}`}
            >
              <Ionicons name="call" size={24} color="#FFFFFF" />
            </TouchableOpacity>
          </View>

          {/* Navigation bar */}
          <View style={styles.navBar}>
            <TouchableOpacity
              style={styles.homeButton}
              onPress={goHome}
              accessibilityRole="button"
              accessibilityLabel={t('tab_home', language)}
            >
              <Ionicons name="home" size={18} color={PHONE.keySub} />
            </TouchableOpacity>
          </View>

          {/* USSD pop-up, over a dimmed screen */}
          {phase !== 'idle' && (
            <View style={styles.overlay}>
              {phase === 'loading' ? (
                <View style={[styles.dialog, styles.loadingDialog]}>
                  <ActivityIndicator color={PHONE.key} />
                  <Text style={styles.dialogText}>{t('ussdSim_running', language)}</Text>
                </View>
              ) : (
                <View style={styles.dialog}>
                  <ScrollView style={phase === 'open' ? styles.dialogScroll : styles.dialogScrollTall}>
                    <Text style={styles.dialogText} accessibilityLiveRegion="polite">
                      {message}
                    </Text>
                  </ScrollView>

                  {phase === 'open' && (
                    <TextInput
                      style={[styles.input, NO_FOCUS_BOX]}
                      value={reply}
                      onChangeText={setReply}
                      onSubmitEditing={submitReply}
                      placeholder={t('ussdSim_reply', language)}
                      placeholderTextColor={PHONE.keySub}
                      accessibilityLabel={t('ussdSim_reply', language)}
                      keyboardType="phone-pad"
                      returnKeyType="send"
                      selectionColor={PHONE.key}
                      maxLength={30}
                      autoFocus
                    />
                  )}

                  <View style={styles.actions}>
                    {phase === 'open' ? (
                      <>
                        <DialogButton label={t('cancel', language)} onPress={hangUp} />
                        <DialogButton
                          label={t('ussdSim_send', language)}
                          onPress={submitReply}
                          disabled={!canSend}
                        />
                      </>
                    ) : (
                      <DialogButton label={t('close', language)} onPress={hangUp} />
                    )}
                  </View>
                </View>
              )}
            </View>
          )}
        </View>
      </View>

      <Text style={styles.note}>{t('ussd_note', language)}</Text>
    </ScrollView>
  );
}

function DialogButton({
  label, onPress, disabled = false,
}: { label: string; onPress: () => void; disabled?: boolean }) {
  return (
    <TouchableOpacity
      style={styles.actionButton}
      onPress={onPress}
      disabled={disabled}
      accessibilityRole="button"
      accessibilityLabel={label}
      accessibilityState={{ disabled }}
    >
      <Text style={[styles.actionText, disabled && styles.actionTextDisabled]}>{label}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  scroll: { flex: 1, backgroundColor: Colors.background },
  container: { padding: Spacing.base, paddingBottom: Spacing['3xl'], gap: Spacing.md },

  intro: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.sm,
    color: Colors.textSecondary,
    lineHeight: FontSize.sm * 1.6,
    textAlign: 'center',
  },
  hint: {
    fontFamily: FontFamily.medium,
    fontSize: FontSize.sm,
    color: Colors.textPrimary,
    textAlign: 'center',
  },
  hintCode: { fontFamily: FontFamily.bold, color: Colors.primary, letterSpacing: 1 },

  // Handset: black body with a thin grey edge and two buttons on the right.
  phone: {
    width: '100%',
    maxWidth: 300,
    alignSelf: 'center',
    backgroundColor: PHONE.body,
    borderWidth: 2,
    borderColor: PHONE.edge,
    borderRadius: 46,
    padding: 9,
    marginVertical: Spacing.sm,
  },
  sideButton: {
    position: 'absolute',
    right: -5,
    width: 4,
    borderRadius: 2,
    backgroundColor: PHONE.sideButton,
  },
  sideButtonShort: { top: 120, height: 36 },
  sideButtonLong: { top: 180, height: 70 },

  screen: {
    height: 560,
    backgroundColor: PHONE.screen,
    borderRadius: 36,
    overflow: 'hidden',
  },

  statusBar: {
    height: 34,
    paddingHorizontal: 20,
    paddingTop: 8,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  carrier: { fontFamily: FontFamily.medium, fontSize: 12, color: PHONE.ink },
  statusIcons: { flexDirection: 'row', alignItems: 'center', gap: 6 },

  displayArea: {
    flex: 1,
    justifyContent: 'flex-end',
    paddingHorizontal: 44,
    paddingBottom: Spacing.md,
  },
  display: {
    fontFamily: FontFamily.regular,
    fontSize: 28,
    color: PHONE.ink,
    textAlign: 'center',
    letterSpacing: 1,
    paddingVertical: 4,
  },
  backspace: {
    position: 'absolute',
    right: 10,
    bottom: Spacing.md,
    width: 40,
    height: 40,
    alignItems: 'center',
    justifyContent: 'center',
  },
  divider: { height: 1, backgroundColor: PHONE.divider },

  keypad: { paddingTop: Spacing.sm, paddingHorizontal: Spacing.base },
  keyRow: { flexDirection: 'row' },
  key: {
    flex: 1,
    height: 54,
    alignItems: 'center',
    justifyContent: 'center',
  },
  keyDigit: {
    fontFamily: FontFamily.regular,
    fontSize: 26,
    lineHeight: 30,
    color: PHONE.key,
  },
  keySub: {
    fontFamily: FontFamily.regular,
    fontSize: 10,
    lineHeight: 12,
    letterSpacing: 0.5,
    color: PHONE.keySub,
    minHeight: 12,
  },

  callRow: { alignItems: 'center', paddingVertical: Spacing.md },
  callButton: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: PHONE.call,
    alignItems: 'center',
    justifyContent: 'center',
  },

  navBar: {
    height: 40,
    borderTopWidth: 1,
    borderTopColor: PHONE.divider,
    alignItems: 'center',
    justifyContent: 'center',
  },
  homeButton: { width: 44, height: 40, alignItems: 'center', justifyContent: 'center' },

  // The USSD pop-up.
  overlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: PHONE.dim,
    justifyContent: 'center',
    padding: Spacing.md,
  },
  dialog: {
    backgroundColor: PHONE.screen,
    borderRadius: 12,
    padding: Spacing.base,
    gap: Spacing.md,
  },
  loadingDialog: { flexDirection: 'row', alignItems: 'center' },
  // Menus leave room for the reply box; a final answer can use the full height.
  dialogScroll: { maxHeight: 300 },
  dialogScrollTall: { maxHeight: 410 },
  dialogText: {
    flexShrink: 1,
    fontFamily: FontFamily.regular,
    fontSize: 15,
    color: PHONE.ink,
    lineHeight: 22,
  },
  input: {
    borderBottomWidth: 2,
    borderBottomColor: PHONE.key,
    paddingVertical: Spacing.sm,
    fontFamily: FontFamily.regular,
    fontSize: FontSize.md,
    color: PHONE.ink,
  },
  actions: { flexDirection: 'row', justifyContent: 'flex-end', gap: Spacing.xs },
  actionButton: {
    paddingVertical: Spacing.sm,
    paddingHorizontal: Spacing.md,
    minHeight: 44,
    justifyContent: 'center',
  },
  actionText: {
    fontFamily: FontFamily.semiBold,
    fontSize: FontSize.sm,
    color: PHONE.key,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  actionTextDisabled: { color: PHONE.divider },

  note: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.xs,
    color: Colors.textMuted,
    textAlign: 'center',
    lineHeight: FontSize.xs * 1.6,
  },
});
