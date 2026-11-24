/**
 * Document upload screen.
 * Supports camera, gallery, and file picker. Previews before submission.
 */
import React, { useState } from 'react';
import {
  View, Text, StyleSheet, ScrollView,
  TouchableOpacity, Image, Alert, Platform,
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import * as ImagePicker from 'expo-image-picker';
import * as DocumentPicker from 'expo-document-picker';
import { Ionicons } from '@expo/vector-icons';
import { documentsApi } from '@/services/api';
import { Colors } from '@/constants/Colors';
import { Spacing, BorderRadius } from '@/constants/Spacing';
import { webShadow } from '@/constants/Shadows';
import { FontFamily, FontSize } from '@/constants/Typography';
import { useAppStore } from '@/store/useAppStore';
import { t } from '@/i18n/translations';
import Button from '@/components/ui/Button';
import LoadingOverlay from '@/components/ui/LoadingOverlay';
import DisclaimerBanner from '@/components/ui/DisclaimerBanner';

type PickedFile = {
  uri: string;
  name: string;
  mimeType: string;
  isImage: boolean;
};

export default function UploadScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ category?: string }>();
  const { language } = useAppStore();

  const userCategory = params.category ?? 'general';
  const [file, setFile] = useState<PickedFile | null>(null);
  const [uploading, setUploading] = useState(false);
  const [loadingMsg, setLoadingMsg] = useState('');

  // ── Pick methods ─────────────────────────────────────────────────────────

  const pickFromCamera = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert(t('alert_permissionNeeded', language), t('upload_cameraPermission', language));
      return;
    }
    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 0.85,
      allowsEditing: false,
    });
    if (!result.canceled && result.assets[0]) {
      const asset = result.assets[0];
      setFile({
        uri: asset.uri,
        name: `photo_${Date.now()}.jpg`,
        mimeType: 'image/jpeg',
        isImage: true,
      });
    }
  };

  const pickFromGallery = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert(t('alert_permissionNeeded', language), t('upload_photoPermission', language));
      return;
    }
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 0.85,
    });
    if (!result.canceled && result.assets[0]) {
      const asset = result.assets[0];
      setFile({
        uri: asset.uri,
        name: asset.fileName ?? `image_${Date.now()}.jpg`,
        mimeType: asset.mimeType ?? 'image/jpeg',
        isImage: true,
      });
    }
  };

  const pickFromFiles = async () => {
    const result = await DocumentPicker.getDocumentAsync({
      type: ['image/jpeg', 'image/png', 'application/pdf'],
      copyToCacheDirectory: true,
    });
    if (result.canceled) return;
    const asset = result.assets[0];
    setFile({
      uri: asset.uri,
      name: asset.name,
      mimeType: asset.mimeType ?? 'application/pdf',
      isImage: asset.mimeType?.startsWith('image/') ?? false,
    });
  };

  // ── Submit ────────────────────────────────────────────────────────────────

  const handleSubmit = async () => {
    if (!file) return;
    setUploading(true);
    setLoadingMsg(t('uploading', language));

    try {
      setLoadingMsg(t('processing', language));
      const uploadResult = await documentsApi.upload(
        file.uri, file.name, file.mimeType, userCategory, language
      );
      const docId = uploadResult.id;

      setLoadingMsg(t('analyzing', language));
      await documentsApi.analyze(docId, language);

      router.replace(`/document/${docId}` as any);
    } catch (err: any) {
      Alert.alert(t('alert_uploadFailed', language), err.message ?? t('error_generic', language));
    } finally {
      setUploading(false);
      setLoadingMsg('');
    }
  };

  return (
    <ScrollView
      style={styles.scroll}
      contentContainerStyle={styles.container}
      showsVerticalScrollIndicator={false}
    >
      <LoadingOverlay visible={uploading} message={loadingMsg} />

      <Text style={styles.title}>{t('uploadDocument', language)}</Text>
      <Text style={styles.subtitle}>
        {userCategory === 'boda_boda'
          ? t('upload_hint_boda', language)
          : userCategory === 'market_vendor'
          ? t('upload_hint_vendor', language)
          : t('upload_hint_general', language)}
      </Text>

      {/* Pick options */}
      {!file && (
        <View style={styles.pickOptions}>
          <TouchableOpacity
            style={[styles.pickCard, { backgroundColor: '#EDE8F5' }, webShadow.sm]}
            onPress={pickFromCamera}
            activeOpacity={0.8}
            accessibilityLabel={t('takePhoto', language)}
          >
            <Ionicons name="camera" size={36} color={Colors.primaryDeepPurple} />
            <Text style={[styles.pickLabel, { color: Colors.primaryDeepPurple }]}>
              {t('takePhoto', language)}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.pickCard, { backgroundColor: '#FDF3DC' }, webShadow.sm]}
            onPress={pickFromGallery}
            activeOpacity={0.8}
            accessibilityLabel={t('chooseGallery', language)}
          >
            <Ionicons name="images" size={36} color={Colors.secondaryGold} />
            <Text style={[styles.pickLabel, { color: Colors.secondaryGold }]}>
              {t('chooseGallery', language)}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.pickCard, { backgroundColor: '#E8F4FA', flex: undefined, width: '100%' }, webShadow.sm]}
            onPress={pickFromFiles}
            activeOpacity={0.8}
            accessibilityLabel={t('chooseFile', language)}
          >
            <Ionicons name="document" size={36} color={Colors.accentSoftBlueDark} />
            <Text style={[styles.pickLabel, { color: Colors.accentSoftBlueDark }]}>
              {t('chooseFile', language)} (PDF)
            </Text>
          </TouchableOpacity>
        </View>
      )}

      {/* File preview */}
      {file && (
        <View style={styles.preview}>
          {file.isImage ? (
            <Image source={{ uri: file.uri }} style={styles.previewImage} resizeMode="contain" />
          ) : (
            <View style={styles.pdfPreview}>
              <Ionicons name="document-text" size={56} color={Colors.primaryDeepTeal} />
              <Text style={styles.pdfName}>{file.name}</Text>
            </View>
          )}
          <TouchableOpacity
            style={styles.removeBtn}
            onPress={() => setFile(null)}
            accessibilityLabel={t('removeDocument', language)}
          >
            <Ionicons name="close-circle" size={28} color={Colors.errorRed} />
            <Text style={styles.removeText}>{t('removeDocument', language)}</Text>
          </TouchableOpacity>

          <Button
            label={t('submitForAnalysis', language)}
            onPress={handleSubmit}
            loading={uploading}
          />
        </View>
      )}

      {/* Formats notice */}
      <View style={styles.formatsBox}>
        <Ionicons name="information-circle-outline" size={16} color={Colors.textMuted} />
        <Text style={styles.formatsText}>{t('supportedFormats', language)}</Text>
      </View>

      <DisclaimerBanner />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scroll: { flex: 1, backgroundColor: Colors.backgroundOffWhite },
  container: { padding: Spacing.base, paddingBottom: Spacing['3xl'], gap: Spacing.base },

  title: {
    fontFamily: FontFamily.bold,
    fontSize: FontSize.xl,
    color: Colors.textPrimary,
  },
  subtitle: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.sm,
    color: Colors.textMuted,
    lineHeight: FontSize.sm * 1.6,
  },

  pickOptions: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: Spacing.md,
  },
  pickCard: {
    flex: 1,
    minWidth: '45%',
    borderRadius: BorderRadius.xl,
    padding: Spacing.xl,
    alignItems: 'center',
    gap: Spacing.sm,
  },
  pickLabel: {
    fontFamily: FontFamily.semiBold,
    fontSize: FontSize.sm,
    textAlign: 'center',
  },

  preview: { gap: Spacing.base },
  previewImage: {
    width: '100%',
    height: 260,
    borderRadius: BorderRadius.lg,
    backgroundColor: Colors.surfaceLight,
  },
  pdfPreview: {
    backgroundColor: Colors.surfaceLight,
    borderRadius: BorderRadius.lg,
    padding: Spacing['2xl'],
    alignItems: 'center',
    gap: Spacing.sm,
  },
  pdfName: {
    fontFamily: FontFamily.medium,
    fontSize: FontSize.sm,
    color: Colors.textSecondary,
    textAlign: 'center',
  },
  removeBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: Spacing.sm,
    padding: Spacing.sm,
  },
  removeText: {
    fontFamily: FontFamily.medium,
    fontSize: FontSize.sm,
    color: Colors.errorRed,
  },

  formatsBox: {
    flexDirection: 'row',
    gap: Spacing.xs,
    alignItems: 'center',
    justifyContent: 'center',
  },
  formatsText: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.xs,
    color: Colors.textMuted,
  },
});
