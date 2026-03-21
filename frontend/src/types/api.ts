// ─── Shared API Response / Error Types ────────────────────────────────────────

export interface ApiResponse<T> {
  data: T;
  status: string;
  message?: string;
}

export interface ApiError {
  message: string;
  code: number;
  details?: Record<string, unknown>;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}
