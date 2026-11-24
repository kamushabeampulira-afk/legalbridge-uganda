/**
 * Profile & Settings screen.
 */
import React, { useState } from 'react';
import {
  View, Text, StyleSheet, ScrollView,
  TouchableOpacity, Alert, Switch,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '@/store/useAppStore';
import { userApi } from '@/services/api';
import { Colors } from '@/constants/Colors';
import { Spacing, BorderRadius } from '@/constants/Spacing';
import { webShadow } from '@/constants/Shadows';
import { FontFamily, FontSize } from '@/constants/Typography';
import { t } from '@/i18n/translations';

export default function ProfileScreen() {
  const router = useRouter();
  const { user, language, setLanguage, logout } = useAppStore();
  const [deleting, setDeleting] = useState(false);

  const handleLanguageToggle = () => {
    const next = language === 'en' ? 'lg' : 'en';
    setLanguage(next);
  };

  const handleLogout = () => {
    Alert.alert(
      t('profile_logout', language),
      language === 'lg' ? 'Ofuna okufuluma?' : 'Are you sure you want to log out?',
      [
        { text: t('cancel', language), style: 'cancel' },
        {
          text: t('profile_logout', language),
          onPress: async () => {
            await logout();
            router.replace('/(auth)/login');
          },
        },
      ]
    );
  };

  const handleDeleteAccount = () => {
    Alert.alert(
      t('profile_deleteAccount', language),
      t('profile_confirmDelete', language),
      [
        { text: t('cancel', language), style: 'cancel' },
        {
          text: t('profile_deleteAccount', language),
          style: 'destructive',
          onPress: async () => {
            setDeleting(true);
            try {
              await userApi.deleteAccount();
              await logout();
              router.replace('/(auth)/login');
            } catch {
              Alert.alert('Error', t('error_generic', language));
            } finally {
              setDeleting(false);
            }
          },
        },
      ]
    );
  };

  const SettingRow = ({
    icon, title, onPress, right, danger = false,
  }: {
    icon: string; title: string; onPress?: () => void;
    right?: React.ReactNode; danger?: boolean;
  }) => (
    <TouchableOpacity
      style={styles.row}
      onPress={onPress}
      disabled={!onPress}
      activeOpacity={onPress ? 0.7 : 1}
    >
      <Ionicons
        name={icon as any}
        size={22}
        color={danger ? Colors.errorRed : Colors.textSecondary}
        style={styles.rowIcon}
      />
      <Text style={[styles.rowTitle, danger && styles.dangerText]}>{title}</Text>
      {right ?? (onPress && (
        <Ionicons name="chevron-forward" size={18} color={Colors.textMuted} />
      ))}
    </TouchableOpacity>
  );

  return (
    <ScrollView
      style={styles.scroll}
      contentContainerStyle={styles.container}
      showsVerticalScrollIndicator={false}
    >
      {/* User card */}
      <View style={[styles.userCard, webShadow.md]}>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>
            {user?.full_name ? user.full_name[0].toUpperCase() : '👤'}
          </Text>
        </View>
        <View>
          <Text style={styles.userName}>{user?.full_name || 'LegalBridge User'}</Text>
          <Text style={styles.userPhone}>{user?.phone_number}</Text>
          <Text style={styles.userType}>
            {user?.user_type?.replace(/_/g, ' ') ?? 'User'}
          </Text>
        </View>
      </View>

      {/* Settings sections */}
      <View style={[styles.section, webShadow.sm]}>
        <Text style={styles.sectionTitle}>{t('profile_language', language)}</Text>
        <SettingRow
          icon="language"
          title={language === 'en' ? 'English' : 'Luganda'}
          right={
            <Switch
              value={language === 'lg'}
              onValueChange={handleLanguageToggle}
              trackColor={{ false: Colors.borderMedium, true: Colors.primaryDeepTeal }}
              thumbColor={Colors.surfaceWhite}
            />
          }
        />
      </View>

      <View style={[styles.section, webShadow.sm]}>
        <Text style={styles.sectionTitle}>Account</Text>
        <SettingRow
          icon="person-outline"
          title="Edit Profile"
          onPress={() => {/* TODO: edit profile screen */}}
        />
        <SettingRow
          icon="document-text-outline"
          title={t('history_title', language)}
          onPress={() => router.push('/(tabs)/history')}
        />
        <SettingRow
          icon="people-outline"
          title={t('legalHelp_title', language)}
          onPress={() => router.push('/legal-help')}
        />
      </View>

      <View style={[styles.section, webShadow.sm]}>
        <Text style={styles.sectionTitle}>{t('profile_privacy', language)}</Text>
        <SettingRow
          icon="shield-outline"
          title={t('profile_privacy', language)}
          onPress={() => {/* TODO: privacy screen */}}
        />
        <SettingRow
          icon="help-circle-outline"
          title={t('profile_help', language)}
          onPress={() => {/* TODO: help screen */}}
        />
      </View>

      <View style={[styles.section, webShadow.sm]}>
        <SettingRow
          icon="log-out-outline"
          title={t('profile_logout', language)}
          onPress={handleLogout}
        />
        <SettingRow
          icon="trash-outline"
          title={t('profile_deleteAccount', language)}
          onPress={handleDeleteAccount}
          danger
        />
      </View>

      <Text style={styles.version}>LegalBridge Informal v1.0.0 · Hack4Justice 2026</Text>
      <Text style={styles.disclaimer}>
        LegalBridge provides legal information, not legal advice.
      </Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scroll: { flex: 1, backgroundColor: Colors.backgroundOffWhite },
  container: { padding: Spacing.base, paddingBottom: Spacing['3xl'], gap: Spacing.base },

  userCard: {
    backgroundColor: Colors.primaryDeepPurple,
    borderRadius: BorderRadius.xl,
    padding: Spacing.xl,
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.base,
  },
  avatar: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: 'rgba(255,255,255,0.2)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarText: {
    fontFamily: FontFamily.bold,
    fontSize: FontSize.xl,
    color: Colors.textOnPrimary,
  },
  userName: {
    fontFamily: FontFamily.bold,
    fontSize: FontSize.md,
    color: Colors.textOnPrimary,
  },
  userPhone: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.sm,
    color: Colors.accentSoftPeach,
    marginTop: 2,
  },
  userType: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.xs,
    color: 'rgba(255,255,255,0.6)',
    marginTop: 2,
    textTransform: 'capitalize',
  },

  section: {
    backgroundColor: Colors.surfaceWhite,
    borderRadius: BorderRadius.lg,
    overflow: 'hidden',
  },
  sectionTitle: {
    fontFamily: FontFamily.semiBold,
    fontSize: FontSize.xs,
    color: Colors.textMuted,
    textTransform: 'uppercase',
    letterSpacing: 0.8,
    paddingHorizontal: Spacing.base,
    paddingTop: Spacing.md,
    paddingBottom: Spacing.sm,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: Spacing.base,
    paddingVertical: Spacing.md,
    borderTopWidth: 1,
    borderTopColor: Colors.borderLight,
  },
  rowIcon: { marginRight: Spacing.md },
  rowTitle: {
    flex: 1,
    fontFamily: FontFamily.regular,
    fontSize: FontSize.base,
    color: Colors.textPrimary,
  },
  dangerText: { color: Colors.errorRed },

  version: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.xs,
    color: Colors.textMuted,
    textAlign: 'center',
  },
  disclaimer: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.xs,
    color: Colors.textMuted,
    textAlign: 'center',
  },
});
