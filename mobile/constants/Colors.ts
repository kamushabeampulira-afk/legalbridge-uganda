/**
 * LegalBridge design tokens: Justice Week 2026 visual identity.
 *
 * Three layers:
 *   Palette   raw brand colours from the Justice Week 2026 participant badge.
 *             Do NOT use these directly in components.
 *   Colors    semantic tokens named by ROLE (primary, textMuted, warningBg...).
 *             Components use only these, so the identity can change in one place.
 *   Gradients the single brand gradient, for hero areas only.
 *
 * Accessibility (WCAG 2.1 AA), checked for every pairing the app uses:
 *   - Body text tokens are >= 4.5:1 on background, surface, surfaceMuted and all *Tint/*Bg surfaces.
 *   - textOnPrimary (white) is 7.2:1 on primary and 4.6:1 on secondary.
 *   - accent (champagne gold) is decorative: borders, tints, icons on primary. It is only 2.1:1 on
 *     ivory, so NEVER use it for text on light backgrounds; use accentText (4.9:1) instead.
 *   - secondary (berry) is 4.1:1 on ivory: fine for icons and large text, but use secondaryText for
 *     small text on light backgrounds.
 *   - borderStrong is >= 3:1 so input outlines are visible (WCAG 1.4.11).
 */

export const Palette = {
  justiceMagenta: '#922F7C',
  berryPurple: '#AD5790',
  champagneGold: '#C5A17D',
  warmIvory: '#F5F1EC',
  justiceCharcoal: '#41474A',
  white: '#FFFFFF',
} as const;

export const Colors = {
  // ── Brand ──────────────────────────────────────────────────────────────────
  /** Justice Magenta: primary buttons, active navigation, important actions, links */
  primary: Palette.justiceMagenta,
  /** Pressed/active state of primary elements */
  primaryPressed: '#782766',
  /** Very light magenta surface: selected options, highlighted cards */
  primaryTint: '#F5ECF3',

  /** Berry Purple: secondary buttons, gradients, highlights (complements primary) */
  secondary: Palette.berryPurple,
  /** Berry for small text on light backgrounds (berry itself is too light for small text) */
  secondaryText: '#9D4F83',
  secondaryTint: '#F7EEF4',

  /** Champagne Gold: small accents, borders, icons on primary. Never small text on light backgrounds. */
  accent: Palette.champagneGold,
  /** Gold for icons/graphics on light backgrounds (>= 3:1) */
  accentStrong: '#9E8164',
  /** Gold-family text on light backgrounds (>= 4.5:1) */
  accentText: '#7C654F',
  accentTint: '#F6F0EA',

  // ── Surfaces ───────────────────────────────────────────────────────────────
  /** Warm Ivory: screen backgrounds */
  background: Palette.warmIvory,
  /** White: cards, inputs, sheets */
  surface: Palette.white,
  /** Inset areas within cards (source lists, input fills) */
  surfaceMuted: '#EEEAE6',

  // ── Text ───────────────────────────────────────────────────────────────────
  /** Justice Charcoal: headings and body text */
  textPrimary: Palette.justiceCharcoal,
  textSecondary: '#53585A',
  /** Captions, hints, placeholders, inactive tabs (still >= 4.5:1) */
  textMuted: '#676A6C',
  textOnPrimary: Palette.white,
  /** Subtitles on primary (magenta) surfaces */
  textOnPrimaryMuted: '#E0C5DA',
  textLink: Palette.justiceMagenta,

  // ── On-primary overlays (controls placed on magenta headers) ───────────────
  onPrimarySubtle: 'rgba(255, 255, 255, 0.16)',
  onPrimaryBorder: 'rgba(255, 255, 255, 0.35)',

  // ── Borders ────────────────────────────────────────────────────────────────
  /** Decorative dividers and card outlines */
  border: '#E3E0DC',
  /** Form field outlines and other component boundaries (>= 3:1) */
  borderStrong: '#858787',
  borderFocus: Palette.justiceMagenta,
  borderAccent: Palette.champagneGold,

  // ── Status (fg >= 4.5:1 on its own Bg and on light surfaces) ───────────────
  success: '#2C7753',
  successBg: '#EAF2EE',
  successBorder: '#A1C5B3',
  warning: '#8A5A00',
  warningBg: '#FBF2E1',
  warningBorder: '#D9B26A',
  error: '#B3261E',
  errorBg: '#F9EEED',
  errorBorder: '#DD9D9A',
  info: '#2D6987',
  infoBg: '#EAF0F3',
  infoBorder: '#A1BCC9',

  // ── Misc ───────────────────────────────────────────────────────────────────
  overlay: 'rgba(65, 71, 74, 0.55)',
  shadow: Palette.justiceCharcoal,
  transparent: 'transparent',
} as const;

/** Magenta → berry. Use sparingly (hero areas). White text passes AA on both ends. */
export const Gradients = {
  brand: [Colors.primary, Colors.secondary] as const,
};

/** A 6-digit hex token at the given opacity, e.g. withAlpha(Colors.primary, 0.1) for an icon backdrop. */
export function withAlpha(hexColor: string, opacity: number): string {
  const h = hexColor.replace('#', '');
  const [r, g, b] = [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16));
  return `rgba(${r}, ${g}, ${b}, ${opacity})`;
}

export type ColorKey = keyof typeof Colors;
