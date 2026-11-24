import React from 'react';
import { View, StyleSheet, ViewStyle } from 'react-native';
import { Colors } from '@/constants/Colors';
import { Spacing, BorderRadius } from '@/constants/Spacing';
import { webShadow } from '@/constants/Shadows';

interface CardProps {
  children: React.ReactNode;
  style?: ViewStyle;
  variant?: 'default' | 'elevated' | 'outlined' | 'teal' | 'peach' | 'success' | 'warning';
  padding?: keyof typeof Spacing;
}

export default function Card({ children, style, variant = 'default', padding = 'base' }: CardProps) {
  const shadowStyle =
    variant === 'default' ? webShadow.sm :
    variant === 'elevated' ? webShadow.md :
    variant === 'teal' ? webShadow.sm :
    undefined;

  return (
    <View style={[styles.base, styles[variant], shadowStyle, { padding: Spacing[padding] }, style]}>
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  base: { borderRadius: BorderRadius.lg, backgroundColor: Colors.surface },
  default: {},
  elevated: {},
  outlined: { borderWidth: 1.5, borderColor: Colors.border },
  // Variant names kept for compatibility: 'teal' = brand primary, 'peach' = soft gold accent surface
  teal: { backgroundColor: Colors.primary },
  peach: { backgroundColor: Colors.accentTint, borderWidth: 1, borderColor: Colors.borderAccent },
  success: { backgroundColor: Colors.successBg, borderLeftWidth: 4, borderLeftColor: Colors.success },
  warning: { backgroundColor: Colors.warningBg, borderLeftWidth: 4, borderLeftColor: Colors.warningBorder },
});
