
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

  const headers = new Headers(init.headers);

  // Only set JSON content type if body is NOT FormData
  if (!(init.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(url, {
    ...init,
    headers,
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
    let message = errorData.detail || errorData.message || "An unexpected error occurred";

    // Handle FastAPI validation error array
    if (Array.isArray(message)) {
      message = message
        .map((err: any) => `${err.loc?.join(".")}: ${err.msg}`)
        .join(", ");
    } else if (typeof message === "object") {
      message = JSON.stringify(message);
    }

    // Toast error only if not silent
    if (!silent) {
      toast.error("Error", { description: message });
    }

    throw new Error(message);
  }

  return response.json();
};
