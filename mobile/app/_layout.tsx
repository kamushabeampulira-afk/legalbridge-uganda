import { useEffect } from 'react';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import {
  useFonts,
  Inter_400Regular,
  Inter_500Medium,
  Inter_600SemiBold,
  Inter_700Bold,
} from '@expo-google-fonts/inter';
import * as SplashScreen from 'expo-splash-screen';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { useAppStore } from '@/store/useAppStore';
import { t } from '@/i18n/translations';
import { Colors } from '@/constants/Colors';

SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const checkAuth = useAppStore((s) => s.checkAuth);
  const language = useAppStore((s) => s.language);

  const [fontsLoaded] = useFonts({
    Inter_400Regular,
    Inter_500Medium,
    Inter_600SemiBold,
    Inter_700Bold,
  });

  useEffect(() => {
    checkAuth();
  }, []);

  useEffect(() => {
    if (fontsLoaded) {
      SplashScreen.hideAsync();
    }
  }, [fontsLoaded]);

  if (!fontsLoaded) return null;

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <StatusBar style="light" backgroundColor={Colors.primary} />
      <Stack
        screenOptions={{
          headerStyle: { backgroundColor: Colors.primary },
          headerTintColor: Colors.textOnPrimary,
          headerTitleStyle: { fontFamily: 'Inter_600SemiBold', fontSize: 17 },
          contentStyle: { backgroundColor: Colors.background },
          headerBackTitle: '',
        }}
      >
        <Stack.Screen name="index" options={{ headerShown: false }} />
        <Stack.Screen name="onboarding" options={{ headerShown: false }} />
        <Stack.Screen name="language" options={{ headerShown: false }} />
        <Stack.Screen name="(auth)" options={{ headerShown: false }} />
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen name="document/upload" options={{ title: t('stack_uploadDocument', language) }} />
        <Stack.Screen name="document/[id]" options={{ title: t('stack_documentExplanation', language) }} />
        <Stack.Screen name="boda/stopped" options={{ title: t('stack_bodaStopped', language) }} />
        <Stack.Screen name="vendor/eviction" options={{ title: t('stack_vendorEviction', language) }} />
        <Stack.Screen name="voice" options={{ title: t('stack_voice', language) }} />
        <Stack.Screen name="legal-help" options={{ title: t('stack_legalHelp', language) }} />
        <Stack.Screen name="legal-aid" options={{ title: t('stack_legalAid', language) }} />
        <Stack.Screen name="ask" options={{ title: t('stack_ask', language) }} />
        <Stack.Screen name="rights" options={{ title: t('stack_rights', language) }} />
        <Stack.Screen name="ussd" options={{ title: t('stack_ussd', language) }} />
      </Stack>
    </GestureHandlerRootView>
  );
}
