/**
 * Location-aware legal aid connection card.
 * Choose a district to see the published area office, then call it.
 * Counsel Doug and the toll-free line are shown as clearly labelled extra help.
 */
import React, { useMemo, useState } from 'react';
import {
  View, Text, StyleSheet, TouchableOpacity, Modal, FlatList,
  TextInput as RNTextInput, Linking,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '@/constants/Colors';
import { Spacing, BorderRadius } from '@/constants/Spacing';
import { webShadow } from '@/constants/Shadows';
import { FontFamily, FontSize } from '@/constants/Typography';
import { UGANDA_DISTRICTS, getLegalAidOffice, EXTRA_SUPPORT, telHref } from '@/constants/LegalAid';
import { useAppStore } from '@/store/useAppStore';
import { t } from '@/i18n/translations';

export default function LegalAidConnectCard() {
  const { language } = useAppStore();
  const [district, setDistrict] = useState('');
  const [pickerVisible, setPickerVisible] = useState(false);
  const [districtSearch, setDistrictSearch] = useState('');

  const office = getLegalAidOffice(district);
  const filteredDistricts = useMemo(
    () => UGANDA_DISTRICTS.filter((name) =>
      !districtSearch || name.toLowerCase().includes(districtSearch.trim().toLowerCase())
    ),
    [districtSearch]
  );

  const call = (phone: string) => Linking.openURL(telHref(phone));

  return (
    <View style={[styles.card, webShadow.sm]}>
      <View style={styles.cardHeader}>
        <View style={styles.iconBox}>
          <Ionicons name="people-circle" size={24} color={Colors.textOnPrimary} />
        </View>
        <View style={styles.headerText}>
          <Text style={styles.title}>{t('legalAidConnect_title', language)}</Text>
          <Text style={styles.subtitle}>{t('legalAidConnect_subtitle', language)}</Text>
        </View>
      </View>

      <TouchableOpacity
        style={styles.pickerButton}
        onPress={() => setPickerVisible(true)}
        activeOpacity={0.85}
        accessibilityRole="button"
        accessibilityLabel={t('legalAidConnect_chooseDistrict', language)}
      >
        <Ionicons name="location-outline" size={18} color={Colors.primary} />
        <Text style={[styles.pickerText, !district && styles.pickerPlaceholder]}>
          {district || t('legalAidConnect_chooseDistrict', language)}
        </Text>
        <Ionicons name="chevron-down" size={18} color={Colors.textMuted} />
      </TouchableOpacity>

      {district && office ? (
        <View style={styles.officeBox}>
          <Text style={styles.sectionLabel}>{t('legalAidConnect_areaOffice', language)}</Text>
          <Text style={styles.officeName}>{office.name}</Text>
          <Text style={styles.officeServes}>
            {t('legalAidConnect_serves', language)} {office.districts.join(', ')}
          </Text>

          {office.phones.map((phone) => (
            <View key={phone} style={styles.phoneRow}>
              <Ionicons name="call-outline" size={16} color={Colors.primary} />
              <Text style={styles.phoneRowText}>{phone}</Text>
              <TouchableOpacity
                style={styles.smallCallButton}
                onPress={() => call(phone)}
                activeOpacity={0.85}
                accessibilityLabel={`${t('legalHelp_call', language)} ${phone}`}
              >
                <Text style={styles.smallCallButtonText}>{t('legalHelp_call', language)}</Text>
              </TouchableOpacity>
            </View>
          ))}
        </View>
      ) : null}

      {district && !office ? (
        <View style={styles.noOfficeBox}>
          <Ionicons name="information-circle-outline" size={18} color={Colors.warning} />
          <Text style={styles.noOfficeText}>{t('legalAidConnect_noOffice', language)}</Text>
        </View>
      ) : null}

      <View style={styles.extraBox}>
        <Text style={styles.sectionLabel}>{t('legalAidConnect_extraHelp', language)}</Text>
        <Text style={styles.extraHint}>{t('legalAidConnect_extraHint', language)}</Text>

        <View style={styles.contactRow}>
          <View style={styles.contactInfo}>
            <Text style={styles.contactRole}>{t('legalAidConnect_officerLabel', language)}</Text>
            <Text style={styles.contactName}>{EXTRA_SUPPORT.officerName}</Text>
            <Text style={styles.phoneText}>{EXTRA_SUPPORT.officerPhone}</Text>
          </View>
          <TouchableOpacity
            style={[styles.callButton, styles.officerButton]}
            onPress={() => call(EXTRA_SUPPORT.officerPhone)}
            activeOpacity={0.85}
            accessibilityLabel={`${t('legalAidConnect_callDoug', language)} ${EXTRA_SUPPORT.officerPhone}`}
          >
            <Ionicons name="call" size={16} color={Colors.textOnPrimary} />
            <Text style={styles.callButtonText}>{t('legalAidConnect_callDoug', language)}</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.divider} />

        <View style={styles.contactRow}>
          <View style={styles.contactInfo}>
            <Text style={styles.contactRole}>{t('legalAidConnect_tollFree', language)}</Text>
            <Text style={styles.phoneText}>{EXTRA_SUPPORT.tollFreePhone}</Text>
          </View>
          <TouchableOpacity
            style={[styles.callButton, styles.tollFreeButton]}
            onPress={() => call(EXTRA_SUPPORT.tollFreePhone)}
            activeOpacity={0.85}
            accessibilityLabel={`${t('legalAidConnect_callTollFree', language)} ${EXTRA_SUPPORT.tollFreePhone}`}
          >
            <Ionicons name="call" size={16} color={Colors.textOnPrimary} />
            <Text style={styles.callButtonText}>{t('legalAidConnect_callTollFree', language)}</Text>
          </TouchableOpacity>
        </View>
      </View>

      <Text style={styles.note}>{t('legalAidConnect_note', language)}</Text>

      <Modal
        visible={pickerVisible}
        animationType="slide"
        transparent
        onRequestClose={() => setPickerVisible(false)}
      >
        <View style={styles.modalBackdrop}>
          <View style={styles.modalCard}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>{t('legalAidConnect_chooseDistrict', language)}</Text>
              <TouchableOpacity
                onPress={() => setPickerVisible(false)}
                accessibilityRole="button"
                accessibilityLabel={t('close', language)}
              >
                <Ionicons name="close" size={22} color={Colors.textPrimary} />
              </TouchableOpacity>
            </View>

            <View style={styles.modalSearch}>
              <Ionicons name="search" size={18} color={Colors.textMuted} />
              <RNTextInput
                style={styles.modalSearchInput}
                value={districtSearch}
                onChangeText={setDistrictSearch}
                placeholder={t('legalAidConnect_searchDistrict', language)}
                placeholderTextColor={Colors.textMuted}
              />
            </View>

            <FlatList
              data={filteredDistricts}
              keyExtractor={(item) => item}
              style={styles.districtList}
              renderItem={({ item }) => (
                <TouchableOpacity
                  style={styles.districtRow}
                  onPress={() => {
                    setDistrict(item);
                    setDistrictSearch('');
                    setPickerVisible(false);
                  }}
                  activeOpacity={0.7}
                >
                  <Text style={styles.districtRowText}>{item}</Text>
                  {district === item ? (
                    <Ionicons name="checkmark" size={18} color={Colors.primary} />
                  ) : null}
                </TouchableOpacity>
              )}
              ListEmptyComponent={
                <Text style={styles.noDistricts}>{t('legalAidConnect_noDistricts', language)}</Text>
              }
            />
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.xl,
    padding: Spacing.base,
    gap: Spacing.sm,
  },
  cardHeader: { flexDirection: 'row', alignItems: 'flex-start', gap: Spacing.sm },
  iconBox: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: Colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerText: { flex: 1 },
  title: { fontFamily: FontFamily.bold, fontSize: FontSize.base, color: Colors.textPrimary },
  subtitle: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.xs,
    color: Colors.textMuted,
    lineHeight: FontSize.xs * 1.5,
    marginTop: 2,
  },

  pickerButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    backgroundColor: Colors.surfaceMuted,
    borderRadius: BorderRadius.lg,
    borderWidth: 1.5,
    borderColor: Colors.border,
    paddingHorizontal: Spacing.base,
    minHeight: 48,
  },
  pickerText: { flex: 1, fontFamily: FontFamily.medium, fontSize: FontSize.sm, color: Colors.textPrimary },
  pickerPlaceholder: { color: Colors.textMuted },

  sectionLabel: {
    fontFamily: FontFamily.semiBold,
    fontSize: FontSize.xs,
    color: Colors.primary,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },

  officeBox: {
    backgroundColor: Colors.primaryTint,
    borderRadius: BorderRadius.lg,
    padding: Spacing.base,
    gap: Spacing.xs,
  },
  officeName: { fontFamily: FontFamily.bold, fontSize: FontSize.sm, color: Colors.textPrimary },
  officeServes: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.xs,
    color: Colors.textSecondary,
    lineHeight: FontSize.xs * 1.5,
    marginBottom: Spacing.xs,
  },
  phoneRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    paddingVertical: Spacing.sm,
    borderTopWidth: 1,
    borderTopColor: Colors.border,
  },
  phoneRowText: {
    flex: 1,
    fontFamily: FontFamily.medium,
    fontSize: FontSize.sm,
    color: Colors.textPrimary,
  },
  smallCallButton: {
    backgroundColor: Colors.primary,
    borderRadius: BorderRadius.full,
    paddingHorizontal: Spacing.md,
    paddingVertical: 6,
  },
  smallCallButtonText: {
    fontFamily: FontFamily.medium,
    fontSize: FontSize.xs,
    color: Colors.textOnPrimary,
  },

  noOfficeBox: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: Spacing.sm,
    backgroundColor: Colors.warningBg,
    borderRadius: BorderRadius.lg,
    padding: Spacing.base,
  },
  noOfficeText: {
    flex: 1,
    fontFamily: FontFamily.regular,
    fontSize: FontSize.xs,
    color: Colors.textSecondary,
    lineHeight: FontSize.xs * 1.6,
  },

  extraBox: {
    backgroundColor: Colors.surfaceMuted,
    borderRadius: BorderRadius.lg,
    padding: Spacing.base,
    gap: Spacing.sm,
  },
  extraHint: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.xs,
    color: Colors.textMuted,
    lineHeight: FontSize.xs * 1.5,
  },
  contactRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: Spacing.sm },
  contactInfo: { flex: 1 },
  contactRole: { fontFamily: FontFamily.regular, fontSize: FontSize.xs, color: Colors.textMuted },
  contactName: { fontFamily: FontFamily.semiBold, fontSize: FontSize.sm, color: Colors.textPrimary },
  phoneText: { fontFamily: FontFamily.bold, fontSize: FontSize.sm, color: Colors.textPrimary, marginTop: 2 },
  callButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.xs,
    borderRadius: BorderRadius.full,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
  },
  officerButton: { backgroundColor: Colors.secondary },
  tollFreeButton: { backgroundColor: Colors.primary },
  callButtonText: { fontFamily: FontFamily.medium, fontSize: FontSize.xs, color: Colors.textOnPrimary },
  divider: { height: 1, backgroundColor: Colors.border },

  note: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.xs,
    color: Colors.textSecondary,
    lineHeight: FontSize.xs * 1.5,
  },

  modalBackdrop: { flex: 1, backgroundColor: 'rgba(0,0,0,0.45)', justifyContent: 'flex-end' },
  modalCard: {
    maxHeight: '80%',
    backgroundColor: Colors.surface,
    borderTopLeftRadius: BorderRadius.xl,
    borderTopRightRadius: BorderRadius.xl,
    padding: Spacing.base,
    gap: Spacing.sm,
  },
  modalHeader: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  modalTitle: { fontFamily: FontFamily.bold, fontSize: FontSize.md, color: Colors.textPrimary },
  modalSearch: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    borderWidth: 1.5,
    borderColor: Colors.border,
    borderRadius: BorderRadius.lg,
    paddingHorizontal: Spacing.md,
    minHeight: 46,
  },
  modalSearchInput: {
    flex: 1,
    fontFamily: FontFamily.regular,
    fontSize: FontSize.sm,
    color: Colors.textPrimary,
  },
  districtList: { maxHeight: 380 },
  districtRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: Spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  districtRowText: { fontFamily: FontFamily.regular, fontSize: FontSize.sm, color: Colors.textPrimary },
  noDistricts: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.sm,
    color: Colors.textMuted,
    textAlign: 'center',
    paddingVertical: Spacing.xl,
  },
});
