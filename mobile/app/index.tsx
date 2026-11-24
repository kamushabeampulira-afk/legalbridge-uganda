/**
 * Entry point — routes to onboarding, language selection, or home.
 */
import { useEffect } from 'react';
import { View, Text, StyleSheet, Image } from 'react-native';
import { useRouter } from 'expo-router';
import { useAppStore } from '@/store/useAppStore';
import { Colors } from '@/constants/Colors';
import { FontFamily, FontSize } from '@/constants/Typography';
import AsyncStorage from '@react-native-async-storage/async-storage';

const ONBOARDING_KEY = 'lb_onboarding_done';

export default function IndexScreen() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAppStore();

  useEffect(() => {
    if (isLoading) return;
    const navigate = async () => {
      const onboardingDone = await AsyncStorage.getItem(ONBOARDING_KEY);
      if (!onboardingDone) {
        router.replace('/onboarding');
      } else if (!isAuthenticated) {
        router.replace('/(auth)/login');
      } else {
        router.replace('/(tabs)');
      }
    };
    navigate();
  }, [isLoading, isAuthenticated]);

  // Splash-like loading screen
  return (
    <View style={styles.container}>
      <View style={styles.logoArea}>
        <Text style={styles.logo}>⚖️</Text>
        <Text style={styles.name}>LegalBridge</Text>
        <Text style={styles.tagline}>Justice Within Reach</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.primaryDeepPurple,
    alignItems: 'center',
    justifyContent: 'center',
  },
  logoArea: { alignItems: 'center', gap: 12 },
  logo: { fontSize: 72 },
  name: {
    fontFamily: FontFamily.bold,
    fontSize: FontSize['3xl'],
    color: Colors.textOnPrimary,
    letterSpacing: 0.5,
  },
  tagline: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.md,
    color: Colors.accentSoftPeach,
    letterSpacing: 1,
  },
});
