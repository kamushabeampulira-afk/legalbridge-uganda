import React from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ActivityIndicator,
  ViewStyle,
  TextStyle,
  View,
  Platform,
} from 'react-native';
import { Colors } from '@/constants/Colors';
import { Spacing, BorderRadius } from '@/constants/Spacing';
import { FontFamily, FontSize } from '@/constants/Typography';

type Variant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
type Size = 'sm' | 'md' | 'lg';

interface ButtonProps {
  label: string;
  onPress: () => void;
  variant?: Variant;
  size?: Size;
  loading?: boolean;
  disabled?: boolean;
  fullWidth?: boolean;
  icon?: React.ReactNode;
  style?: ViewStyle;
  textStyle?: TextStyle;
}

export default function Button({
  label,
  onPress,
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  fullWidth = true,
  icon,
  style,
  textStyle,
}: ButtonProps) {
  const isDisabled = disabled || loading;

  const shadowStyle: ViewStyle = Platform.OS !== 'web'
    ? {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.1,
        shadowRadius: 3,
        elevation: 2,
      }
    : {};

  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={isDisabled}
      activeOpacity={0.8}
      style={[
        styles.base,
        shadowStyle,
        styles[variant],
        styles[`size_${size}` as keyof typeof styles],
        fullWidth && styles.fullWidth,
        isDisabled && styles.disabled,
        style,
      ]}
      accessibilityRole="button"
      accessibilityLabel={label}
      accessibilityState={{ disabled: isDisabled, busy: loading }}
    >
      {loading ? (
        <ActivityIndicator
          color={variant === 'outline' || variant === 'ghost' ? Colors.primaryDeepTeal : Colors.textOnPrimary}
          size="small"
        />
      ) : (
        <View style={styles.content}>
          {icon && <View style={styles.icon}>{icon}</View>}
          <Text style={[
            styles.text,
            styles[`text_${variant}` as keyof typeof styles] as TextStyle,
            styles[`textSize_${size}` as keyof typeof styles] as TextStyle,
            textStyle,
          ]}>
            {label}
          </Text>
        </View>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  base: {
    borderRadius: BorderRadius.lg,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 52,
    paddingHorizontal: Spacing.xl,
  },
  fullWidth: { width: '100%' },
  content: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center' },
  icon: { marginRight: Spacing.sm },

  // Variants
  primary: { backgroundColor: Colors.primaryDeepPurple },
  secondary: { backgroundColor: Colors.secondaryGold },
  outline: {
    backgroundColor: Colors.transparent,
    borderWidth: 2,
    borderColor: Colors.primaryDeepPurple,
  },
  ghost: { backgroundColor: Colors.transparent },
  danger: { backgroundColor: Colors.errorRed },

  // Text colour per variant
  text: { fontFamily: FontFamily.semiBold, letterSpacing: 0.2 },
  text_primary: { color: Colors.textOnPrimary },
  text_secondary: { color: Colors.textOnSecondary },
  text_outline: { color: Colors.primaryDeepPurple },
  text_ghost: { color: Colors.primaryDeepPurple },
  text_danger: { color: Colors.textOnPrimary },

  // Sizes
  size_sm: { minHeight: 40, paddingHorizontal: Spacing.base },
  size_md: { minHeight: 52, paddingHorizontal: Spacing.xl },
  size_lg: { minHeight: 60, paddingHorizontal: Spacing['2xl'] },

  textSize_sm: { fontSize: FontSize.sm },
  textSize_md: { fontSize: FontSize.base },
  textSize_lg: { fontSize: FontSize.md },

  disabled: { opacity: 0.5 },
});
