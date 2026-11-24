/**
 * Document history screen — user's uploaded documents.
 */
import React, { useEffect, useState, useCallback } from 'react';
import {
  View, Text, StyleSheet, FlatList,
  TouchableOpacity, Alert, RefreshControl,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { documentsApi } from '@/services/api';
import { Colors, withAlpha } from '@/constants/Colors';
import { Spacing, BorderRadius } from '@/constants/Spacing';
import { webShadow } from '@/constants/Shadows';
import { FontFamily, FontSize } from '@/constants/Typography';
import { useAppStore } from '@/store/useAppStore';
import { t } from '@/i18n/translations';

const DOC_TYPE_ICONS: Record<string, { icon: string }> = {
  traffic_notice: { icon: '🚦' },
  police_charge: { icon: '👮' },
  eviction_notice: { icon: '🏚️' },
  allocation_slip: { icon: '📋' },
  payment_receipt: { icon: '🧾' },
  court_summons: { icon: '⚖️' },
  unknown: { icon: '📄' },
};

type StatusKey = 'status_ready' | 'status_processing' | 'status_failed' | 'status_uploaded' | 'status_unknown';

const STATUS_LABELS: Record<string, { labelKey: StatusKey; color: string }> = {
  completed: { labelKey: 'status_ready', color: Colors.success },
  processing: { labelKey: 'status_processing', color: Colors.primary },
  failed: { labelKey: 'status_failed', color: Colors.error },
  uploaded: { labelKey: 'status_uploaded', color: Colors.info },
};

export default function HistoryScreen() {
  const router = useRouter();
  const { language } = useAppStore();
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadDocuments = useCallback(async () => {
    try {
      const data = await documentsApi.getHistory();
      setDocuments(data.results ?? data);
    } catch {
      // silent — show empty state
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => { loadDocuments(); }, []);

  const handleDelete = (docId: string) => {
    Alert.alert(
      t('history_delete', language),
      t('history_confirmDelete', language),
      [
        { text: t('cancel', language), style: 'cancel' },
        {
          text: t('history_delete', language),
          style: 'destructive',
          onPress: async () => {
            try {
              await documentsApi.delete(docId);
              setDocuments((prev) => prev.filter((d) => d.id !== docId));
            } catch {
              Alert.alert(t('alert_error', language), t('error_generic', language));
            }
          },
        },
      ]
    );
  };

  const renderItem = ({ item }: { item: any }) => {
    const typeInfo = DOC_TYPE_ICONS[item.doc_type] ?? DOC_TYPE_ICONS.unknown;
    const statusInfo = STATUS_LABELS[item.status] ?? { labelKey: 'status_unknown' as StatusKey, color: Colors.textMuted };
    const date = new Date(item.created_at).toLocaleDateString('en-UG', {
      day: 'numeric', month: 'short', year: 'numeric',
    });

    return (
      <TouchableOpacity
        style={[styles.docCard, webShadow.sm]}
        onPress={() => router.push(`/document/${item.id}` as any)}
        activeOpacity={0.85}
      >
        <View style={styles.docLeft}>
          <Text style={styles.docIcon}>{typeInfo.icon}</Text>
        </View>
        <View style={styles.docInfo}>
          <Text style={styles.docName} numberOfLines={1}>
            {item.original_filename || t('document_defaultTitle', language)}
          </Text>
          <Text style={styles.docType}>
            {item.doc_type?.replace(/_/g, ' ') ?? t('history_unknownType', language)}
          </Text>
          <Text style={styles.docDate}>{date}</Text>
        </View>
        <View style={styles.docRight}>
          <View style={[styles.statusBadge, { backgroundColor: withAlpha(statusInfo.color, 0.12) }]}>
            <Text style={[styles.statusText, { color: statusInfo.color }]}>
              {t(statusInfo.labelKey, language)}
            </Text>
          </View>
          <TouchableOpacity
            onPress={() => handleDelete(item.id)}
            style={styles.deleteBtn}
            accessibilityLabel={t('history_delete', language)}
          >
            <Ionicons name="trash-outline" size={18} color={Colors.textMuted} />
          </TouchableOpacity>
        </View>
      </TouchableOpacity>
    );
  };

  if (!loading && documents.length === 0) {
    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyIcon}>📂</Text>
        <Text style={styles.emptyTitle}>{t('history_empty', language)}</Text>
        <TouchableOpacity
          style={styles.uploadBtn}
          onPress={() => router.push('/document/upload')}
        >
          <Ionicons name="cloud-upload" size={18} color={Colors.textOnPrimary} />
          <Text style={styles.uploadBtnText}>{t('uploadDocument', language)}</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={documents}
        keyExtractor={(item) => item.id}
        renderItem={renderItem}
        contentContainerStyle={styles.list}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={() => { setRefreshing(true); loadDocuments(); }}
            tintColor={Colors.primary}
          />
        }
        ItemSeparatorComponent={() => <View style={{ height: Spacing.sm }} />}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  list: { padding: Spacing.base, paddingBottom: Spacing['3xl'] },

  docCard: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.base,
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.md,
  },
  docLeft: {
    width: 48,
    height: 48,
    borderRadius: BorderRadius.md,
    backgroundColor: Colors.surfaceMuted,
    alignItems: 'center',
    justifyContent: 'center',
  },
  docIcon: { fontSize: 24 },
  docInfo: { flex: 1 },
  docName: {
    fontFamily: FontFamily.semiBold,
    fontSize: FontSize.base,
    color: Colors.textPrimary,
  },
  docType: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.xs,
    color: Colors.textMuted,
    marginTop: 2,
    textTransform: 'capitalize',
  },
  docDate: {
    fontFamily: FontFamily.regular,
    fontSize: FontSize.xs,
    color: Colors.textMuted,
    marginTop: 2,
  },
  docRight: { alignItems: 'flex-end', gap: Spacing.sm },
  statusBadge: {
    paddingHorizontal: Spacing.sm,
    paddingVertical: 3,
    borderRadius: BorderRadius.full,
  },
  statusText: {
    fontFamily: FontFamily.medium,
    fontSize: 11,
  },
  deleteBtn: { padding: 4 },

  emptyContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: Spacing['3xl'],
    backgroundColor: Colors.background,
    gap: Spacing.base,
  },
  emptyIcon: { fontSize: 64 },
  emptyTitle: {
    fontFamily: FontFamily.medium,
    fontSize: FontSize.md,
    color: Colors.textMuted,
    textAlign: 'center',
  },
  uploadBtn: {
    flexDirection: 'row',
    backgroundColor: Colors.primary,
    borderRadius: BorderRadius.lg,
    paddingHorizontal: Spacing.xl,
    paddingVertical: Spacing.md,
    gap: Spacing.sm,
    alignItems: 'center',
    marginTop: Spacing.base,
  },
  uploadBtnText: {
    fontFamily: FontFamily.semiBold,
    fontSize: FontSize.base,
    color: Colors.textOnPrimary,
  },
});
