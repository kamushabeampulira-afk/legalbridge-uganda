/**
 * LegalBridge — API service layer.
 * All backend calls go through this module.
 */
import axios, { AxiosInstance, AxiosError } from 'axios';
import type { Language } from '@/i18n/translations';
import { Platform } from 'react-native';

// ── Config ──────────────────────────────────────────────────────────────────
// Set EXPO_PUBLIC_API_URL to point the app at a deployed backend.
// For device testing on the same LAN, use your machine's IP instead.
const BASE_URL =
  process.env.EXPO_PUBLIC_API_URL ||
  (__DEV__
    ? 'http://localhost:8000/api'
    : 'https://api.legalbridgeug.org/api');

const TOKEN_KEY = 'lb_access_token';
const REFRESH_KEY = 'lb_refresh_token';

// ── Client ───────────────────────────────────────────────────────────────────
const apiClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

// ── Token management ─────────────────────────────────────────────────────────
// expo-secure-store is native-only. On web, fall back to localStorage.
const isWeb = typeof window !== 'undefined' && typeof window.document !== 'undefined';

export const tokenStorage = {
  save: async (access: string, refresh: string) => {
    if (isWeb) {
      localStorage.setItem(TOKEN_KEY, access);
      localStorage.setItem(REFRESH_KEY, refresh);
    } else {
      const SecureStore = await import('expo-secure-store');
      await SecureStore.default.setItemAsync(TOKEN_KEY, access);
      await SecureStore.default.setItemAsync(REFRESH_KEY, refresh);
    }
  },
  getAccess: async () => {
    if (isWeb) return localStorage.getItem(TOKEN_KEY);
    const SecureStore = await import('expo-secure-store');
    return SecureStore.default.getItemAsync(TOKEN_KEY);
  },
  getRefresh: async () => {
    if (isWeb) return localStorage.getItem(REFRESH_KEY);
    const SecureStore = await import('expo-secure-store');
    return SecureStore.default.getItemAsync(REFRESH_KEY);
  },
  clear: async () => {
    if (isWeb) {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(REFRESH_KEY);
    } else {
      const SecureStore = await import('expo-secure-store');
      await SecureStore.default.deleteItemAsync(TOKEN_KEY);
      await SecureStore.default.deleteItemAsync(REFRESH_KEY);
    }
  },
};

// ── Request interceptor: attach bearer token ─────────────────────────────────
apiClient.interceptors.request.use(async (config) => {
  const token = await tokenStorage.getAccess();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ── Response interceptor: auto-refresh token ─────────────────────────────────
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as any;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      try {
        const refresh = await tokenStorage.getRefresh();
        if (!refresh) throw new Error('No refresh token');
        const res = await axios.post(`${BASE_URL}/auth/token/refresh/`, { refresh });
        const newAccess: string = res.data.access;
        await tokenStorage.save(newAccess, refresh);
        original.headers.Authorization = `Bearer ${newAccess}`;
        return apiClient(original);
      } catch {
        await tokenStorage.clear();
      }
    }
    return Promise.reject(error);
  }
);

// ── Helpers ───────────────────────────────────────────────────────────────────
function extractErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data;
    if (typeof data === 'string') return data;
    if (data?.detail) return data.detail;
    if (data?.error) return data.error;
    if (data?.non_field_errors) return data.non_field_errors[0];
    const firstKey = Object.keys(data || {})[0];
    if (firstKey && Array.isArray(data[firstKey])) return `${firstKey}: ${data[firstKey][0]}`;
    if (error.message) return error.message;
  }
  return 'An unexpected error occurred. Please try again.';
}

// ── Auth ──────────────────────────────────────────────────────────────────────
export const authApi = {
  register: async (data: {
    phone_number: string;
    password: string;
    password_confirm: string;
    full_name?: string;
    user_type: string;
    preferred_language: Language;
    consented_to_processing: boolean;
  }) => {
    try {
      const res = await apiClient.post('/users/register/', data);
      return res.data;
    } catch (e) {
      throw new Error(extractErrorMessage(e));
    }
  },

  login: async (phone_number: string, password: string) => {
    try {
      const res = await apiClient.post('/auth/token/', { phone_number, password });
      await tokenStorage.save(res.data.access, res.data.refresh);
      return res.data;
    } catch (e) {
      throw new Error(extractErrorMessage(e));
    }
  },

  logout: async () => {
    await tokenStorage.clear();
  },
};

// ── User ──────────────────────────────────────────────────────────────────────
export const userApi = {
  getProfile: async () => {
    const res = await apiClient.get('/users/profile/');
    return res.data;
  },
  updateProfile: async (data: { full_name?: string; preferred_language?: Language }) => {
    const res = await apiClient.patch('/users/profile/', data);
    return res.data;
  },
  setLanguage: async (language: Language) => {
    const res = await apiClient.post('/users/language/', { language });
    return res.data;
  },
  deleteAccount: async () => {
    const res = await apiClient.delete('/users/delete/');
    return res.data;
  },
};

