"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { isAdmin, isLoading, isAuthenticated } = useAuth();

  useEffect(() => {
    if (isLoading) return;

    // Redirect if not authenticated
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }

    // Redirect if not admin
    if (!isAdmin) {
      toast.error("Access Denied", {
        description: "You don't have permission to access this page.",
      });
      router.push("/dashboard");
    }
  }, [isAdmin, isLoading, isAuthenticated, router]);

  // Show loading state while checking auth
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Don't render admin content if not authorized
  if (!isAdmin) {
    return null;
  }

  return <>{children}</>;
}
