
"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { authService } from "@/lib/services/auth";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

export function useAuth() {
    const queryClient = useQueryClient();
    const router = useRouter();

    const { data: user, isLoading, error } = useQuery({
        queryKey: ["auth", "user"],
        queryFn: authService.getMe,
        retry: false,
        staleTime: Infinity, // User data doesn't change often
    });

    const loginMutation = useMutation({
        mutationFn: authService.login,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["auth", "user"] });
            toast.success("Welcome back!");
            router.push("/dashboard");
        },
        onError: (error: any) => {
            // Error is handled by apiClient toast mostly, but can do more here
        }
    });

    const logoutMutation = useMutation({
        mutationFn: authService.logout,
        onSuccess: () => {
            queryClient.setQueryData(["auth", "user"], null);
            queryClient.clear(); // Clear all data
            router.push("/login");
            toast.success("Logged out successfully");
        },
    });

    return {
        user,
        isLoading,
        isAuthenticated: !!user,
        login: loginMutation.mutate,
        isLoggingIn: loginMutation.isPending,
        logout: logoutMutation.mutate,
    };
}
