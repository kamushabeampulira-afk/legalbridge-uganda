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

const { width } = Dimensions.get('window');
const ONBOARDING_KEY = 'lb_onboarding_done';

const slides = [
  {
    id: '1',
    icon: 'document-text' as const,
    title: 'Understand Your Documents',
    body: 'Photograph or upload any official document — traffic notices, eviction letters, market slips — and get a plain-language explanation.',
    color: Colors.primaryDeepPurple,
  },
  {
    id: '2',
    icon: 'shield-checkmark' as const,
    title: 'Know Your Rights',
    body: 'Find out what Ugandan law says about your situation. LegalBridge references verified legal sources — no guessing.',
    color: Colors.secondaryGold,
  },
  {
    id: '3',
    icon: 'footsteps' as const,
    title: 'Find Your Next Step',
    body: 'Get a practical checklist of things you can do, and connect with legal aid organisations and qualified lawyers.',
    color: Colors.accentSoftBlueDark,
  },
  {
    id: '4',
    icon: 'mic' as const,
    title: 'Speak or Type',
    body: 'Ask questions by voice or text in your chosen language. No internet? Dial our USSD service from any phone.',
    color: Colors.primaryDeepPurpleLight,
  },
];

export default function OnboardingScreen() {
  const router = useRouter();
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
          <Text style={styles.skipText}>Skip</Text>
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
          label={isLast ? 'Get Started' : 'Next'}
          onPress={handleNext}
          variant="primary"
        />
        {isLast && (
          <TouchableOpacity onPress={() => router.replace('/(auth)/login')} style={styles.loginLink}>
            <Text style={styles.loginText}>Already have an account? Log in</Text>
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
