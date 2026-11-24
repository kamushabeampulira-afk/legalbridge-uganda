/**
 * Hook: useDocumentAnalysis
 * Manages upload → OCR → analysis lifecycle with clean state.
 */
import { useState, useCallback } from 'react';
import { documentsApi } from '@/services/api';
import { useAppStore } from '@/store/useAppStore';

type Phase = 'idle' | 'uploading' | 'processing' | 'analyzing' | 'done' | 'error';

export function useDocumentAnalysis() {
  const language = useAppStore((s) => s.language);
  const [phase, setPhase] = useState<Phase>('idle');
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const upload = useCallback(async (
    uri: string,
    name: string,
    mimeType: string,
    userCategory: string,
  ) => {
    setPhase('uploading');
    setError(null);
    try {
      const uploadResult = await documentsApi.upload(uri, name, mimeType, userCategory, language);
      setDocumentId(uploadResult.id);
      setPhase('analyzing');

      const analysisResult = await documentsApi.analyze(uploadResult.id, language);
      setAnalysis(analysisResult);
      setPhase('done');
      return { documentId: uploadResult.id, analysis: analysisResult };
    } catch (err: any) {
      setError(err.message ?? 'Upload failed. Please try again.');
      setPhase('error');
      throw err;
    }
  }, [language]);

  const reset = useCallback(() => {
    setPhase('idle');
    setDocumentId(null);
    setAnalysis(null);
    setError(null);
  }, []);

  const isLoading = ['uploading', 'processing', 'analyzing'].includes(phase);

  const loadingMessage = {
    uploading: 'Uploading document...',
    processing: 'Reading your document...',
    analyzing: 'Analysing with LegalBridge...',
  }[phase as 'uploading' | 'processing' | 'analyzing'] ?? '';

  return { phase, documentId, analysis, error, isLoading, loadingMessage, upload, reset };
}