// ── File uploads ──────────────────────────────────────────────────────────────
// React Native's FormData accepts a { uri, name, type } object, but a browser's
// FormData would stringify it to "[object Object]". On web, read the picked
// file's blob:/data: URI into a real Blob instead.
async function appendFile(formData: FormData, field: string, uri: string, name: string, type: string) {
  if (isWeb) {
    const blob = await (await fetch(uri)).blob();
    formData.append(field, new File([blob], name, { type: blob.type || type }));
  } else {
    formData.append(field, { uri, name, type } as any);
  }
}

// ── Documents ─────────────────────────────────────────────────────────────────
export const documentsApi = {
  upload: async (fileUri: string, fileName: string, mimeType: string, userCategory: string, language: Language) => {
    const formData = new FormData();
    try {
      await appendFile(formData, 'file', fileUri, fileName, mimeType);
    } catch {
      throw new Error('Could not read the selected file. Please choose it again.');
    }
    formData.append('user_category', userCategory);
    formData.append('language', language);
    try {
      const res = await apiClient.post('/documents/upload/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return res.data;
    } catch (e) {
      throw new Error(extractErrorMessage(e));
    }
  },

  analyze: async (documentId: string, language: Language) => {
    try {
      const res = await apiClient.post(`/documents/${documentId}/analyze/`, { language });
      return res.data;
    } catch (e) {
      throw new Error(extractErrorMessage(e));
    }
  },

  getHistory: async () => {
    const res = await apiClient.get('/documents/history/');
    return res.data;
  },

  getDetail: async (documentId: string) => {
    const res = await apiClient.get(`/documents/${documentId}/`);
    return res.data;
  },

  delete: async (documentId: string) => {
    const res = await apiClient.delete(`/documents/${documentId}/delete/`);
    return res.data;
  },
};

// ── Legal ─────────────────────────────────────────────────────────────────────
export const legalApi = {
  ask: async (question: string, userCategory: string, language: Language) => {
    try {
      const res = await apiClient.post('/legal/ask/', { question, user_category: userCategory, language });
      return res.data;
    } catch (e) {
      throw new Error(extractErrorMessage(e));
    }
  },

  getCategories: async (subject?: string) => {
    const params = subject ? { subject } : {};
    const res = await apiClient.get('/legal/categories/', { params });
    return res.data;
  },
};

// ── AI Guided Scenarios ───────────────────────────────────────────────────────
export const aiApi = {
  bodaStopped: async (data: object) => {
    try {
      const res = await apiClient.post('/ai/boda-stopped/', data);
      return res.data;
    } catch (e) {
      throw new Error(extractErrorMessage(e));
    }
  },

  evictionGuidance: async (data: object) => {
    try {
      const res = await apiClient.post('/ai/eviction-guidance/', data);
      return res.data;
    } catch (e) {
      throw new Error(extractErrorMessage(e));
    }
  },
};

// ── Voice ─────────────────────────────────────────────────────────────────────
export const voiceApi = {
  transcribe: async (audioUri: string, language: Language) => {
    const formData = new FormData();
    // Expo AV records WebM on web and M4A on native — tell the backend the truth.
    const isWeb = Platform.OS === 'web';
    try {
      // appendFile sends a real File on web (a { uri } object would arrive as "[object Object]")
      await appendFile(
        formData,
        'audio',
        audioUri,
        isWeb ? 'recording.webm' : 'recording.m4a',
        isWeb ? 'audio/webm' : 'audio/m4a',
      );
    } catch {
      throw new Error('Could not read the recording. Please try again.');
    }
    formData.append('language', language);
    try {
      const res = await apiClient.post('/voice/transcribe/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 60000,
      });
      return res.data;
    } catch (e) {
      throw new Error(extractErrorMessage(e));
    }
  },

  synthesize: async (text: string, language: Language) => {
    try {
      const res = await apiClient.post('/voice/synthesize/', { text, language });
      return res.data;
    } catch (e) {
      throw new Error(extractErrorMessage(e));
    }
  },
};

// ── Referrals ─────────────────────────────────────────────────────────────────
export const referralsApi = {
  getLegalAid: async (params?: { district?: string; service_type?: string }) => {
    const res = await apiClient.get('/referrals/legal-aid/', { params });
    return res.data;
  },
  getProfessionals: async (params?: { district?: string }) => {
    const res = await apiClient.get('/referrals/professionals/', { params });
    return res.data;
  },
};

// ── Subscriptions ────────────────────────────────────────────────────────────
export const subscriptionsApi = {
  getPlans: async () => {
    const res = await apiClient.get('/subscriptions/plans/');
    return res.data;
  },
};

export default apiClient;
