import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '@/constants/Colors';
import { Spacing, BorderRadius } from '@/constants/Spacing';
import { FontFamily, FontSize } from '@/constants/Typography';

interface Props {
  message?: string;
}

export default function UncertaintyBanner({ message }: Props) {
  return (
    <View style={styles.container}>
      <Ionicons name="warning" size={20} color={Colors.warningMutedCoral} style={styles.icon} />
      <Text style={styles.text}>
        {message ??
          'No verified legal source was found for this document. ' +
          'Please seek assistance from a qualified legal professional or legal aid organisation.'}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    backgroundColor: Colors.warningLight,
    borderRadius: BorderRadius.md,
    borderLeftWidth: 4,
    borderLeftColor: Colors.warningMutedCoral,
    padding: Spacing.md,
    marginVertical: Spacing.sm,
    alignItems: 'flex-start',
  },
  icon: { marginRight: Spacing.sm, marginTop: 1 },
  text: {
    flex: 1,
    fontFamily: FontFamily.medium,
    fontSize: FontSize.sm,
    color: Colors.textPrimary,
    lineHeight: FontSize.sm * 1.6,
  },
});
