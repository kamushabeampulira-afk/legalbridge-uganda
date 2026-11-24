/**
 * Profile & Settings screen.
 */
import React, { useState } from 'react';
import {
  View, Text, StyleSheet, ScrollView,
  TouchableOpacity, Alert,
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
import { LANGUAGES, getLanguageMeta } from '@/i18n/languages';

export default function ProfileScreen() {
  const router = useRouter();
  const { user, language, setLanguage, logout } = useAppStore();
  const [deleting, setDeleting] = useState(false);

  const handleLanguageCycle = () => {
    const index = LANGUAGES.findIndex((item) => item.code === language);
    const next = LANGUAGES[(index + 1) % LANGUAGES.length];
    setLanguage(next.code);
  };

  const handleLogout = () => {
    Alert.alert(
      t('profile_logout', language),
      t('profile_confirmLogout', language),
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
              Alert.alert(t('alert_error', language), t('error_generic', language));
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
        color={danger ? Colors.error : Colors.textSecondary}
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
          <Text style={styles.userName}>{user?.full_name || t('profile_defaultName', language)}</Text>
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
          title={`${getLanguageMeta(language).nativeName} · ${t('changeLanguage', language)}`}
          onPress={handleLanguageCycle}
        />
      </View>

      <View style={[styles.section, webShadow.sm]}>
        <Text style={styles.sectionTitle}>{t('profile_account', language)}</Text>
        <SettingRow
          icon="person-outline"
          title={t('profile_editProfile', language)}
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

      <Text style={styles.version}>{t('profile_versionText', language)}</Text>
      <Text style={styles.disclaimer}>{t('disclaimer', language)}</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scroll: { flex: 1, backgroundColor: Colors.background },
  container: { padding: Spacing.base, paddingBottom: Spacing['3xl'], gap: Spacing.base },

  userCard: {
    backgroundColor: Colors.primary,
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
    backgroundColor: Colors.onPrimarySubtle,
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
    color: Colors.textOnPrimaryMuted,
    marginTop: 2,
  },
  userType: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.xs,
    color: Colors.textOnPrimaryMuted,
    marginTop: 2,
    textTransform: 'capitalize',
  },

  section: {
    backgroundColor: Colors.surface,
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
    borderTopColor: Colors.border,
  },
  rowIcon: { marginRight: Spacing.md },
  rowTitle: {
    flex: 1,
    fontFamily: FontFamily.regular,
    fontSize: FontSize.base,
    color: Colors.textPrimary,
  },
  dangerText: { color: Colors.error },

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
