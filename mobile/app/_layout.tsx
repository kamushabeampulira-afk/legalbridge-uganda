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
import { Colors } from '@/constants/Colors';

SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const checkAuth = useAppStore((s) => s.checkAuth);

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
        <Stack.Screen name="document/upload" options={{ title: 'Upload Document' }} />
        <Stack.Screen name="document/[id]" options={{ title: 'Document Explanation' }} />
        <Stack.Screen name="boda/stopped" options={{ title: 'Stopped by an Officer' }} />
        <Stack.Screen name="vendor/eviction" options={{ title: 'Eviction Guidance' }} />
        <Stack.Screen name="voice" options={{ title: 'Speak to LegalBridge' }} />
        <Stack.Screen name="legal-help" options={{ title: 'Find Legal Help' }} />
        <Stack.Screen name="ask" options={{ title: 'Ask LegalBridge' }} />
      </Stack>
    </GestureHandlerRootView>
  );
}
