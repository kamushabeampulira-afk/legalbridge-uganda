/**
 * Legal Help Directory — verified legal aid organisations and professionals.
 */
import React, { useEffect, useState } from 'react';
import {
  View, Text, StyleSheet, FlatList,
  TouchableOpacity, Linking, TextInput,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { referralsApi } from '@/services/api';
import { Colors } from '@/constants/Colors';
import { Spacing, BorderRadius } from '@/constants/Spacing';
import { webShadow } from '@/constants/Shadows';
import { FontFamily, FontSize } from '@/constants/Typography';
import { useAppStore } from '@/store/useAppStore';
import { t } from '@/i18n/translations';

export default function LegalHelpScreen() {
  const { language } = useAppStore();
  const [orgs, setOrgs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    referralsApi.getLegalAid()
      .then((data) => setOrgs(data.results ?? data))
      .catch(() => {/* show static fallback */})
      .finally(() => setLoading(false));
  }, []);

  const filtered = orgs.filter((o) =>
    !search || o.name.toLowerCase().includes(search.toLowerCase()) ||
    o.district?.toLowerCase().includes(search.toLowerCase())
  );

  const renderOrg = ({ item }: { item: any }) => (
    <View style={styles.orgCard}>
      <View style={styles.orgHeader}>
        <View style={styles.orgIconBox}>
          <Ionicons name="business" size={24} color={Colors.primary} />
        </View>
        <View style={styles.orgHeaderText}>
          <Text style={styles.orgName}>{item.name}</Text>
          {item.district ? (
            <Text style={styles.orgDistrict}>📍 {item.district}</Text>
          ) : null}
        </View>
        {item.is_free && (
          <View style={styles.freeBadge}>
            <Text style={styles.freeText}>{t('legalHelp_free', language)}</Text>
          </View>
        )}
      </View>

      {item.description ? (
        <Text style={styles.orgDesc}>{item.description}</Text>
      ) : null}

      {item.eligibility ? (
        <View style={styles.eligibilityBox}>
          <Ionicons name="people-outline" size={14} color={Colors.textMuted} />
          <Text style={styles.eligibilityText}>{item.eligibility}</Text>
        </View>
      ) : null}

      {item.consultation_info ? (
        <Text style={styles.consultInfo}>{item.consultation_info}</Text>
      ) : null}

      {/* Contact actions */}
      <View style={styles.contactRow}>
        {item.phone_number ? (
          <TouchableOpacity
            style={[styles.contactBtn, { backgroundColor: Colors.primaryTint }]}
            onPress={() => Linking.openURL(`tel:${item.phone_number}`)}
            accessibilityLabel={`Call ${item.name}`}
          >
            <Ionicons name="call" size={16} color={Colors.primary} />
            <Text style={[styles.contactBtnText, { color: Colors.primary }]}>
              {t('legalHelp_contact', language)}
            </Text>
          </TouchableOpacity>
        ) : null}

        {item.website ? (
          <TouchableOpacity
            style={[styles.contactBtn, { backgroundColor: Colors.secondaryTint }]}
            onPress={() => Linking.openURL(item.website)}
            accessibilityLabel={`Visit ${item.name} website`}
          >
            <Ionicons name="globe" size={16} color={Colors.secondary} />
            <Text style={[styles.contactBtnText, { color: Colors.secondaryText }]}>
              {t('legalHelp_website', language)}
            </Text>
          </TouchableOpacity>
        ) : null}
      </View>
    </View>
  );

  // Static fallback organisations (shown if API is unavailable)
  const fallbackOrgs = [
    {
      id: 'uls',
      name: 'Uganda Law Society',
      district: 'Kampala',
      description: 'Professional body for lawyers in Uganda. Referrals to qualified advocates.',
      phone_number: '+256414259808',
      website: 'https://www.uls.or.ug',
      is_free: false,
      eligibility: 'Open to all — provides referrals to member advocates.',
      consultation_info: 'Contact for referral to a qualified advocate in your area.',
    },
    {
      id: 'fida',
      name: 'FIDA Uganda',
      district: 'Kampala',
      description: 'Federation of Women Lawyers in Uganda. Free legal aid for women and families.',
      phone_number: '+256414530848',
      website: 'https://www.fidauganda.org',
      is_free: true,
      eligibility: 'Primarily women and families. Low-income individuals prioritised.',
      consultation_info: 'Walk-in and phone consultations available.',
    },
    {
      id: 'laspnet',
      name: 'Legal Aid Service Providers Network',
      district: 'National',
      description: 'Network of legal aid providers across Uganda.',
      phone_number: '',
      website: 'https://www.laspnet.org',
      is_free: true,
      eligibility: 'Low-income individuals. Eligibility varies by member organisation.',
      consultation_info: 'Contact to find the nearest legal aid provider in your district.',
    },
  ];

  const displayOrgs = filtered.length > 0 ? filtered : (loading ? [] : fallbackOrgs);

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>{t('legalHelp_title', language)}</Text>
        <Text style={styles.headerSub}>{t('legalHelp_subtitle', language)}</Text>
      </View>

      {/* Search */}
      <View style={styles.searchBox}>
        <Ionicons name="search" size={18} color={Colors.textMuted} style={styles.searchIcon} />
        <TextInput
          style={styles.searchInput}
          value={search}
          onChangeText={setSearch}
          placeholder={`${t('search', language)} by name or district...`}
          placeholderTextColor={Colors.textMuted}
        />
      </View>

      <FlatList
        data={displayOrgs}
        keyExtractor={(item) => item.id}
        renderItem={renderOrg}
        contentContainerStyle={styles.list}
        showsVerticalScrollIndicator={false}
        ItemSeparatorComponent={() => <View style={{ height: Spacing.md }} />}
        ListEmptyComponent={
          <View style={styles.emptyBox}>
            <Text style={styles.emptyText}>{t('legalHelp_noResults', language)}</Text>
          </View>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },

  header: {
    backgroundColor: Colors.primary,
    padding: Spacing.xl,
    paddingTop: Spacing.base,
    gap: 4,
  },
  headerTitle: { fontFamily: FontFamily.bold, fontSize: FontSize.xl, color: Colors.textOnPrimary },
  headerSub: { fontFamily: FontFamily.regular, fontSize: FontSize.sm, color: Colors.textOnPrimaryMuted },

  searchBox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.surface,
    marginHorizontal: Spacing.base,
    marginVertical: Spacing.base,
    borderRadius: BorderRadius.lg,
    paddingHorizontal: Spacing.base,
    borderWidth: 1.5,
    borderColor: Colors.border,
    minHeight: 48,
  },
  searchIcon: { marginRight: Spacing.sm },
  searchInput: {
    flex: 1,
    fontFamily: FontFamily.regular,
    fontSize: FontSize.base,
    color: Colors.textPrimary,
    paddingVertical: Spacing.md,
  },

  list: { paddingHorizontal: Spacing.base, paddingBottom: Spacing['3xl'] },

  orgCard: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.xl,
    padding: Spacing.base,
    gap: Spacing.sm,
  },
  orgHeader: { flexDirection: 'row', alignItems: 'flex-start', gap: Spacing.sm },
  orgIconBox: {
    width: 44, height: 44, borderRadius: 22,
    backgroundColor: Colors.primaryTint, alignItems: 'center', justifyContent: 'center',
  },
  orgHeaderText: { flex: 1 },
  orgName: { fontFamily: FontFamily.bold, fontSize: FontSize.base, color: Colors.textPrimary },
  orgDistrict: { fontFamily: FontFamily.regular, fontSize: FontSize.xs, color: Colors.textMuted, marginTop: 2 },
  freeBadge: {
    backgroundColor: Colors.successBg,
    paddingHorizontal: Spacing.sm,
    paddingVertical: 3,
    borderRadius: BorderRadius.full,
  },
  freeText: { fontFamily: FontFamily.medium, fontSize: 11, color: Colors.success },

  orgDesc: { fontFamily: FontFamily.regular, fontSize: FontSize.sm, color: Colors.textSecondary, lineHeight: FontSize.sm * 1.6 },

  eligibilityBox: {
    flexDirection: 'row', gap: Spacing.xs, alignItems: 'flex-start',
    backgroundColor: Colors.surfaceMuted, borderRadius: BorderRadius.sm, padding: Spacing.sm,
  },
  eligibilityText: { flex: 1, fontFamily: FontFamily.regular, fontSize: FontSize.xs, color: Colors.textMuted, lineHeight: FontSize.xs * 1.5 },

  consultInfo: { fontFamily: FontFamily.regular, fontSize: FontSize.xs, color: Colors.textSecondary, fontStyle: 'italic' },

  contactRow: { flexDirection: 'row', gap: Spacing.sm, flexWrap: 'wrap' },
  contactBtn: {
    flexDirection: 'row', alignItems: 'center', gap: Spacing.xs,
    paddingHorizontal: Spacing.md, paddingVertical: Spacing.sm,
    borderRadius: BorderRadius.full,
  },
  contactBtnText: { fontFamily: FontFamily.medium, fontSize: FontSize.xs },

  emptyBox: { alignItems: 'center', paddingVertical: Spacing['3xl'] },
  emptyText: { fontFamily: FontFamily.regular, fontSize: FontSize.base, color: Colors.textMuted, textAlign: 'center' },
});
