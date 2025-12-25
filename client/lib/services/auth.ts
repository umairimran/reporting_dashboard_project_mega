
import { apiClient } from "@/lib/api-client";
import { User, LoginCredentials, RegisterData } from "@/types/auth"; // Need to ensure types exist or inline them



export const authService = {
    login: async (credentials: any) => {
        return apiClient<{ access_token: string; token_type: string }>("/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams({
                username: credentials.email,
                password: credentials.password,
            }).toString(),
        });
    },

    logout: async () => {
        return apiClient("/auth/logout", { method: "POST" });
    },

    getMe: async () => {
        return apiClient<User>("/auth/me", { silent: true });
    },

    register: async (data: any) => {
        return apiClient<User>("/auth/register", { method: "POST", body: JSON.stringify(data) });
    },

    deleteUser: async (userId: string) => {
        return apiClient(`/auth/users/${userId}`, { method: "DELETE" });
    }
};
