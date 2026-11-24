import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '@/constants/Colors';
import { Spacing, BorderRadius } from '@/constants/Spacing';
import { FontFamily, FontSize } from '@/constants/Typography';
import { useAppStore } from '@/store/useAppStore';
import { t } from '@/i18n/translations';

interface Props {
  message?: string;
}

export default function DisclaimerBanner({ message }: Props) {
  const language = useAppStore((s) => s.language);
  return (
    <View style={styles.container}>
      <Ionicons name="information-circle" size={18} color={Colors.accentSoftBlueDark} style={styles.icon} />
      <Text style={styles.text}>
        {message ?? t('disclaimer', language)}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    backgroundColor: '#E8F4FA',
    borderRadius: BorderRadius.md,
    padding: Spacing.md,
    marginVertical: Spacing.sm,
    alignItems: 'flex-start',
  },
  icon: { marginRight: Spacing.sm, marginTop: 1 },
  text: {
    flex: 1,
    fontFamily: FontFamily.regular,
    fontSize: FontSize.xs,
    color: Colors.accentSoftBlueDark,
    lineHeight: FontSize.xs * 1.6,
  },
});
