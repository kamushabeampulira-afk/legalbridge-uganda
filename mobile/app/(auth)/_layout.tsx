import { Stack } from 'expo-router';
import { Colors } from '@/constants/Colors';
import { useAppStore } from '@/store/useAppStore';
import { t } from '@/i18n/translations';

export default function AuthLayout() {
  const language = useAppStore((s) => s.language);

  return (
    <Stack
      screenOptions={{
        headerStyle: { backgroundColor: Colors.backgroundOffWhite },
        headerTintColor: Colors.primaryDeepTeal,
        headerTitleStyle: { fontFamily: 'Inter_600SemiBold' },
        contentStyle: { backgroundColor: Colors.backgroundOffWhite },
        headerShadowVisible: false,
      }}
    >
      <Stack.Screen name="login" options={{ headerShown: false }} />
      <Stack.Screen name="register" options={{ title: t('register', language) }} />
    </Stack>
  );
}
