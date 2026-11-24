import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '@/constants/Colors';
import { Spacing, BorderRadius } from '@/constants/Spacing';
import { FontFamily, FontSize } from '@/constants/Typography';

interface Props {
  message?: string;
}

export default function DisclaimerBanner({ message }: Props) {
  return (
    <View style={styles.container}>
      <Ionicons name="information-circle" size={18} color={Colors.info} style={styles.icon} />
      <Text style={styles.text}>
        {message ??
          'This is legal information, not legal advice. For matters with serious consequences, consult a qualified lawyer.'}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    backgroundColor: Colors.infoBg,
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
    color: Colors.info,
    lineHeight: FontSize.xs * 1.6,
  },
});
