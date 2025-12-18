"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { isAdmin, simulatedClient, isLoading } = useAuth();

  useEffect(() => {
    if (isLoading) return;

    // Redirect if not admin OR if admin is in simulation mode
    if (!isAdmin || simulatedClient) {
      router.push("/dashboard");
    }
  }, [isAdmin, simulatedClient, isLoading, router]);

  // Show loading state while checking auth
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-600"></div>
      </div>
    );
  }

  // Don't render admin content if not authorized
  if (!isAdmin || simulatedClient) {
    return null;
  }

  return <>{children}</>;
}
