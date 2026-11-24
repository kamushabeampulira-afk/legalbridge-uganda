import React, { useState, useRef } from 'react';
import {
  View, Text, StyleSheet, FlatList, Dimensions,
  TouchableOpacity, ViewToken,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Colors } from '@/constants/Colors';
import { Spacing, BorderRadius } from '@/constants/Spacing';
import { FontFamily, FontSize } from '@/constants/Typography';
import Button from '@/components/ui/Button';
import { useAppStore } from '@/store/useAppStore';
import { t } from '@/i18n/translations';

const { width } = Dimensions.get('window');
const ONBOARDING_KEY = 'lb_onboarding_done';

const getSlides = (language: 'en' | 'lg') => [
  {
    id: '1',
    icon: 'document-text' as const,
    title: t('onboarding_title_1', language),
    body: t('onboarding_body_1', language),
    color: Colors.primaryDeepPurple,
  },
  {
    id: '2',
    icon: 'shield-checkmark' as const,
    title: t('onboarding_title_2', language),
    body: t('onboarding_body_2', language),
    color: Colors.secondaryGold,
  },
  {
    id: '3',
    icon: 'footsteps' as const,
    title: t('onboarding_title_3', language),
    body: t('onboarding_body_3', language),
    color: Colors.accentSoftBlueDark,
  },
  {
    id: '4',
    icon: 'mic' as const,
    title: t('onboarding_title_4', language),
    body: t('onboarding_body_4', language),
    color: Colors.primaryDeepPurpleLight,
  },
];

export default function OnboardingScreen() {
  const router = useRouter();
  const language = useAppStore((s) => s.language);
  const slides = getSlides(language);
  const [currentIndex, setCurrentIndex] = useState(0);
  const flatListRef = useRef<FlatList>(null);

  const handleDone = async () => {
    await AsyncStorage.setItem(ONBOARDING_KEY, 'true');
    router.replace('/language');
  };

  const handleSkip = async () => {
    await AsyncStorage.setItem(ONBOARDING_KEY, 'true');
    router.replace('/(auth)/login');
  };

  const handleNext = () => {
    if (currentIndex < slides.length - 1) {
      flatListRef.current?.scrollToIndex({ index: currentIndex + 1 });
      setCurrentIndex(currentIndex + 1);
    } else {
      handleDone();
    }
  };

  const onViewableItemsChanged = useRef(({ viewableItems }: { viewableItems: ViewToken[] }) => {
    if (viewableItems[0]) setCurrentIndex(viewableItems[0].index ?? 0);
  }).current;

  const isLast = currentIndex === slides.length - 1;

  return (
    <View style={styles.container}>
      {/* Skip button */}
      <View style={styles.topBar}>
        <TouchableOpacity onPress={handleSkip} style={styles.skipBtn}>
          <Text style={styles.skipText}>{t('onboarding_skip', language)}</Text>
        </TouchableOpacity>
      </View>

      <FlatList
        ref={flatListRef}
        data={slides}
        keyExtractor={(item) => item.id}
        horizontal
        pagingEnabled
        showsHorizontalScrollIndicator={false}
        onViewableItemsChanged={onViewableItemsChanged}
        viewabilityConfig={{ viewAreaCoveragePercentThreshold: 50 }}
        renderItem={({ item }) => (
          <View style={[styles.slide, { width }]}>
            <View style={[styles.iconCircle, { backgroundColor: item.color }]}>
              <Ionicons name={item.icon} size={56} color={Colors.textOnPrimary} />
            </View>
            <Text style={styles.title}>{item.title}</Text>
            <Text style={styles.body}>{item.body}</Text>
          </View>
        )}
      />

      {/* Dots */}
      <View style={styles.dots}>
        {slides.map((_, i) => (
          <View
            key={i}
            style={[styles.dot, currentIndex === i && styles.dotActive]}
          />
        ))}
      </View>

      {/* CTA */}
      <View style={styles.buttonArea}>
        <Button
          label={isLast ? t('onboarding_getStarted', language) : t('onboarding_next', language)}
          onPress={handleNext}
          variant="primary"
        />
        {isLast && (
          <TouchableOpacity onPress={() => router.replace('/(auth)/login')} style={styles.loginLink}>
            <Text style={styles.loginText}>{t('onboarding_loginLink', language)}</Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.backgroundOffWhite },
  topBar: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    padding: Spacing.base,
    paddingTop: Spacing['2xl'],
  },
  skipBtn: { padding: Spacing.sm },
  skipText: {
    fontFamily: FontFamily.medium,
    fontSize: FontSize.sm,
    color: Colors.textMuted,
  },
  slide: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: Spacing['3xl'],
    gap: Spacing.xl,
  },
  iconCircle: {
    width: 120,
    height: 120,
    borderRadius: 60,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: Spacing.base,
  },
  title: {
    fontFamily: FontFamily.bold,
    fontSize: FontSize['2xl'],
    color: Colors.textPrimary,
    textAlign: 'center',
    lineHeight: FontSize['2xl'] * 1.3,
  },
  body: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.md,
    color: Colors.textSecondary,
    textAlign: 'center',
    lineHeight: FontSize.md * 1.7,
  },
  dots: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: Spacing.sm,
    marginBottom: Spacing.xl,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: Colors.borderMedium,
  },
  dotActive: {
    backgroundColor: Colors.primaryDeepPurple,
    width: 24,
  },
  buttonArea: {
    padding: Spacing.xl,
    paddingBottom: Spacing['3xl'],
    gap: Spacing.base,
  },
  loginLink: { alignItems: 'center', padding: Spacing.sm },
  loginText: {
    fontFamily: FontFamily.medium,
    fontSize: FontSize.sm,
    color: Colors.primaryDeepPurple,
  },
});
