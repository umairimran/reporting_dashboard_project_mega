"use client";

import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
} from "react";
import { User, UserRole, Client } from "@/types/dashboard";
import { mockUsers, mockClients } from "@/lib/mock-data";

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isAdmin: boolean;
  currentClient: Client | null;
  simulatedClient: Client | null;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  simulateAsClient: (client: Client | null) => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [simulatedClient, setSimulatedClient] = useState<Client | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load user from localStorage on mount
  useEffect(() => {
    try {
      const storedUser = localStorage.getItem("auth_user");
      const storedSimulatedClient = localStorage.getItem("simulated_client");

      if (storedUser) {
        setUser(JSON.parse(storedUser));
      }
      if (storedSimulatedClient) {
        setSimulatedClient(JSON.parse(storedSimulatedClient));
      }
    } catch (error) {
      console.error("Error loading auth state:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const isAuthenticated = !!user;
  const isAdmin = user?.role === "admin";

  // Get the current client (either simulated for admin, or the user's own client)
  const currentClient =
    simulatedClient ||
    (user?.role === "client"
      ? mockClients.find((c) => c.userId === user.id) || null
      : null);

  const login = useCallback(
    async (email: string, password: string): Promise<boolean> => {
      // Mock authentication - in production, this would hit an API
      const foundUser = mockUsers.find(
        (u) => u.email.toLowerCase() === email.toLowerCase()
      );

      if (foundUser && foundUser.isActive) {
        // Simulate network delay
        await new Promise((resolve) => setTimeout(resolve, 500));
        setUser(foundUser);

        // Persist to localStorage
        try {
          localStorage.setItem("auth_user", JSON.stringify(foundUser));
        } catch (error) {
          console.error("Error saving auth state:", error);
        }

        return true;
      }

      return false;
    },
    []
  );

  const logout = useCallback(() => {
    setUser(null);
    setSimulatedClient(null);

    // Clear localStorage
    try {
      localStorage.removeItem("auth_user");
      localStorage.removeItem("simulated_client");
    } catch (error) {
      console.error("Error clearing auth state:", error);
    }
  }, []);

  const simulateAsClient = useCallback(
    (client: Client | null) => {
      if (isAdmin) {
        setSimulatedClient(client);

        // Persist to localStorage
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
        user,
        isAuthenticated,
        isAdmin,
        currentClient,
        simulatedClient,
        login,
        logout,
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
