"use client";

import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
} from "react";
import { User as AuthUser } from "@/types/auth"; // We will create this or use equivalent
import { Client } from "@/types/dashboard"; // Keep existing types
import { authService } from "@/lib/services/auth";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { clientsService } from "@/lib/services/clients";

// Adapt User type if necessary to match Dashboard's expectation
interface User extends AuthUser { }

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isAdmin: boolean;
  currentClient: Client | null;
  simulatedClient: Client | null;
  login: (credentials: any) => Promise<void>;
  logout: () => void;
  simulateAsClient: (client: Client | null) => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [simulatedClient, setSimulatedClient] = useState<Client | null>(null);
  const queryClient = useQueryClient();
  const router = useRouter();

  // Fetch current user
  const { data: user, isLoading } = useQuery({
    queryKey: ["auth", "user"],
    queryFn: async () => {
      try {
        return await authService.getMe();
      } catch (e) {
        return null;
      }
    },
    retry: false,
    staleTime: Infinity,
  });

  // Load simulated client from local storage
  useEffect(() => {
    try {
      const storedSimulatedClient = localStorage.getItem("simulated_client");
      if (storedSimulatedClient) {
        setSimulatedClient(JSON.parse(storedSimulatedClient));
      }
    } catch (error) {
      console.error("Error loading auth state:", error);
    }
  }, []);

  // Fetch client for the logged-in user (if not admin)
  const { data: userClient } = useQuery({
    queryKey: ["auth", "client", user?.id],
    queryFn: async () => {
      if (!user || user.role === "admin") return null;
      // Fetch all clients and find the one belonging to this user
      // efficient enough for now until we have a dedicated endpoint
      const response = await clientsService.getClients(0, 1000);
      const myClient = response.clients.find((c) => c.userId === user.id);
      return myClient || null;
    },
    enabled: !!user && user.role === "client",
    staleTime: Infinity,
  });

  // Sync logout and login across tabs
  useEffect(() => {
    const handleStorageChange = (event: StorageEvent) => {
      if (event.key === "logout-event") {
        queryClient.setQueryData(["auth", "user"], null);
        queryClient.clear();
        setSimulatedClient(null);
        router.push("/login");
        toast.info("Logged out from another tab");
      } else if (event.key === "login-event") {
        // Invalidate query to fetch new user data
        queryClient.invalidateQueries({ queryKey: ["auth", "user"] });
        // The LoginPage will auto-redirect due to isAuthenticated becoming true
      }
    };

    window.addEventListener("storage", handleStorageChange);
    return () => window.removeEventListener("storage", handleStorageChange);
  }, [queryClient, router]);

  const loginMutation = useMutation({
    mutationFn: authService.login,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["auth", "user"] });

      // Signal other tabs to update auth state
      localStorage.setItem("login-event", Date.now().toString());

      toast.success("Welcome back!");
      router.push("/dashboard");
    },
    onError: (error: any) => {
      // toast.error("Login failed"); // Handled by apiClient
    }
  });

  const logoutMutation = useMutation({
    mutationFn: authService.logout,
    onSuccess: () => {
      queryClient.setQueryData(["auth", "user"], null);
      queryClient.clear();
      localStorage.removeItem("simulated_client");

      // Signal other tabs to logout
      localStorage.setItem("logout-event", Date.now().toString());

      setSimulatedClient(null);
      router.push("/login");
      toast.success("Logged out successfully");
    },
  });

  const isAuthenticated = !!user;
  const isAdmin = user?.role === "admin";

  // Get the current client (either simulated for admin, or the user's mapped client)
  const currentClient = simulatedClient || userClient || null;

  const simulateAsClient = useCallback(
    (client: Client | null) => {
      if (isAdmin) {
        setSimulatedClient(client);
        try {
          if (client) {
            localStorage.setItem("simulated_client", JSON.stringify(client));
          } else {
            localStorage.removeItem("simulated_client");
          }
        } catch (error) {
          console.error("Error saving simulated client:", error);
        }
      }
    },
    [isAdmin]
  );

  return (
    <AuthContext.Provider
      value={{
        user: user as User | null,
        isAuthenticated,
        isAdmin,
        currentClient,
        simulatedClient,
        login: async (creds) => { await loginMutation.mutateAsync(creds); },
        logout: logoutMutation.mutate,
        simulateAsClient,
        isLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

