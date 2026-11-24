import { StyleSheet } from 'react-native';

export const FontFamily = {
  regular: 'Inter_400Regular',
  medium: 'Inter_500Medium',
  semiBold: 'Inter_600SemiBold',
  bold: 'Inter_700Bold',
  // Noto Sans for Luganda text
  notoRegular: 'NotoSans_400Regular',
  notoBold: 'NotoSans_700Bold',
};

export const FontSize = {
  xs: 11,
  sm: 13,
  base: 15,
  md: 17,
  lg: 19,
  xl: 22,
  '2xl': 26,
  '3xl': 30,
  '4xl': 36,
};

export const LineHeight = {
  tight: 1.2,
  normal: 1.5,
  relaxed: 1.7,
};

export const Typography = StyleSheet.create({
  h1: {
    fontSize: FontSize['3xl'],
    fontFamily: FontFamily.bold,
    lineHeight: FontSize['3xl'] * 1.2,
  },
  h2: {
    fontSize: FontSize['2xl'],
    fontFamily: FontFamily.bold,
    lineHeight: FontSize['2xl'] * 1.3,
  },
  h3: {
    fontSize: FontSize.xl,
    fontFamily: FontFamily.semiBold,
    lineHeight: FontSize.xl * 1.3,
  },
  h4: {
    fontSize: FontSize.lg,
    fontFamily: FontFamily.semiBold,
    lineHeight: FontSize.lg * 1.4,
  },
  bodyLarge: {
    fontSize: FontSize.md,
    fontFamily: FontFamily.regular,
    lineHeight: FontSize.md * 1.6,
  },
  body: {
    fontSize: FontSize.base,
    fontFamily: FontFamily.regular,
    lineHeight: FontSize.base * 1.6,
  },
  bodySmall: {
    fontSize: FontSize.sm,
    fontFamily: FontFamily.regular,
    lineHeight: FontSize.sm * 1.5,
  },
  caption: {
    fontSize: FontSize.xs,
    fontFamily: FontFamily.regular,
    lineHeight: FontSize.xs * 1.4,
  },
  label: {
    fontSize: FontSize.sm,
    fontFamily: FontFamily.medium,
    lineHeight: FontSize.sm * 1.4,
  },
  button: {
    fontSize: FontSize.base,
    fontFamily: FontFamily.semiBold,
    lineHeight: FontSize.base * 1.2,
  },
  buttonSmall: {
    fontSize: FontSize.sm,
    fontFamily: FontFamily.semiBold,
    lineHeight: FontSize.sm * 1.2,
  },
});
