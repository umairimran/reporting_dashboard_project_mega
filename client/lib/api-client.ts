
import { toast } from "sonner";

const API_Base_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface FetchOptions extends RequestInit {
  params?: Record<string, string>;
  silent?: boolean;
}

export const apiClient = async <T>(endpoint: string, options: FetchOptions = {}): Promise<T> => {
  const { params, silent, ...init } = options;

  let url = `${API_Base_URL}${endpoint}`;
  if (params) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, value);
      }
    });
    url += `?${searchParams.toString()}`;
  }

  const response = await fetch(url, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init.headers,
    },
    credentials: "include", // Important for HttpOnly cookies
  });

  if (!response.ok) {
    // Handle 401 Unauthorized globally
    if (response.status === 401) {
      if (typeof window !== "undefined" && !window.location.pathname.startsWith("/login")) {
        // Force redirect to login which will trigger clean re-auth flow
        window.location.href = "/login";
      }
    }

    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || errorData.message || "An unexpected error occurred";

    // Toast error only if not silent
    if (!silent) {
      toast.error("Error", { description: message });
    }

    throw new Error(message);
  }

  return response.json();
};
