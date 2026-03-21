// ─── Document Feature Types ──────────────────────────────────────────────────

export type DocumentStatus = "processing" | "ready" | "failed";

export interface Document {
  id: string;
  filename: string;
  status: DocumentStatus;
  uploadedAt: string;
  /** Number of chunks after processing */
  chunkCount?: number;
  /** File size in bytes */
  fileSize?: number;
  /** MIME type */
  mimeType?: string;
  /** Processing error message if status === "failed" */
  error?: string;
}

export interface UploadProgress {
  filename: string;
  progress: number; // 0-100
  status: "uploading" | "processing" | "done" | "error";
  error?: string;
}
