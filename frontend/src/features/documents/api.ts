import apiClient from "@/lib/api-client";
import type { Document } from "./types";

// ─── Documents API ───────────────────────────────────────────────────────────

/**
 * Upload a document for RAG processing
 */
export async function uploadDocument(
  file: File,
  onProgress?: (progress: number) => void
): Promise<Document> {
  const formData = new FormData();
  formData.append("file", file);

  const { data } = await apiClient.post<Document>("/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const percent = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        onProgress(percent);
      }
    },
  });

  return data;
}

/**
 * Fetch all uploaded documents
 */
export async function getDocuments(): Promise<Document[]> {
  const { data } = await apiClient.get<Document[]>("/documents");
  return data;
}

/**
 * Delete a document
 */
export async function deleteDocument(documentId: string): Promise<void> {
  await apiClient.delete(`/documents/${documentId}`);
}
