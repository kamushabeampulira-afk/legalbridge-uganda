import React, { useState } from 'react';
import {
  View, Text, StyleSheet, ScrollView,
  TouchableOpacity, KeyboardAvoidingView, Platform,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { authApi } from '@/services/api';
import { Colors } from '@/constants/Colors';
import { Spacing, BorderRadius } from '@/constants/Spacing';
import { FontFamily, FontSize } from '@/constants/Typography';
import Button from '@/components/ui/Button';
import TextInput from '@/components/ui/TextInput';
import { useAppStore } from '@/store/useAppStore';
import { t } from '@/i18n/translations';

const USER_TYPES = [
  { value: 'boda_boda', label: 'Boda Boda Rider', icon: '🏍️' },
  { value: 'market_vendor', label: 'Market Vendor', icon: '🏪' },
  { value: 'general', label: 'General User', icon: '👤' },
];

export default function RegisterScreen() {
  const router = useRouter();
  const { language } = useAppStore();
  const [phone, setPhone] = useState('');
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [userType, setUserType] = useState('general');
  const [consented, setConsented] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = () => {
    const e: Record<string, string> = {};
    if (!phone.trim()) e.phone = 'Phone number is required.';
    if (password.length < 6) e.password = 'Password must be at least 6 characters.';
    if (password !== confirm) e.confirm = 'Passwords do not match.';
    if (!consented) e.consent = 'You must agree to data processing to continue.';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleRegister = async () => {
    if (!validate()) return;
    setLoading(true);
    try {
      await authApi.register({
        phone_number: phone.trim(),
        password,
        password_confirm: confirm,
        full_name: name.trim(),
        user_type: userType,
        preferred_language: language,
        consented_to_processing: consented,
      });
      router.replace('/(auth)/login');
    } catch (err: any) {
      setErrors({ general: err.message });
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
        contentContainerStyle={styles.container}
        keyboardShouldPersistTaps="handled"
      >
        <Text style={styles.title}>{t('register', language)}</Text>
        <Text style={styles.subtitle}>Create your LegalBridge account</Text>

        {errors.general && (
          <View style={styles.errorBanner}>
            <Text style={styles.errorText}>{errors.general}</Text>
          </View>
        )}

        <TextInput
          label={t('phoneNumber', language)}
          value={phone}
          onChangeText={setPhone}
          keyboardType="phone-pad"
          placeholder="+256 7XX XXX XXX"
          error={errors.phone}
        />

        <TextInput
          label={`${t('fullName', language)}`}
          value={name}
          onChangeText={setName}
          placeholder="Your name"
        />

        <TextInput
          label={t('password', language)}
          value={password}
          onChangeText={setPassword}
          isPassword
          error={errors.password}
        />

        <TextInput
          label={t('confirmPassword', language)}
          value={confirm}
          onChangeText={setConfirm}
          isPassword
          error={errors.confirm}
        />

        {/* User type selector */}
        <Text style={styles.sectionLabel}>{t('iAmA', language)}</Text>
        <View style={styles.typeRow}>
          {USER_TYPES.map((ut) => (
            <TouchableOpacity
              key={ut.value}
              style={[styles.typeOption, userType === ut.value && styles.typeSelected]}
              onPress={() => setUserType(ut.value)}
              activeOpacity={0.8}
            >
              <Text style={styles.typeIcon}>{ut.icon}</Text>
              <Text style={[styles.typeLabel, userType === ut.value && styles.typeLabelSelected]}>
                {ut.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Consent */}
        <TouchableOpacity
          style={styles.consentRow}
          onPress={() => setConsented(!consented)}
          activeOpacity={0.7}
        >
          <View style={[styles.checkbox, consented && styles.checkboxChecked]}>
            {consented && <Ionicons name="checkmark" size={14} color={Colors.textOnPrimary} />}
          </View>
          <Text style={styles.consentText}>{t('consent', language)}</Text>
        </TouchableOpacity>
        {errors.consent && <Text style={styles.errorSmall}>{errors.consent}</Text>}

        <Button label={t('register', language)} onPress={handleRegister} loading={loading} />

        <TouchableOpacity
          style={styles.link}
          onPress={() => router.back()}
        >
          <Text style={styles.linkText}>
            {t('alreadyHaveAccount', language)}{' '}
            <Text style={styles.linkBold}>{t('login', language)}</Text>
          </Text>
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    backgroundColor: Colors.background,
    padding: Spacing.xl,
    gap: Spacing.sm,
  },
  title: {
    fontFamily: FontFamily.bold,
    fontSize: FontSize['2xl'],
    color: Colors.textPrimary,
    marginBottom: 4,
  },
  subtitle: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.sm,
    color: Colors.textMuted,
    marginBottom: Spacing.md,
  },
  errorBanner: {
    backgroundColor: Colors.errorBg,
    borderRadius: 10,
    padding: Spacing.md,
  },
  errorText: {
    fontFamily: FontFamily.medium,
    fontSize: FontSize.sm,
    color: Colors.error,
  },
  sectionLabel: {
    fontFamily: FontFamily.medium,
    fontSize: FontSize.sm,
    color: Colors.textSecondary,
    marginTop: Spacing.sm,
  },
  typeRow: { flexDirection: 'row', gap: Spacing.sm },
  typeOption: {
    flex: 1,
    alignItems: 'center',
    padding: Spacing.md,
    borderRadius: BorderRadius.md,
    borderWidth: 1.5,
    borderColor: Colors.border,
    backgroundColor: Colors.surface,
    gap: 4,
  },
  typeSelected: {
    borderColor: Colors.primary,
    backgroundColor: Colors.primaryTint,
  },
  typeIcon: { fontSize: 24 },
  typeLabel: {
    fontFamily: FontFamily.medium,
    fontSize: 11,
    color: Colors.textMuted,
    textAlign: 'center',
  },
  typeLabelSelected: { color: Colors.primary },
  consentRow: {
    flexDirection: 'row',
    gap: Spacing.sm,
    alignItems: 'flex-start',
    marginTop: Spacing.sm,
  },
  checkbox: {
    width: 22,
    height: 22,
    borderRadius: 6,
    borderWidth: 2,
    borderColor: Colors.borderStrong,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 2,
  },
  checkboxChecked: {
    backgroundColor: Colors.primary,
    borderColor: Colors.primary,
  },
  consentText: {
    flex: 1,
    fontFamily: FontFamily.regular,
    fontSize: FontSize.xs,
    color: Colors.textSecondary,
    lineHeight: FontSize.xs * 1.6,
  },
  errorSmall: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.xs,
    color: Colors.error,
  },
  link: { alignItems: 'center', padding: Spacing.md },
  linkText: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.sm,
    color: Colors.textSecondary,
  },
  linkBold: { fontFamily: FontFamily.bold, color: Colors.primary },
});
