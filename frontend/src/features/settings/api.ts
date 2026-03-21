import apiClient from "@/lib/api-client";
import type { Settings } from "./types";

// ─── Settings API ────────────────────────────────────────────────────────────

/**
 * Fetch settings from the backend
 */
export async function getSettings(): Promise<Settings> {
  const { data } = await apiClient.get<Settings>("/settings");
  return data;
}

/**
 * Update settings on the backend
 */
export async function updateSettings(
  settings: Partial<Settings>
): Promise<Settings> {
  const { data } = await apiClient.put<Settings>("/settings", settings);
  return data;
}
