import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getSettings, updateSettings } from "./api";
import { useSettingsStore } from "./store";

// ─── Query Keys ──────────────────────────────────────────────────────────────

export const settingsKeys = {
  all: ["settings"] as const,
};

// ─── Hooks ───────────────────────────────────────────────────────────────────

/**
 * Fetch settings from backend and sync to Zustand store
 */
export function useSettings() {
  const { updateSettings: updateLocal } = useSettingsStore();

  return useQuery({
    queryKey: settingsKeys.all,
    queryFn: async () => {
      const settings = await getSettings();
      // Sync server settings → local store
      updateLocal(settings);
      return settings;
    },
    staleTime: 5 * 60_000, // 5 minutes
  });
}

/**
 * Save settings to backend
 */
export function useSaveSettings() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updateSettings,
    onSuccess: (data) => {
      queryClient.setQueryData(settingsKeys.all, data);
    },
  });
}
