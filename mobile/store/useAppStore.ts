/**
 * LegalBridge — Global app state (Zustand).
 * Manages auth, user profile, language, and navigation state.
 */
import { create } from 'zustand';
import { tokenStorage, authApi, userApi } from '@/services/api';
import { normalizeLanguage, type Language } from '@/i18n/translations';

export type { Language } from '@/i18n/translations';
export type UserType = 'boda_boda' | 'market_vendor' | 'general';

export interface UserProfile {
  id: string;
  phone_number: string;
  full_name: string;
  user_type: UserType;
  preferred_language: Language;
  is_verified: boolean;
}

interface AppState {
  // Auth
  isAuthenticated: boolean;
  isLoading: boolean;
  user: UserProfile | null;

  // Language — persists user preference
  language: Language;

  // Actions
  checkAuth: () => Promise<void>;
  login: (phone: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  setLanguage: (lang: Language) => void;
  setUser: (user: UserProfile) => void;
  refreshProfile: () => Promise<void>;
}

export const useAppStore = create<AppState>((set, get) => ({
  isAuthenticated: false,
  isLoading: true,
  user: null,
  language: 'en',

  checkAuth: async () => {
    set({ isLoading: true });
    try {
      const token = await tokenStorage.getAccess();
      if (token) {
        const profile = await userApi.getProfile();
        set({
          isAuthenticated: true,
          user: profile,
          language: normalizeLanguage(profile.preferred_language),
          isLoading: false,
        });
      } else {
        set({ isAuthenticated: false, user: null, isLoading: false });
      }
    } catch {
      await tokenStorage.clear();
      set({ isAuthenticated: false, user: null, isLoading: false });
    }
  },

  login: async (phone: string, password: string) => {
    await authApi.login(phone, password);
    const profile = await userApi.getProfile();
    set({
      isAuthenticated: true,
      user: profile,
      language: normalizeLanguage(profile.preferred_language),
    });
  },

  logout: async () => {
    await authApi.logout();
    set({ isAuthenticated: false, user: null });
  },

  setLanguage: (lang: Language) => {
    const language = normalizeLanguage(lang);
    set({ language });
    // Sync to backend if authenticated
    if (get().isAuthenticated) {
      userApi.setLanguage(language).catch(() => null);
    }
  },

  setUser: (user: UserProfile) => set({ user }),

  refreshProfile: async () => {
    try {
      const profile = await userApi.getProfile();
      set({ user: profile });
    } catch {
      // silent
    }
  },
}));
