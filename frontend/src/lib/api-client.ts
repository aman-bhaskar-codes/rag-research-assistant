import axios from "axios";
import { API_BASE_URL } from "@/config/constants";

// ─── Axios Instance ──────────────────────────────────────────────────────────

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
});

// ─── Request Interceptor ────────────────────────────────────────────────────
// Future: attach auth tokens here

apiClient.interceptors.request.use(
  (config) => {
    // const token = getAuthToken();
    // if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
);

// ─── Response Interceptor ───────────────────────────────────────────────────

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (axios.isAxiosError(error)) {
      const message =
        error.response?.data?.detail ||
        error.response?.data?.message ||
        error.message ||
        "An unexpected error occurred";

      const normalizedError = {
        message,
        code: error.response?.status || 500,
        details: error.response?.data,
      };

      return Promise.reject(normalizedError);
    }
    return Promise.reject(error);
  }
);

export default apiClient;
