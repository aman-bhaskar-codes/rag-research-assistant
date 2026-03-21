import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getDocuments, uploadDocument, deleteDocument } from "./api";

// ─── Query Keys ──────────────────────────────────────────────────────────────

export const documentKeys = {
  all: ["documents"] as const,
  list: () => [...documentKeys.all, "list"] as const,
};

// ─── Hooks ───────────────────────────────────────────────────────────────────

/**
 * Fetch all documents
 */
export function useDocuments() {
  return useQuery({
    queryKey: documentKeys.list(),
    queryFn: getDocuments,
    staleTime: 60_000, // 1 minute
  });
}

/**
 * Upload a document with progress tracking
 */
export function useUpload() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ file, onProgress }: { file: File; onProgress?: (p: number) => void }) =>
      uploadDocument(file, onProgress),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: documentKeys.list() });
    },
  });
}

/**
 * Delete a document
 */
export function useDeleteDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: documentKeys.list() });
    },
  });
}
