/**
 * LegalBridge Design System — Colour Palette
 * Hack4Justice 2026 theme: Purple + Gold + White + Soft Blue
 */
export const Colors = {
  // Primary — Deep Purple (matches Hack4Justice brand)
  primaryDeepPurple: '#5B2D8E',
  primaryDeepPurpleLight: '#7B4DB0',
  primaryDeepPurpleDark: '#3D1A6E',

  // Secondary — Gold / Amber
  secondaryGold: '#C9A84C',
  secondaryGoldLight: '#E4C46A',
  secondaryGoldDark: '#A07C2E',

  // Accent — Soft Blue (Hack4Justice slide background)
  accentSoftBlue: '#B8D8E8',
  accentSoftBlueMid: '#7FB8D4',
  accentSoftBlueDark: '#4A9ABF',

  // Semantic
  successLeafGreen: '#2A9D8F',
  successLight: '#E8F7F5',
  warningAmber: '#E9B44C',
  warningLight: '#FDF3DC',
  errorRed: '#C0392B',
  errorLight: '#FDECEA',
  infoBlue: '#4A9ABF',
  infoLight: '#E8F4FA',

  // Background
  backgroundOffWhite: '#FAFBFF',
  backgroundGrey: '#F4F5FB',
  backgroundDark: '#1A0D2E',

  // Surface
  surfaceWhite: '#FFFFFF',
  surfaceLight: '#F0F2FA',
  surfaceMedium: '#E2E5F5',

  // Text
  textPrimary: '#1A0D2E',
  textSecondary: '#4A3A6E',
  textMuted: '#8A80A8',
  textOnDark: '#FFFFFF',
  textOnPrimary: '#FFFFFF',
  textOnSecondary: '#1A0D2E',
  textOnGold: '#1A0D2E',

  // Border
  borderLight: '#E2E5F5',
  borderMedium: '#C8C2E0',
  borderFocus: '#5B2D8E',

  // Overlay
  overlay: 'rgba(26, 13, 46, 0.55)',
  overlayLight: 'rgba(26, 13, 46, 0.3)',

  // Transparent
  transparent: 'transparent',

  // Legacy aliases (keeps existing code working)
  primaryDeepTeal: '#5B2D8E',
  primaryDeepTealLight: '#7B4DB0',
  primaryDeepTealDark: '#3D1A6E',
  secondaryBurntOrange: '#C9A84C',
  secondaryBurntOrangeLight: '#E4C46A',
  secondaryBurntOrangeDark: '#A07C2E',
  accentSoftPeach: '#B8D8E8',
  accentSoftPeachLight: '#D4EAF4',
  warningMutedCoral: '#E9B44C',
} as const;

export type ColorKey = keyof typeof Colors;
