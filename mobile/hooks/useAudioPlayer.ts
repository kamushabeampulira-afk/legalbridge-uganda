/**
 * Hook: useAudioPlayer
 * Manages expo-av Sound instance lifecycle cleanly.
 */
import { useState, useEffect, useCallback } from 'react';
import { Audio } from 'expo-av';

export function useAudioPlayer() {
  const [sound, setSound] = useState<Audio.Sound | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    return () => {
      sound?.unloadAsync();
    };
  }, [sound]);

  const play = useCallback(async (uri: string) => {
    // Unload previous
    if (sound) {
      await sound.unloadAsync();
      setSound(null);
    }
    setIsLoading(true);
    try {
      const { sound: newSound } = await Audio.Sound.createAsync(
        { uri },
        { shouldPlay: true }
      );
      setSound(newSound);
      setIsPlaying(true);
      newSound.setOnPlaybackStatusUpdate((status) => {
        if (!status.isLoaded) return;
        setIsPlaying(status.isPlaying);
        if ((status as any).didJustFinish) {
          setIsPlaying(false);
        }
      });
    } catch (e) {
      setIsPlaying(false);
    } finally {
      setIsLoading(false);
    }
  }, [sound]);

  const stop = useCallback(async () => {
    await sound?.stopAsync();
    setIsPlaying(false);
  }, [sound]);

  const pause = useCallback(async () => {
    await sound?.pauseAsync();
    setIsPlaying(false);
  }, [sound]);

  const resume = useCallback(async () => {
    await sound?.playAsync();
    setIsPlaying(true);
  }, [sound]);

  return { isPlaying, isLoading, play, stop, pause, resume };
}
