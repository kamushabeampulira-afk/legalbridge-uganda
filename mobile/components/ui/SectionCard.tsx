import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '@/constants/Colors';
import { Spacing, BorderRadius } from '@/constants/Spacing';
import { FontFamily, FontSize } from '@/constants/Typography';
import { webShadow } from '@/constants/Shadows';

interface Props {
  title: string;
  content: string | string[];
  iconName?: keyof typeof Ionicons.glyphMap;
  iconColor?: string;
  collapsible?: boolean;
  defaultOpen?: boolean;
}

export default function SectionCard({
  title,
  content,
  iconName,
  iconColor = Colors.primaryDeepTeal,
  collapsible = false,
  defaultOpen = true,
}: Props) {
  const [open, setOpen] = useState(defaultOpen);
  const isArray = Array.isArray(content);

  return (
    <View style={[styles.card, webShadow.sm]}>
      <TouchableOpacity
        style={styles.header}
        onPress={() => collapsible && setOpen(!open)}
        disabled={!collapsible}
        activeOpacity={collapsible ? 0.7 : 1}
        accessibilityRole={collapsible ? 'button' : undefined}
        accessibilityState={collapsible ? { expanded: open } : undefined}
      >
        {iconName && <Ionicons name={iconName} size={20} color={iconColor} style={styles.icon} />}
        <Text style={styles.title}>{title}</Text>
        {collapsible && (
          <Ionicons name={open ? 'chevron-up' : 'chevron-down'} size={18} color={Colors.textMuted} />
        )}
      </TouchableOpacity>

      {(!collapsible || open) && (
        <View style={styles.body}>
          {isArray
            ? (content as string[]).map((item, i) => (
                <View key={i} style={styles.listItem}>
                  <Text style={styles.bullet}>{i + 1}.</Text>
                  <Text style={styles.listText}>{item}</Text>
                </View>
              ))
            : <Text style={styles.text}>{content as string}</Text>
          }
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.surfaceWhite,
    borderRadius: BorderRadius.lg,
    marginBottom: Spacing.md,
    overflow: 'hidden',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: Spacing.base,
    backgroundColor: '#EDE8F5',
  },
  icon: { marginRight: Spacing.sm },
  title: {
    flex: 1,
    fontFamily: FontFamily.semiBold,
    fontSize: FontSize.sm,
    color: Colors.textPrimary,
    letterSpacing: 0.3,
  },
  body: { padding: Spacing.base, paddingTop: Spacing.md },
  text: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.base,
    color: Colors.textSecondary,
    lineHeight: FontSize.base * 1.7,
  },
  listItem: { flexDirection: 'row', marginBottom: Spacing.sm },
  bullet: {
    fontFamily: FontFamily.semiBold,
    fontSize: FontSize.base,
    color: Colors.primaryDeepPurple,
    marginRight: Spacing.sm,
    minWidth: 20,
  },
  listText: {
    flex: 1,
    fontFamily: FontFamily.regular,
    fontSize: FontSize.base,
    color: Colors.textSecondary,
    lineHeight: FontSize.base * 1.7,
  },
});
