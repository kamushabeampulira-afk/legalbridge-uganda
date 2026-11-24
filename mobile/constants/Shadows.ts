/**
 * Web-safe shadow styles.
 * On web, React Native Web doesn't support shadowOffset (an object) inside
 * StyleSheet.create at module level. Use these as inline styles or spread
 * them outside StyleSheet.create with Platform.select.
 *
 * Usage:  style={[styles.card, webShadow.sm]}
 */
import { Platform, ViewStyle } from 'react-native';

const nativeSm: ViewStyle = {
  shadowColor: '#000',
  shadowOffset: { width: 0, height: 1 },
  shadowOpacity: 0.08,
  shadowRadius: 3,
  elevation: 2,
};
const nativeMd: ViewStyle = {
  shadowColor: '#000',
  shadowOffset: { width: 0, height: 2 },
  shadowOpacity: 0.12,
  shadowRadius: 6,
  elevation: 4,
};
const nativeLg: ViewStyle = {
  shadowColor: '#000',
  shadowOffset: { width: 0, height: 4 },
  shadowOpacity: 0.16,
  shadowRadius: 12,
  elevation: 8,
};

// On web use CSS boxShadow; on native use the RN shadow props
export const webShadow = {
  sm: Platform.select<ViewStyle>({
    web: { boxShadow: '0 1px 3px rgba(0,0,0,0.10)' } as any,
    default: nativeSm,
  })!,
  md: Platform.select<ViewStyle>({
    web: { boxShadow: '0 2px 8px rgba(0,0,0,0.13)' } as any,
    default: nativeMd,
  })!,
  lg: Platform.select<ViewStyle>({
    web: { boxShadow: '0 4px 16px rgba(0,0,0,0.18)' } as any,
    default: nativeLg,
  })!,
};
